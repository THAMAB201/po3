# PO3 MMXM Enigma — Trading Logic Specification

This document is the behavioral source of truth. When code and this document disagree, the code must be corrected.

## 1. Core market concepts

The strategy may use only the intended framework concepts:

- Session FPI
- 30-minute FPI
- 9:50–10:10 Macro FPI
- order blocks (OB)
- imbalances (IMB)
- breaker-GOBs (BGOB)
- Judas/pullback state
- structural respect, disrespect, reclaim, retest, and rejection

Do not add EMA, VWAP, RSI, MACD, generic moving-average filters, or unrelated indicators.

## 2. Session FPI authority

The first valid FPI after 9:30 New York time is the **Session FPI**.

It is the primary directional controller and must persist across later 30-minute phases. It must not be reset merely because the clock enters another phase.

- Bullish Session FPI: actively look for bullish foundations and buys.
- Bearish Session FPI: actively look for bearish foundations and sells.
- A wick through the FPI is not automatic disrespect.
- Disrespect requires the defined candle-body close against the FPI.
- Local opposing FPIs may represent pullback/Judas delivery and do not automatically erase the Session FPI.

The Session FPI can lose authority only through explicit invalidation or a confirmed reversal-state protocol.

## 3. Primary order-block entry

This is the entry missed in the July 19 chart near the session low.

### Bullish sequence

1. Session FPI is bullish.
2. Detect a local bullish OB below price.
3. A bullish OB is the valid down-close candle or consecutive down-close candle group that begins the bullish displacement.
4. The OB confirms when price closes above its upper boundary with valid bullish displacement.
5. Price later physically retests the confirmed OB.
6. Wick penetration is allowed if the candle body does not invalidate the OB. This is the BOLO behavior.
7. The retest candle closes back above the OB upper boundary.
8. Enter **BUY on that close**.

No later IMB is required for this primary entry.

### Bearish sequence

Mirror the bullish sequence:

1. Session FPI is bearish.
2. Detect the local bearish OB above price.
3. The bearish OB confirms when price closes below its lower boundary with valid bearish displacement.
4. Price retests the OB.
5. Wick penetration is allowed if the body does not invalidate the OB.
6. The retest candle closes back below the OB lower boundary.
7. Enter **SELL on that close**.

## 4. Post-OB IMB continuation entry

This is a separate later entry signature, not a requirement for the primary OB entry.

### Bullish continuation

1. Bullish Session FPI remains authoritative.
2. A bullish OB has already confirmed and successfully retested.
3. Track bullish IMBs formed after the relevant OB confirmation/retest sequence.
4. Use the lowest relevant bullish IMB supporting that move.
5. Price physically retests the IMB.
6. The confirming candle closes above the IMB upper boundary.
7. Enter BUY if flat and the supporting OB/IMB foundation remains respected.

### Bearish continuation

Mirror the bullish logic using the highest relevant bearish IMB and a close below its lower boundary.

Do not require a second retest. The first valid later retest and directional close is the signal.

## 5. OB and IMB relationship

An order block and the displacement/imbalance it creates are a causal pair.

- The OB starts the move.
- The IMB communicates the importance and directional force of that OB.
- The system must track which OB created or structurally supports each IMB.
- Old unrelated IMBs must not be attached to a newly confirmed OB.
- A breakout alone may establish narrative context but must not execute a trade without the required retest/confirmation signature.

## 6. BGOB behavior

A valid BGOB requires:

1. close through the original structure;
2. later retest;
3. directional close confirming the breaker behavior.

A BGOB may be an entry foundation or continuation foundation when aligned with the active directional state. It is invalidated by the defined close/penetration rule, including the existing 50% breaker penetration rule where applicable.

## 7. Macro FPI and conflict handling

The original 9:50–10:10 Macro FPI is an important authority layer but must not blindly overwrite the Session FPI.

Possible relationships include:

- Session and Macro aligned: strongest directional permission.
- Session bullish, Macro bearish: treat bearish delivery as possible Judas/pullback until the reversal protocol is actually confirmed.
- Session bearish, Macro bullish: mirrored behavior.
- Macro reclaim or disrespect can upgrade, weaken, or reverse the directional state.

The exact market condition must be represented in the 1,008-case catalog. A catalog conflict may change the action to wait, pullback mode, reduced authority, or reversal mode. It must not make the engine incapable of recognizing a valid structural signature.

## 8. Reversal mode

For the established 30-minute reversal protocol:

- If the 10:00 and 10:30 FPIs both print against the Session FPI and price remains closed against the Session FPI, reversal mode may activate.
- In reversal mode, trade only the confirmed reversal direction from qualified 30-minute foundations.
- Re-alignment occurs when a later 30-minute FPI re-establishes the original Session direction or an explicit new session HH/LL breakout and structural confirmation restores authority.

Do not switch direction from one opposing wick or one unconfirmed local imbalance.

## 9. All 1,008 catalog possibilities

The catalog is not merely an audit label. Every one of the 1,008 valid combinations must resolve to a defined state and action policy.

Each case must output at least:

- approved directional bias: bullish, bearish, neutral, or transitional;
- state: trend, pullback/Judas, reversal candidate, confirmed reversal, or no-trade;
- allowed entry families: OB retest, post-OB IMB retest, BGOB, prior-FPI reversal, or none;
- authority source: Session FPI, Macro FPI, both, or reversal state;
- invalidation condition.

"Able to execute in all 1,008 possibilities" means every state has a complete decision path. It does not mean forcing a trade in every state. Some states correctly resolve to WAIT or NO TRADE.

## 10. Entries visible in the July 19 reference chart

Expected behavior around the marked bullish example:

- Session FPI is bullish.
- The low-area bullish OB confirms.
- Price retests that OB and closes above it around the first orange mark.
- The system should buy on that close.
- A later supporting bullish IMB retest may create a second buy opportunity only if the system is flat.
- The buy around the later consolidation near 10:03 is not valid merely because price paused or because the wrapper produced a signal. It needs one of the defined entry signatures.

## 11. Position constraints

- Pyramiding remains disabled unless the user explicitly changes it.
- Do not issue additional entries while already holding a position.
- A later valid foundation should be recorded as context but not create another position while the first remains open.

## 12. Trade management that must be preserved

Preserve the existing full engine's:

- hard structural invalidations;
- stop placement logic;
- break-even logic;
- target logic;
- multi-confluence exit logic;
- second-retest exit behavior;
- authority-loss exits;
- forced-flat time;
- MMBM/MMXM campaign holding behavior;
- session result reporting and trade ledger.

Some historical versions contain conflicting numeric target rules. Do not silently choose one. Verify the intended final bracket and campaign rules with the user before changing those numeric values.

## 13. Time behavior

The current chart examples explicitly require valid entries before 10:00 when the Session-FPI/OB signature confirms. Therefore, an unconditional "no trading before 10:00" gate is not compatible with the latest shown behavior.

Any time gate must be treated as a configurable rule and confirmed with the user rather than assumed from an older revision.