# Prompt for the Next AI / New Chat

Copy everything below into the next AI and provide the repository branch.

---

You are continuing the PO3 MMXM Enigma TradingView Pine v6 strategy for SunovaBeach.

## Required sources

Read every file in:

`handoff/PO3_MMXM_2026-07-27/`

Current experimental source:

`enigma/PO3_MMXM_Enigma_Strategy_V9_5_1_Session_Recovery_Decoupled.pine`

Repository/branch:

- `THAMAB201/po3`
- `enigma-v9-3-window-narrative`

Current TradingView header: `PO3E951R`.

Do not begin by rewriting the strategy. First restate the Session FPI classification, 30-minute state model, OB/BOLO → IMB causal sequence, BGOB lifecycle, and holding rules.

## Primary immediate defect

The latest screenshot has a **bearish Session FPI**, but the same-direction sell is labeled `JUDAS-END-SELL`.

That is incorrect classification.

Canonical classification:

```text
selected direction == active Session FPI direction
    => SESSION_DELIVERY / SESSION_RECOVERY

selected direction == opposite active Session FPI direction
    => JUDAS
```

`JUDAS_END` is only a transition event. It must never make a bearish-FPI sell a Judas trade.

Correct these fields separately:

```text
tradeClass
transitionEvent
entryFamily
entryRule
```

Also set `tradeIsJudas` from selected direction relative to Session FPI, not from `phase` or signal-source name.

## Non-negotiable strategy rules

1. One-minute execution only.
2. Three controller sessions: 09:30, 11:30, 13:30 New York.
3. First valid FPI after each session start establishes the controller.
4. Stocks/RTH gap crossing the start cannot become Session FPI when filtering is enabled.
5. FPI disrespect requires body close, not wick.
6. Bullish Session FPI: buys are delivery; sells are Judas.
7. Bearish Session FPI: sells are delivery; buys are Judas.
8. Each 30-minute window searches for the lowest bullish or highest bearish valid foundation.
9. Regular OB or BOLO/series must causally precede and bind the supporting IMB.
10. The confirming displacement may create the IMB, but entry waits for a later IMB retest and directional close.
11. No OB-only or IMB-only entry.
12. No cross-window pairing of ordinary foundations/supports.
13. Once an IMB is body-close disrespected, it is permanently invalid.
14. Series BOLO has priority over an isolated candle when the series body remains valid despite wick penetration.
15. BGOB must use the existing user/framework definition: close beyond, later retest, close outside; no made-up user labels.
16. Session + first Macro disrespect may release a Judas search but never an automatic trade.
17. Session-direction structure detection cannot be blocked by missing/opposing local 30-minute FPI.
18. A confirmed Session-direction foundation cancels stale Judas authority before arbitration.
19. Judas holds until a later-window complete Session-direction reversal, hard stop, or forced flat.
20. Interval-close structural holding remains available; hard maximum stop stays active intrabar.
21. Master drawings toggle is off by default and must not affect logic.
22. No EMA, VWAP, RSI, generic trend filters, or invented concepts.
23. Provide the full replacement code after the fix; the user does not want partial edits.

## Engineering constraints

- Preserve the current source as an immutable control.
- Make one narrowly scoped patch.
- Do not delete unrelated entry families to remove a false trade.
- Detection must be independent from authority.
- Every structure stores source bar, source time, source window, direction, status, parent/foundation ID, invalidation, and consumed state.
- Every completed candle should emit an auditable terminal action/reason.
- Add data-window diagnostics before changing behavior.
- Run the full acceptance suite in `05_ACCEPTANCE_TESTS.md`.
- Reject the patch if a previously valid hallmark trade disappears or the locked baseline becomes materially worse.

## First requested task

1. Inspect the current source and identify every place where `phase`, `recoveryRule`, signal name, or candidate source is used to infer Judas classification.
2. Create direction-based `tradeClass` and separate `transitionEvent`.
3. Rename same-direction entries to `SESSION-DELIVERY-*` or `SESSION-RECOVERY-*`.
4. Keep the structural entry behavior unchanged for this first patch.
5. Return the complete corrected Pine file and a concise change report.

Do not claim TradingView compilation until the Pine Editor confirms it.

---
