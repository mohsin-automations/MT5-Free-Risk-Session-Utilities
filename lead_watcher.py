#!/usr/bin/env python3
"""
Lightweight 24/7 RSS Lead Watcher for Reddit & BabyPips.
Monitors public RSS feeds for high-intent MT4/MT5/MQL4/MQL5/Pine Script keywords,
deduplicates via seen_leads.json, and notifies via GitHub Issues (zero extra setup)
and optional Telegram Bot webhook.
"""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    ("Reddit r/algotrading", "https://www.reddit.com/r/algotrading/new/.rss"),
    ("Reddit r/Forex", "https://www.reddit.com/r/Forex/new/.rss"),
    ("Reddit r/TradingView", "https://www.reddit.com/r/TradingView/new/.rss"),
    ("BabyPips EAs", "https://forums.babypips.com/c/trading-systems/expert-advisors-and-automated-trading/30.rss"),
]

KEYWORDS = [
    "mt5 ea",
    "mt4 ea",
    "mql5",
    "mql4",
    "pine script",
    "pinescript",
    "error 4756",
    "metaeditor",
    "expert advisor",
    "convert to mt5",
    "convert to mt4",
    "fix my ea",
    "strategy tester",
    "invalid stops",
]

SEEN_FILE = "seen_leads.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    # Keep latest 500 IDs so the file stays tiny
    trimmed = sorted(seen)[-500:]
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)


def fetch_feed(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AlgoEdgeLeadWatcher/1.0 (+https://github.com)"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_entries(xml_bytes):
    root = ET.fromstring(xml_bytes)
    entries = []
    # Atom (Reddit)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", "", ns) or "").strip()
        link_el = entry.find("atom:link", ns)
        link = link_el.attrib.get("href", "") if link_el is not None else ""
        summary = (entry.findtext("atom:content", "", ns) or "").strip()
        entry_id = (entry.findtext("atom:id", "", ns) or link).strip()
        entries.append((entry_id, title, link, summary))
    # RSS 2.0 (BabyPips / Discourse)
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        summary = (item.findtext("description") or "").strip()
        entry_id = (item.findtext("guid") or link).strip()
        entries.append((entry_id, title, link, summary))
    return entries


def notify_telegram(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "disable_web_page_preview": False}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as exc:
        print(f"Telegram notify failed: {exc}")


def create_github_issue(title, body):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return
    url = f"https://api.github.com/repos/{repo}/issues"
    payload = json.dumps({"title": title[:200], "body": body, "labels": ["lead"]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "AlgoEdgeLeadWatcher/1.0",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as exc:
        print(f"GitHub issue creation failed: {exc}")


def main():
    seen = load_seen()
    new_matches = []

    for source_name, feed_url in FEEDS:
        try:
            raw = fetch_feed(feed_url)
            entries = parse_entries(raw)
        except Exception as exc:
            print(f"Failed to fetch {source_name}: {exc}")
            continue

        for entry_id, title, link, summary in entries:
            if not entry_id or entry_id in seen:
                continue
            haystack = f"{title} {summary}".lower()
            matched_kw = [kw for kw in KEYWORDS if kw in haystack]
            if matched_kw:
                seen.add(entry_id)
                new_matches.append((source_name, title, link, matched_kw))

    if new_matches:
        save_seen(seen)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        for source_name, title, link, matched_kw in new_matches[:5]:
            kw_str = ", ".join(matched_kw)
            msg = (
                f"Live Lead [{source_name}]\n"
                f"Title: {title}\n"
                f"Matched: {kw_str}\n"
                f"Link: {link}\n"
                f"Time: {ts}\n\n"
                f"Tip: Reply manually with a quick diagnostic + subtle mention of your MT4/MT5 work."
            )
            print(msg)
            notify_telegram(msg)
            create_github_issue(f"[Lead] {source_name}: {title}", msg)
    else:
        print("No new matching leads found.")


if __name__ == "__main__":
    main()
