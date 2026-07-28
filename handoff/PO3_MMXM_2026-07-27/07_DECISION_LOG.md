# Decision Log and Superseded Assumptions

This log prevents older experimental assumptions from silently overriding later user instructions.

## Current binding decisions

### Sessions

- Three controller starts: 09:30, 11:30, and 13:30 New York.
- Each uses the first valid FPI after its own start.
- Earlier documentation describing Lunch as purely neutral is superseded by the later explicit instruction that 11:30 has its own FPI controller.

### FPI direction

- Session FPI is the overall direction/objective for its controller period.
- Price movement before delivery may be Judas.
- FPI disrespect uses body closes, not wicks.
- A same-direction trade is delivery even when it ends a prior Judas phase.

### Judas classification

- Bullish Session FPI → Judas side is sell.
- Bearish Session FPI → Judas side is buy.
- The latest bearish-FPI screenshot proves that `JUDAS-END-SELL` is an incorrect trade label.
- `JUDAS_END` is a transition event only.

### 30-minute windows

- Search resets locally every 30 minutes.
- Failed prior-window ordinary foundations/supports cannot be paired with new structures.
- Session FPI and first Macro context persist.
- If first two windows fail and the third forms the correct BOLO/OB + IMB sequence, the third must enter.

### Foundations

- Order block starts every run.
- Both regular OB and BOLO are allowed.
- Consecutive candle-body series is important and may be the true foundation.
- Wick penetration is allowed for BOLO; body-close violation invalidates.
- For bullish intent use the lowest valid foundation; bearish intent uses the highest valid foundation.

### Supporting IMB

- BOLO/OB alone cannot enter.
- Supporting IMB alone cannot enter.
- Displacement confirming the foundation may create the IMB.
- Entry requires later IMB retest and directional close.
- Once an IMB is disrespected it can never later be respected.

### BGOB

- User objected to invented definitions and labels.
- Use the existing framework/library definition.
- Required visible behavior: close beyond, later retest, directional close outside.
- Bullish BGOB stop at low; bearish mirror.
- First-Macro/third-candle BGOB cases must not be missed.

### Opposite trade safeguard

- When Session FPI and first Macro FPI are both disrespected, tactical opposite direction may be considered.
- Opposite entry still requires fresh structure.
- ORB safeguard is optional, hidden by default, and cannot replace structural confirmation.

### Holding

- Judas trade holds through same-window noise until a later 30-minute window confirms Session-direction reversal.
- Delivery should not close early merely from a generic target or intrainterval temporary failure.
- Interval-end evaluation was explicitly requested.
- Hard maximum stop remains active.

### Visuals

- Master drawings toggle off by default.
- No invented user-facing labels.
- Full replacement code only; no small manual edit instructions.

## Important superseded or rejected approaches

### Reduced wrapper architecture

Rejected. The full engine and existing entry families must be preserved. Do not replace the project with a small wrapper around old publications.

### Local FPI as mandatory structural detector gate

Rejected. Local FPI may influence authority but cannot stop valid Session-direction OB/BOLO and IMB evidence from being recorded.

### Phase-based Judas classification

Rejected. Direction relative to Session FPI determines trade class.

### Standalone OB or IMB Judas entry

Rejected. Judas also needs a complete causal sequence.

### Reusing an invalid IMB

Rejected permanently.

### Lowest isolated candle always wins

Rejected when a valid consecutive BOLO/body series exists.

### Same-bar structure confirmation and retest

Rejected. Retest must be later.

### Generic ORB strategy

Rejected. ORB is only an optional safeguard inside the technical MMXM system.

### Adding unrelated indicators

Rejected.

## Items that remain configuration-sensitive

These should remain explicit settings or be resolved with the user rather than guessed:

- Fixed target usage versus pure structural delivery hold.
- Whether second-separate-retest exit is enabled.
- Exact 50% BGOB entry penetration threshold.
- Maximum entries per session/window.
- Whether a second independent Judas campaign is allowed after a completed campaign.
- Exact PO3 completion target and activation time.
- Instrument-specific point/tick settings and commissions.

## Change-control rule

Every future decision must be added here with:

- date;
- exact new rule;
- which older rule it replaces;
- acceptance test added or changed.
