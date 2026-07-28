# Current Code and Known Failures

## Current source

- File: `enigma/PO3_MMXM_Enigma_Strategy_V9_5_1_Session_Recovery_Decoupled.pine`
- Header: `PO3E951R`
- Branch: `enigma-v9-3-window-narrative`
- Imports:
  - `SunovaBeach/PO3MMXMMarketModel/3`
  - `SunovaBeach/PO3MMXMDecisionModel/2`

## What the current line of development improved

- Three editable session starts.
- Session-boundary stock-gap filter.
- First Macro FPI tracked separately.
- Current-window OB/BOLO + aligned IMB recovery sequence.
- Tactical Session + Macro break latch for opposite-direction search.
- BGOB lifecycle attempts.
- Irreversible IMB invalidation.
- Consecutive body-series preference.
- Master drawings toggle off by default.
- One-trade-per-window control.
- Interval-close structural exit deferral with hard maximum stop.
- Detection partly decoupled from local FPI authorization in V9.5.1.

These improvements must not be discarded by a reduced rewrite.

## Latest critical failure: bearish FPI sell mislabeled as Judas

The latest screenshot shows a bearish Session FPI. The strategy displays `JUDAS-END-SELL`.

The sell direction equals the bearish Session FPI direction, so the new trade is a Session delivery/recovery sell, not Judas.

The likely source is the recovery rule naming logic:

```pine
string recoveryRule = phase == PHASE_JUDAS ?
    (recoveryDirection == DIR_LONG ? "JUDAS-END-BUY" : "JUDAS-END-SELL") :
    (recoveryDirection == DIR_LONG ? "WINDOW-DELIVERY-BUY" : "WINDOW-DELIVERY-SELL")
```

This uses campaign phase to name the trade. Correct implementation must separate:

```text
tradeClass      = direction relative to Session FPI
transitionEvent = previous phase to new phase
entryRule       = structure family that triggered the trade
```

Required output for the screenshot:

```text
tradeClass      = SESSION_DELIVERY
entryDirection  = SELL
transitionEvent = JUDAS_END, only if a Judas campaign was actually active
entryLabel      = SESSION-DELIVERY-SELL or SESSION-RECOVERY-SELL
```

`tradeIsJudas` must also be set from direction relative to Session FPI, not from `phase` or which candidate object happened to emit the signal.

## Repeated regression pattern

Most regressions came from coupling structure detection to authority filters.

Example deadlock:

```text
local 30m FPI does not align
→ recoveryWindowEligible = false
→ valid BOLO and IMB are not promoted
→ stale Judas latch remains active
→ later false Judas signal wins
```

The fix is architectural: detect and preserve evidence first; apply authority only at signal approval.

## Known failure classes

### 1. Trade-class and label confusion

- Same-direction trade called Judas because phase remained `PHASE_JUDAS`.
- `JUDAS_END` used as trade name instead of transition metadata.
- BGOB family label mixed with campaign class.

### 2. Local-FPI authorization deadlock

- Valid Session-direction OB/BOLO + IMB sequence blocked because current window has no FPI or opposing FPI.
- Structure evidence disappears instead of waiting for approval.

### 3. Stale Judas authority

- Old Session + Macro break remains latched after Session-direction structure begins rebuilding.
- Later windows receive counter-bias permission from old conditions.

### 4. Cross-window structure mixing

- Old IMB attached to new BOLO.
- New IMB attached to stale foundation.
- Foundation and support provenance not checked consistently.

### 5. Invalid IMB reuse

- Disrespected IMB later treated as respected.
- Copied support object remains live after original source invalidates.

### 6. Wrong extreme foundation

- Lowest isolated candle replaces valid consecutive BOLO series.
- Highest/lowest price chosen without validating body-series provenance.

### 7. BGOB definition drift

- Made-up labels such as `30m BGOB seed` shown to user.
- BGOB inferred from generic FPI zone without matching user framework.
- Macro BGOB not persisted or not recognized.

### 8. Premature exits

- Generic fixed target closes a structurally valid delivery.
- Structural close exits before the 30-minute interval finishes.
- Judas exits on same-window noise instead of later-window completed reversal.

### 9. Missing valid entries

- No buy in the third 30-minute window after first two windows fail and a valid BOLO + IMB finally completes.
- No sell after Session FPI and first Macro FPI both close-disrespect and fresh bearish structure confirms.
- No Macro BGOB trade despite a complete close-beyond/retest/respect sequence.

### 10. Tilt trading

- Recovery and Judas engines emit competing signals in the same interval.
- Repeated flips occur because no single narrative owns the window.
- A stop resets position state but does not reset the stale campaign cause.

## Rules for future patches

1. Never rewrite the whole engine to fix one screenshot.
2. Freeze the current source before editing.
3. One patch, one stated purpose.
4. Add a test before adding the rule.
5. Detection code may not depend on entry permission.
6. Trade classification must be direction-based.
7. Source-window provenance must be stored on every foundation/support.
8. Invalidated IMBs and their copies must be killed together.
9. Compare all locked examples after every patch.
10. Reject any patch that removes a previously correct hallmark entry.

## Recommended immediate next correction

Do not add another entry filter first. Correct classification and observability:

```text
selectedDirection
sessionDirection
isSessionDirection
isJudasDirection
tradeClass
transitionEvent
entryFamily
entryRule
```

Then replace phase-based labels and `tradeIsJudas` assignment. This will make the chart and diagnostics truthful before further behavior changes.
