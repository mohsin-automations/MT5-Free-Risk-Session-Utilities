#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

KEYWORDS = [
    "mt5", "mt4", "mql5", "mql4", "pine script", "pinescript",
    "error 4756", "metaeditor", "expert advisor", "strategy tester",
]
SEEN_FILE = "seen_leads.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen)[-500:], f, indent=2)


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AlgoEdgeLeadWatcher/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_reddit_pullpush():
    out = []
    for sub in ["algotrading", "Forex", "TradingView"]:
        url = f"https://api.pullpush.io/reddit/search/submission/?subreddit={sub}&size=25"
        try:
            data = get_json(url).get("data", [])
            for p in data:
                eid = f"reddit_{p.get('id', '')}"
                title = (p.get("title") or "").strip()
                body = (p.get("selftext") or "").strip()
                link = f"https://www.reddit.com{p.get('permalink', '')}"
                out.append((eid, f"Reddit r/{sub}", title, link, body))
        except Exception as exc:
            print(f"Reddit r/{sub} skip: {exc}")
    return out


def fetch_stackoverflow():
    out = []
    for tag in ["mql5", "mql4", "pine-script"]:
        url = (
            "https://api.stackexchange.com/2.3/questions?"
            + urllib.parse.urlencode({
                "order": "desc",
                "sort": "creation",
                "tagged": tag,
                "site": "stackoverflow",
                "pagesize": 15,
            })
        )
        try:
            items = get_json(url).get("items", [])
            for q in items:
                eid = f"so_{q.get('question_id', '')}"
                title = (q.get("title") or "").strip()
                link = (q.get("link") or "").strip()
                out.append((eid, f"StackOverflow [{tag}]", title, link, tag))
        except Exception as exc:
            print(f"SO {tag} skip: {exc}")
    return out


def create_issue(title, body):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/issues",
        data=json.dumps({"title": title[:200], "body": body}).encode("utf-8"),
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
        print(f"Issue create failed: {exc}")


def main():
    seen = load_seen()
    candidates = fetch_reddit_pullpush() + fetch_stackoverflow()
    matches = []

    for eid, source, title, link, body in candidates:
        if not eid or eid in seen:
            continue
        haystack = f"{title} {body}".lower()
        kws = [k for k in KEYWORDS if k in haystack]
        if kws or source.startswith("StackOverflow"):
            seen.add(eid)
            matches.append((source, title, link, kws or ["tagged"]))

    if matches:
        save_seen(seen)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        for source, title, link, kws in matches[:5]:
            msg = (
                f"**Source:** {source}\n"
                f"**Matched:** {', '.join(kws)}\n"
                f"**Link:** {link}\n"
                f"**Time:** {ts}\n\n"
                f"Reply manually with a quick diagnostic + subtle mention of your MT4/MT5 work."
            )
            create_issue(f"[Lead] {source}: {title}", msg)
        print(f"Logged {min(len(matches), 5)} new leads.")
    else:
        print("No new matching leads found.")


if __name__ == "__main__":
    main()
