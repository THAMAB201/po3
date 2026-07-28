# Required State Machine

The next implementation must stop deriving behavior from scattered booleans. Use explicit state objects and transitions.

## 1. Separation of layers

The engine has five independent layers:

1. **Detection** — records Session FPI, Macro FPI, local FPI, OB/BOLO, IMB, and BGOB evidence.
2. **Narrative authority** — decides whether Session direction, Judas direction, or neither is permitted.
3. **Trade classification** — classifies the selected direction relative to the active Session FPI.
4. **Order execution** — submits/reverses once the full causal sequence is approved.
5. **Position management** — holds, exits, or reverses using the frozen governing structures.

A failure or filter in layer 2 must not prevent layer 1 from recording valid evidence.

## 2. Session campaign state

```text
WAIT_SESSION_FPI
SESSION_ACTIVE
JUDAS_ACTIVE
DELIVERY_ACTIVE
SESSION_COMPLETE
FORCED_FLAT
```

### WAIT_SESSION_FPI

- Starts at 09:30, 11:30, and 13:30.
- Ignore any FPI crossing the session start when stock/RTH gap filtering is enabled.
- Transition to `SESSION_ACTIVE` when the first valid post-start FPI is confirmed.

### SESSION_ACTIVE

- Session FPI is the global objective.
- Search every local 30-minute window for both Session-direction and tactical/Judas-direction structures.
- Session-direction structures do not require a local FPI before they can be detected.

### JUDAS_ACTIVE

- Tactical direction is opposite Session FPI.
- Enter only after the complete opposite-direction structure sequence.
- Do not exit for same-window noise.
- Later-window Session-direction completion transitions to `DELIVERY_ACTIVE` and reverses/exits the Judas position.

### DELIVERY_ACTIVE

- Active position direction equals Session FPI direction.
- Hold while frozen foundation/support remain respected.
- Later same-direction structures validate the hold, not pyramid.

### SESSION_COMPLETE / FORCED_FLAT

- No new campaign entries after forced-flat cutoff.
- Reset controller state at the next session start.

## 3. Direction classification

Never use `phase` alone to decide whether a trade is Judas.

```pine
bool selectedIsSessionDirection = selectedDirection == sessionDirection
bool selectedIsJudasDirection   = selectedDirection == -sessionDirection

tradeClass = selectedIsSessionDirection ? CLASS_SESSION_DELIVERY :
             selectedIsJudasDirection   ? CLASS_JUDAS :
                                          CLASS_NONE
```

A transition may separately be logged:

```text
previous campaign = JUDAS_ACTIVE
new trade class   = SESSION_DELIVERY
transition event  = JUDAS_END
```

The entry label remains `SESSION-DELIVERY-BUY/SELL`; `JUDAS_END` is diagnostic metadata.

## 4. Per-window narrative state

```text
SEARCH
BUILD_SESSION
BUILD_JUDAS
LOCK_SESSION
LOCK_JUDAS
RESOLVED
INVALID
```

### SEARCH

- Detect both directions independently.
- Track the most-extreme valid foundation for each direction.
- Track aligned IMBs and framework BGOBs.
- Do not select a trade yet.

### BUILD_SESSION

- A Session-direction foundation has confirmed.
- Continue binding only causally valid Session-direction support.
- Suspend stale Judas latch from stealing the window.
- Do not enter until IMB/BGOB completion.

### BUILD_JUDAS

- A tactical/Judas foundation has confirmed under valid opposite authority.
- Continue binding only causally valid Judas support.
- Do not enter until IMB/BGOB completion.

### LOCK_SESSION / LOCK_JUDAS

- One side has a complete causal sequence or an advanced support state.
- Opposite side is blocked unless the locked foundation is body-close invalidated.
- Authority cannot be inherited from a stale prior window.

### RESOLVED

- Entry submitted or window explicitly consumed.
- No second new entry in that window unless a user-approved reversal exception is configured.

### INVALID

- Governing foundation or support permanently failed.
- Wait until next 30-minute window.

## 5. Foundation lifecycle

```text
CANDIDATE
DISPLACEMENT_CONFIRMED
SUPPORT_WAIT
SUPPORT_ARMED
RETESTED
ENTRY_APPROVED
INVALID
CONSUMED
```

### CANDIDATE

- Regular consecutive body-series OB or BOLO selected.
- Correct source window required.
- For Session direction: lowest bullish / highest bearish.
- For Judas direction: same extreme logic in tactical direction.

### DISPLACEMENT_CONFIRMED

- Price displaces in intended direction.
- Foundation body remains valid.
- The displacement may simultaneously form the supporting IMB.

### SUPPORT_ARMED

- Same-window aligned IMB is bound to the exact foundation.
- Or a framework-defined BGOB has completed its close-beyond stage.

### RETESTED

- A later candle physically overlaps the support.
- The formation/confirmation candle cannot count as its own later retest.

### ENTRY_APPROVED

- Completed directional close outside the support.
- Foundation still valid.
- IMB has never previously been disrespected.
- Direction passes Session/Judas authority.

### INVALID

- Foundation body closes beyond its invalidation.
- Or supporting IMB receives permanent body-close disrespect.
- Or BGOB exceeds allowed penetration.

### CONSUMED

- Used support cannot be reused by another foundation or engine.

## 6. IMB lifecycle

```text
NEW
BOUND
TOUCHED
CONFIRMED
INVALID_PERMANENT
CONSUMED
```

Transitions:

```text
NEW -> BOUND
    only if same active window and sourceBar >= foundation confirmation displacement

BOUND -> TOUCHED
    later physical retest

TOUCHED -> CONFIRMED
    directional body close through intended edge

ANY LIVE STATE -> INVALID_PERMANENT
    bullish: body close below bottom
    bearish: body close above top

CONFIRMED -> CONSUMED
    signal emitted
```

No transition exists from `INVALID_PERMANENT` back to live.

## 7. FPI state

FPI and IMB invalidation are not identical.

```text
ACTIVE_RESPECTED
DISRESPECTED
RECLAIMED
REQUALIFIED
```

- Disrespect requires a completed body close through the far edge.
- A wick does not change state.
- A reclaimed FPI may require another body close through the correct edge before re-entry.
- An IMB, unlike an FPI, cannot recover after permanent disrespect.

## 8. First Macro tactical authority

```text
MACRO_UNKNOWN
MACRO_SUPPORTIVE
MACRO_TESTING
MACRO_FAILED
TACTICAL_JUDAS_RELEASED
TACTICAL_JUDAS_CANCELLED
```

- Session + Macro break may release tactical Judas search.
- It does not create an entry.
- A confirmed Session-direction foundation cancels stale tactical authority before Judas selection.
- A fresh tactical release is required after the Session-direction foundation later fails.

## 9. Position state

```text
FLAT
PENDING_ENTRY
LONG_SESSION
SHORT_SESSION
LONG_JUDAS
SHORT_JUDAS
EXIT_PENDING_INTERVAL_CLOSE
FORCED_FLAT
```

Position class is frozen at entry from direction relative to the Session FPI.

### Holding rules

- Hard maximum stop remains live intrabar.
- Structural close failure may be deferred to the final one-minute close of the current 30-minute interval when enabled.
- Judas ignores incomplete local reversal and waits for a later-window completed Session-direction sequence.
- Same-direction confirmations validate hold; no pyramiding.

## 10. Closed-candle processing order

Use this deterministic order on every completed one-minute candle:

```text
1. Detect session/window boundary.
2. Reset only newly expired local state.
3. Update Session FPI and Macro FPI objects.
4. Update existing foundation/support invalidations.
5. Detect new OB/BOLO/IMB/BGOB evidence for both directions.
6. Advance structure lifecycles.
7. Update Session/Macro/local authority.
8. Cancel stale authority when a contrary valid foundation begins building.
9. Arbitrate one narrative for the active window.
10. Classify selected direction relative to Session FPI.
11. Submit or reverse orders.
12. Manage active position and interval-end exit.
13. Emit diagnostics and labels.
```

Do not reorder detection behind authority gates.

## 11. Required structured decision output

Every candle should expose one decision object:

```text
sessionId
sessionDirection
sessionFpiState
macroDirection
macroState
windowId
windowNarrative
foundationId
supportId
candidateDirection
approvedDirection
tradeClass
transitionEvent
terminalAction
reasonCode
```

This prevents a label such as `JUDAS-END-SELL` from hiding that the actual trade class is `SESSION_DELIVERY`.
