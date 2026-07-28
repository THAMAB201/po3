# Acceptance Tests

Every code revision must compile and pass these replay tests before it replaces the prior baseline. Use one-minute data, the same symbol/contract, the same date range, and unchanged strategy properties.

## Test protocol

For every test record:

- Session FPI direction/top/bottom;
- first Macro FPI direction/top/bottom;
- active 30-minute window;
- foundation source bar/time/window;
- support source bar/time/window;
- foundation status;
- support status;
- approved direction;
- trade class;
- transition event;
- rule ID;
- entry/exit time and price;
- stop/target;
- result in points;
- reason for every blocked entry.

A screenshot label alone is not evidence that the state is correct.

## AT-001 — Bearish Session FPI classification

**Scenario:** Latest screenshot supplied on 2026-07-27. Session FPI is bearish and price sells in the same direction.

Expected:

```text
selected direction = SELL
Session direction  = SELL
trade class        = SESSION_DELIVERY or SESSION_RECOVERY
Judas              = false
```

Forbidden:

- `JUDAS-SELL` as trade class;
- `JUDAS-END-SELL` as entry classification;
- `tradeIsJudas = true`.

Allowed diagnostic metadata:

- `transitionEvent = JUDAS_END` only when an opposite-direction Judas campaign was actually active before the sell.

## AT-002 — Bullish Session FPI mirror classification

Bullish Session FPI plus buy:

```text
trade class = SESSION_DELIVERY/RECOVERY
Judas = false
```

Bullish Session FPI plus sell:

```text
trade class = JUDAS
```

## AT-003 — Third-window recovery after two failed windows

**Scenario:** Bullish Session FPI. First two 30-minute windows fail to produce a valid bullish OB/BOLO + aligned IMB. Third window forms the user-marked BOLO, confirms displacement, creates/binds a bullish IMB, then retests and closes above.

Expected:

- no buy in the first two windows;
- local failed candidates expire;
- Session FPI remains bullish;
- third-window BOLO/OB and IMB use the same window provenance;
- immediate buy on the later IMB confirmation close;
- trade class `SESSION_RECOVERY_BUY`;
- no local-FPI prerequisite deadlock.

## AT-004 — No unsupported early buy

**Scenario:** A window contains price weakness but no confirmed OB/BOLO and no valid aligned IMB.

Expected: `WAIT` / no entry.

A later valid window may enter, but no stale structure can be carried forward and combined.

## AT-005 — IMB permanent invalidation

Bullish IMB receives a completed body close below its bottom.

Expected:

- original IMB becomes permanently invalid;
- every copied/bound version becomes invalid;
- it cannot later retest, respect, reclaim, or trigger;
- a new bullish IMB is required.

Bearish mirror must also pass.

## AT-006 — Series BOLO priority

**Scenario:** User-marked consecutive BOLO body series exists; price wicks through the low/high but does not body-close beyond the valid series boundary. An isolated more-extreme candle also exists.

Expected:

- valid series BOLO remains selected;
- wick penetration does not invalidate it;
- isolated candle does not replace the valid series solely because of wick extremity;
- body-close invalidation is mirrored correctly.

## AT-007 — Session + first Macro tactical break

**Scenario:** Bullish Session FPI and bullish/controlling Macro context receive completed body closes below both controlling zones.

Expected:

- tactical bearish/Judas search may be released;
- no automatic sell from the break alone;
- sell requires fresh current-window bearish OB/BOLO + bearish IMB retest/respect or a complete framework BGOB;
- trade class is `JUDAS_SELL` because direction opposes bullish Session FPI.

Bearish Session FPI mirror: tactical side is buy.

## AT-008 — Stale Judas cancellation

After a tactical break is latched, a valid Session-direction foundation confirms in a later window.

Expected:

- detection records the Session-direction foundation regardless of local FPI;
- stale Judas authority is suspended/cancelled before it can steal the interval;
- completed Session-direction IMB sequence wins the window;
- a fresh tactical break is needed after that foundation later fails.

## AT-009 — Judas hold until later-window reversal

**Scenario:** Valid Judas trade enters opposite Session FPI.

Expected:

- same-window opposing noise does not close/reverse it;
- later-window complete Session-direction foundation + support sequence exits/reverses it;
- hard maximum stop and force-flat remain active;
- `JUDAS_END` is recorded as transition metadata, while the new trade class is Session delivery.

## AT-010 — 30-minute interval-close hold

A delivery trade temporarily body-closes beyond structural invalidation mid-window, then recovers before the final one-minute close.

Expected when interval deferral is enabled:

- no immediate structural exit;
- hard disaster stop remains active;
- final one-minute close of the 30-minute window determines hold/exit.

If final close remains invalid, exit reason must identify interval-end structural failure.

## AT-011 — Framework BGOB lifecycle

For bullish and bearish cases:

```text
valid BGOB
→ body close beyond
→ later retest
→ directional close outside
```

Expected:

- entry only after full sequence;
- no same-bar break-and-retest shortcut;
- reject excessive penetration per configured threshold;
- bullish stop at BGOB low, bearish stop at BGOB high;
- campaign class still comes from direction relative to Session FPI.

## AT-012 — First-Macro BGOB persistence

A valid first-Macro BGOB forms near a local-window boundary and confirms later.

Expected:

- Macro BGOB persists across the 10:00/10:30 equivalent boundary;
- local-window reset does not delete it;
- it cannot be mislabeled as a made-up user structure.

## AT-013 — Stock/RTH session-boundary gap

On a stock with overnight gap:

Expected:

- no FPI whose three candles cross the 09:30 start becomes AM Session FPI when gap filtering is enabled;
- first valid post-start FPI, normally 09:31 or later, becomes controller.

## AT-014 — Three controller resets

At 09:30, 11:30, and 13:30:

Expected:

- old controller campaign closes/resets per rules;
- new first post-start FPI becomes the active controller;
- AM direction cannot remain stuck through Lunch/PM without the new controller logic.

## AT-015 — One narrative owns a window

Both bullish and bearish partial evidence appears.

Expected:

- both sides may be detected;
- only a complete causal sequence can lock the window;
- stale authority cannot win over a fresh complete sequence;
- no repeated flip/tilt trades;
- maximum one new entry per window when enabled.

## AT-016 — No cross-window pairing

Foundation from window A and IMB from window B.

Expected: no entry.

Exception: explicitly persistent first-Macro BGOB/registry structures only, with their own provenance rule.

## AT-017 — Same-direction confirmation while holding

Active Session-direction trade receives another valid same-direction structure.

Expected:

- hold is validated;
- no pyramiding;
- no unnecessary exit/re-entry label clutter.

## AT-018 — Drawings toggle independence

`Show All Drawings = false`.

Expected:

- entries/exits and results are identical to drawings on;
- no visual object changes authority or state.

## Regression gate

A patch fails acceptance if any of these occurs:

- a previously correct hallmark trade disappears;
- unsupported trade count increases;
- Session-direction trade is labeled Judas;
- cross-window structures are mixed;
- invalid IMB is reused;
- strategy becomes unprofitable solely because unrelated logic was changed;
- compiler warnings/errors are introduced.
