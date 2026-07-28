# Canonical PO3 MMXM Strategy Logic

This document consolidates the latest explicit user rules. When older documents conflict with this file, the latest rule stated here wins. Missing details must be surfaced; they must not be invented.

## 1. Operating domain

- Execution chart: one minute.
- Timezone: `America/New_York`.
- Primary instruments: NQ/MNQ; logic should also work on stocks when session-boundary gap filtering is enabled.
- Allowed concepts only: FPI, first Macro FPI, exact 30-minute FPI, regular OB, candle-series OB, BOLO OB, IMB, BPR where already defined, BGOB, Judas state, ORB safeguard, completed one-minute closes, retests, respect, invalidation, and PO3/MMXM delivery.
- Disallowed: EMA, VWAP, RSI, moving-average filters, generic trend filters, or any structure not explicitly defined by the user/library.

## 2. Three session controllers

Each session begins a new controller campaign and must use the same first-FPI logic.

| Session | Start | End | Controller |
|---|---:|---:|---|
| NY AM | 09:30 | 11:30 | First valid FPI after 09:30 |
| NY Lunch | 11:30 | 13:30 | First valid FPI after 11:30 |
| NY PM | 13:30 | 17:00 | First valid FPI after 13:30 |
| Forced flat | 16:49 close / flat by 16:50 | — | Hard risk authority |

For stocks/RTH, an overnight gap crossing the session start must not be mistaken for the session FPI. The first qualifying FPI must be formed after the editable session start, normally 09:31 or later for the AM stock session.

## 3. Session FPI

The first valid FPI after a session start establishes the session’s global delivery objective.

- Bullish Session FPI: overall session objective is bullish delivery.
- Bearish Session FPI: overall session objective is bearish delivery.
- FPI is context and authority, not a raw entry.
- A wick through an FPI does not disrespect it.
- Disrespect requires a completed one-minute candle body close through the controlling far edge.
- Local movement may oppose the Session FPI as Judas or pullback activity.
- A later Session-direction setup may restore delivery without requiring every local 30-minute FPI to align first.

### Trade classification from Session FPI

This rule overrides phase-label shortcuts.

```text
selected direction == Session FPI direction
    => Session delivery, continuation, or recovery

selected direction == opposite Session FPI direction
    => Judas trade
```

A same-direction sell under a bearish Session FPI is never a Judas sell. A same-direction buy under a bullish Session FPI is never a Judas buy.

`JUDAS_END` is a campaign transition event only. It must not be used as the entry’s trade class.

## 4. First Macro FPI

Each controller session has a first Macro window, normally 20 minutes after the session starts and lasting 20 minutes:

- AM: 09:50–10:10;
- Lunch: 11:50–12:10;
- PM: 13:50–14:10.

The first valid FPI inside that Macro window is tracked separately from the Session FPI.

Macro FPI roles:

- support or test the Session objective;
- provide tactical opposite authority after formal disrespect;
- provide persistent Macro structures/BGOBs across local 30-minute boundaries;
- influence holding and reversal decisions;
- never flip bias from a wick alone;
- never create an entry without a completed structure sequence.

## 5. Exact 30-minute windows

Every session is divided into exact 30-minute windows. Examples:

- 09:30–10:00;
- 10:00–10:30;
- 10:30–11:00;
- 11:00–11:30;
- 11:30–12:00;
- continuing through the PM session.

At each new window:

1. Preserve the active Session FPI and first Macro context.
2. Reset only failed or unused local-window structure candidates.
3. Search independently for both Session-direction and tactical/Judas-direction evidence.
4. Do not combine an old-window BOLO with a new-window IMB, or vice versa.
5. If no complete valid sequence forms, wait. The next window starts a clean search.
6. A current-window FPI may reinforce, oppose, or be disrespected toward Session direction, but absence of a local FPI cannot erase a completed Session-direction OB/BOLO + IMB sequence.

## 6. Structure hierarchy

The strategy uses a hierarchy. Drawings do not vote equally.

1. Hard risk authority.
2. Active Session FPI/controller.
3. First Macro FPI and Macro range.
4. Current 30-minute narrative.
5. Governing OB/BOLO/BGOB foundation.
6. Supporting IMB/BPR.
7. Retest and completed directional close.
8. Visual label.

A lower layer may not override a higher layer without an explicit transition rule.

## 7. Regular OB and candle-series OB

An order block starts the run.

- Prefer the complete consecutive opposing candle-body series immediately preceding displacement.
- A random isolated candle inside the search range is not automatically an OB.
- For bullish delivery, select the true lowest valid bullish foundation for the active window.
- For bearish delivery, select the true highest valid bearish foundation for the active window.
- Continue searching for the more-extreme valid foundation until the window resolves.
- The displacement confirming the OB may also create the supporting IMB.
- The entry still requires the later IMB retest and directional respect close.

## 8. BOLO OB

BOLO is a body-valid order block with allowed wick penetration.

### Bullish BOLO

- Price may wick below the bullish OB/body-series boundary.
- The candle body must not close below the governing bullish body boundary.
- A body close below invalidates the bullish BOLO.

### Bearish BOLO

- Price may wick above the bearish OB/body-series boundary.
- The candle body must not close above the governing bearish body boundary.
- A body close above invalidates the bearish BOLO.

The complete valid candle series has priority over an isolated lowest/highest candle. Wick penetration alone must not cause the series to be discarded.

## 9. IMB lifecycle

An IMB can support an entry only through a causal sequence.

- It must form in the same active 30-minute window as the foundation, unless an explicitly persistent Macro structure is being used.
- It must be directionally aligned with the intended trade, unless an explicitly defined opposing-IMB reclaim rule applies.
- It must form from the OB/BOLO confirming displacement or later.
- It must be bound to that exact foundation.
- Entry requires a later physical retest and directional body close through the correct edge.

### Permanent invalidation

Once an IMB is body-close disrespected, it cannot later become respected.

- Bullish IMB: body close below its bottom permanently invalidates it.
- Bearish IMB: body close above its top permanently invalidates it.

After permanent invalidation, the IMB cannot be rebound, reclaimed later, reused by another foundation, or shared by recovery and Judas engines. A new IMB is required.

## 10. BGOB

Do not invent labels such as “30m BGOB seed” as strategy concepts. Use the user’s existing BGOB definition/library.

Known required lifecycle:

1. BGOB zone exists from a valid framework-defined structure.
2. Price body-closes beyond it in the intended direction.
3. A later candle physically retests it.
4. Price closes directionally back outside it.
5. Excessive body penetration, normally beyond the configured 50% rule, rejects the entry.

- Bullish BGOB trade: structural stop belongs at the bullish BGOB low.
- Bearish BGOB trade: mirrored at the BGOB high.
- A first-Macro BGOB may persist across later local windows.
- The exact BGOB detector must come from the existing Market Model/framework logic; do not synthesize a new definition from generic FVG logic.

## 11. Session-direction entry sequence

For a bullish Session FPI:

```text
search each window for the lowest valid bullish regular OB / series BOLO
→ confirm displacement while the body foundation remains valid
→ bind the bullish IMB created by that displacement or later
→ wait for a later IMB retest
→ require a bullish close through the correct edge
→ buy immediately
```

Bearish is mirrored using the highest valid bearish foundation and bearish IMB.

A valid Session-direction structure can build even when:

- the current 30-minute window has no first FPI;
- the current-window FPI remains temporarily opposing;
- a prior Judas phase is still active.

Once a complete Session-direction foundation begins rebuilding, stale Judas authority must not steal that interval.

## 12. Judas sequence

Judas is the temporary movement opposite the active Session FPI.

- Bullish Session FPI → Judas side is sell.
- Bearish Session FPI → Judas side is buy.

A Judas trade is not released by FPI disrespect alone. It requires its own fresh structure.

Typical tactical release:

```text
Session FPI body-close disrespected
+ first Macro FPI body-close disrespected in the same tactical direction
+ optional ORB safeguard when enabled
+ fresh current-window opposite-direction OB/BOLO + aligned IMB
  or a fully confirmed framework-defined BGOB
+ later retest and directional close
→ Judas entry
```

A Judas position ignores incomplete same-window reversal noise. It holds until a later 30-minute window forms a complete Session-direction reversal/delivery sequence, or until the hard maximum stop/forced-flat rule applies.

## 13. ORB safeguard

- ORB range: 09:30–09:45 for the AM controller, with session-relative equivalents only if explicitly configured.
- Toggle must be available.
- ORB should not be highlighted by default.
- ORB is a safeguard for an opposite trade after Session FPI and first Macro FPI disrespect.
- It does not replace OB/BOLO/IMB/BGOB confirmation.
- Entry waits for a completed body close outside the relevant ORB boundary.

## 14. Narrative arbitration

Detection must run independently for both directions. Authority decides only after evidence exists.

Per-window states:

```text
SEARCH
BUILD_SESSION
BUILD_JUDAS
LOCK_SESSION
LOCK_JUDAS
RESOLVED
INVALID
```

- A confirmed foundation alone may begin a build but may not enter without the supporting IMB/BGOB completion.
- Once one side has the complete causal sequence, it wins the window.
- The opposite side cannot steal the window unless the locked foundation is body-close invalidated.
- Stale authority from a previous window cannot override a newly completed current-window sequence.

## 15. Holding and exits

- Hard maximum/disaster stop remains active intrabar.
- Structural invalidation is based on completed body closes, not wicks.
- When interval-close hold is enabled, temporary intrainterval structural failure is observed but not immediately exited; the final one-minute close of the 30-minute interval decides whether the trade remains valid.
- Judas holds until a valid later-window Session-direction reversal, hard stop, or forced flat.
- Delivery holds while the governing foundation and confirmed supports remain respected.
- BGOB structural stops use the BGOB low/high.
- OB/BOLO structural stops use the governing foundation invalidation.
- Fixed 150-point target is optional; delivery must not be forced out merely because a generic target was enabled unintentionally.
- No pyramiding or duplicate entries while a position is active.
- A later same-direction confirmation validates the hold; it does not add another position.

## 16. Visual and naming rules

- Master `Show All Drawings` toggle: off by default.
- Drawings may be hidden without changing trade logic.
- Do not display opposite-direction OBs as active authority unless a real reversal condition exists.
- Do not invent user-facing structure names.
- Entry labels must reflect actual classification:
  - `SESSION-DELIVERY-BUY` / `SESSION-DELIVERY-SELL`;
  - `SESSION-RECOVERY-BUY` / `SESSION-RECOVERY-SELL`;
  - `JUDAS-BUY` / `JUDAS-SELL` only when opposite Session FPI;
  - `BGOB-BUY` / `BGOB-SELL` with Session/Judas class stored separately.
- `JUDAS_END` belongs in a transition/debug field, not as the trade class.

## 17. Safe default

When information is missing, contradictory, stale, cross-window, already invalidated, or not fully confirmed, the action is `WAIT` / `NO_TRADE`. The strategy must never manufacture an entry to avoid inactivity.
