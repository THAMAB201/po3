# Canonical Definitions

These definitions are binding unless the user explicitly replaces them later.

## FPI — First Presented Imbalance

A directional three-candle imbalance used as controller/context.

- The first valid FPI after a session start becomes the Session FPI.
- The first valid FPI inside the session’s first Macro becomes the first Macro FPI.
- The first valid FPI inside a 30-minute interval becomes local interval context.
- FPI is not a raw limit entry.
- Disrespect requires a completed candle-body close through the controlling edge; wick penetration is not disrespect.

## Session FPI

The global objective for the active session campaign.

- Bullish Session FPI: Session-direction trades are buys; sells are Judas.
- Bearish Session FPI: Session-direction trades are sells; buys are Judas.
- Reinitialized at 09:30, 11:30, and 13:30 using the first valid post-start FPI.

## First Macro FPI

The first valid FPI in the first Macro window of the controller session.

- AM default: 09:50–10:10.
- Lunch default: 11:50–12:10.
- PM default: 13:50–14:10.

It is a separate object from Session FPI and local interval FPI.

## Regular OB

An order block is the opposing candle or consecutive opposing candle-body series immediately preceding displacement.

- It starts the run.
- It must be sourced from the active 30-minute window.
- The true extreme valid foundation is selected: lowest bullish or highest bearish.
- A random isolated candle is not automatically an OB.

## Candle-series OB

A group of consecutive opposing candle bodies treated as one foundation.

- Prefer the complete valid series over a single isolated candle when both represent the same displacement.
- The series boundary is based on candle bodies, not the furthest wick.
- Wick penetration does not automatically invalidate the series.

## BOLO OB

A body-valid order block that allows wick penetration.

### Bullish

- Wick below the bullish foundation is allowed.
- A body close below the governing body boundary invalidates it.

### Bearish

- Wick above the bearish foundation is allowed.
- A body close above the governing body boundary invalidates it.

The user’s examples often require the valid series BOLO rather than the lowest/highest isolated candle.

## IMB — Imbalance

A supporting imbalance that confirms delivery after the foundation.

Required causal order:

```text
OB/BOLO foundation
→ displacement confirms foundation
→ same displacement or later forms aligned IMB
→ IMB binds to that exact foundation
→ later retest
→ directional close
→ entry
```

An old IMB from another window cannot be attached to a new foundation.

### IMB disrespect

- Bullish IMB: completed body close below bottom.
- Bearish IMB: completed body close above top.

Once disrespected, the IMB is permanently invalid. It cannot later be respected.

## BPR

BPR is allowed only where already defined by the canonical architecture/framework. Do not invent a BPR rule in the strategy. It must obey the same source-window, causal-foundation, retest, and invalidation discipline as other supports.

## BGOB

Use the framework/library definition supplied by the user. Do not create synthetic BGOB types or names.

Known requirements:

```text
valid BGOB zone
→ body close beyond
→ later retest
→ directional close back outside
→ entry
```

- Bullish BGOB stop: BGOB low.
- Bearish BGOB stop: BGOB high.
- Entry may be rejected after excessive body penetration, normally configured at 50%.
- First-Macro BGOB may persist across local windows.
- “BGOB seed” may be an internal implementation state but must not be shown as a made-up user strategy definition.

## Judas

Judas is a temporary move/trade opposite the active Session FPI.

- Bullish Session FPI → Judas sell.
- Bearish Session FPI → Judas buy.

Judas is determined by direction relative to Session FPI, not by the name of a phase variable.

## Judas end

A transition event when a later valid Session-direction sequence ends the Judas campaign.

Example:

```text
Session FPI = bearish
active Judas side = buy
later valid sell sequence appears
new trade class = SESSION_DELIVERY_SELL
transition event = JUDAS_END
```

The new sell is not a Judas sell and must not be labeled `JUDAS-END-SELL` as its trade class.

## Session delivery

A trade in the active Session FPI direction.

- Bullish Session FPI → delivery buy.
- Bearish Session FPI → delivery sell.

Delivery may be initial continuation or recovery after Judas, but its class remains Session direction.

## Recovery

A Session-direction sequence that forms after price temporarily moved against or disrespected the Session FPI.

Recovery still requires a valid current-window foundation plus support. A local FPI is contextual and may not deadlock the structural sequence.

## MMBM / delivery leg

A validated directional leg held while successive interval FPIs, OBs, IMBs, or BGOBs remain respected.

- Additional same-direction confirmation validates holding.
- It does not pyramid another position.
- Opposing structures do not reverse the position unless the full reversal state completes.

## ORB safeguard

Opening range breakout safeguard, normally based on 09:30–09:45.

- Optional toggle.
- Hidden/no range highlight by default.
- Used only as an additional safeguard for a tactical opposite trade after controlling FPI disrespect.
- Does not replace structural confirmation.

## Respect

A retest followed by the required directional close while the structure has never been permanently invalidated.

## Disrespect

A completed body close beyond a structure’s invalidation boundary. Wick-only penetration is not disrespect unless a specific rule explicitly says otherwise.

## Retest

A later physical overlap after formation/break/confirmation. The same formation candle cannot be counted as its own later retest.

## Extreme selection

- Bullish intended direction: lowest valid foundation/support in the active interval.
- Bearish intended direction: highest valid foundation/support in the active interval.
- Selection must preserve causal provenance and series validity; price extremity alone is insufficient.

## Authority versus evidence

- Evidence: a structure exists and advances through its lifecycle.
- Authority: the current narrative permits that direction to trade.

Evidence must be recorded even before authority permits execution. This distinction is essential to avoid missed later-window recoveries.
