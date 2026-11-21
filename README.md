# MT5 Free Risk, Session & Execution Utilities (MQL5 / MQL4)

Clean, lightweight, zero-bloat **MetaTrader 5 (MQL5)** utilities built for XAUUSD (Gold) and Forex traders who need reliable execution, spread-aware stop-loss placement, session filtering, and Strategy Tester fixes.

> **Need a custom MT4/MT5 Expert Advisor, TradingView Pine Script conversion, or an urgent bug fix (Error 4756, invalid stops, backtest mismatch, AI-generated code rescue)?**
> Hire me directly on Fiverr (5.0★ verified reviews, fast turnaround):
> **[Fix MQL4/MQL5 Errors & Debug MetaEditor EA](https://www.fiverr.com/mosinraza/fix-mql4-mql5-errors-and-debug-metaeditor-expert-advisor-ea)** | **[Full Fiverr Profile](https://www.fiverr.com/mosinraza)**

---

## Included Open-Source MQL5 Utilities

| Utility | Problem Solved | Key Features |
| :--- | :--- | :--- |
| **Manual Entry + Spread SL + 50% ADR TP EA** | Eliminates manual SL/TP math on Gold & FX breakouts | Standby price trigger, `Spread + 1 Tick` SL placement, automatic 50% ADR(20) take-profit |
| **Error 4756 & Filling-Mode Safe Order Wrapper** | Fixes `TRADE_RETCODE_INVALID_FILL` / `Error 4756` across brokers | Auto-detects `ORDER_FILLING_FOK`, `IOC`, or `RETURN` + normalizes lot step & stop level |
| **NY / London Session Time-Window Filter** | Prevents low-liquidity Asia/rollover whipsaws | Clean server-time window guard with automatic pending-order expiry |

---

## Quick Troubleshooting: Common MT5 Errors Fixed

1. **Error 4756 (`TRADE_RETCODE_INVALID_FILL` / `Invalid Stops`):** Usually caused by hardcoding `ORDER_FILLING_FOK` on an ECN broker that requires `IOC`, or placing SL/TP inside `SYMBOL_TRADE_STOPS_LEVEL`.
2. **Backtest Works on Demo, Fails on Live:** Commonly caused by unnormalized lot sizes (`SYMBOL_VOLUME_STEP`), floating spread spikes on XAUUSD, or missing tick-value conversion.
3. **TradingView Pine Script to MT5 MQL5 Conversion:** Rewriting Pine v5/v6 indicators or strategies into native non-repainting MQL5 EAs with clean risk % sizing and session filters.

---

## Need Custom Automation?

* **Debug / Fix Existing MT4 or MT5 EA:** [Order on Fiverr](https://www.fiverr.com/mosinraza/fix-mql4-mql5-errors-and-debug-metaeditor-expert-advisor-ea)
* **Convert Pine Script to MT4/MT5 EA or Rescue AI Code:** [View Fiverr Profile](https://www.fiverr.com/mosinraza)
* **Maintained by:** Mohsin Raza (AlgoEdge Systems)
