# PO3 MMXM Enigma — Known Failures and Acceptance Tests

## Known failures in the current branch

### 1. The current Execution Engine is a wrapper

The roughly 400-line engine imports `PO3MMXMEnigmaExecutionEngine/2` as `baseEngine` and then adds supplemental entries.

This means the old full engine still controls most behavior. The core was not actually corrected.

### 2. Failed publications

Treat `/3`, `/4`, and `/5` as failed experimental engine publications. They should not be used as the foundation of the final system.

### 3. CE10295 was not solved correctly

The full source hit:

`The main body of the script is too long. Try wrapping code in functions (CE10295)`

The correct fix is structural decomposition, not a reduced wrapper.

### 4. Session FPI authority was lost or misidentified

The system has reset or replaced the controller during later phases and has sometimes treated a local imbalance as the controller instead of preserving the first valid Session FPI after 9:30.

### 5. The correct low-area buy was missed

In the July 19 MNQ 1-minute example:

- the Session FPI was bullish;
- a bullish OB near the session low confirmed;
- price retested the OB;
- the candle closed above the OB;
- the strategy should have bought on that close.

It did not.

### 6. A later bad buy was taken

The system bought around the later 10:03 consolidation even though there was no valid reason under the intended signature. The wrapper-generated signal was not equivalent to the marked low-area OB retest.

### 7. OB and IMB sequencing was confused

Earlier patches alternated between:

- requiring an IMB before an OB retest;
- waiting for a second IMB retest;
- attaching old IMBs to new OBs;
- treating the IMB as mandatory for the primary OB entry.

The correct behavior is documented in `TRADING_LOGIC_SPEC.md`.

### 8. Claims about all 1,008 cases were overstated

The catalog may classify 1,008 rows, but the current execution path does not fully consume the catalog and does not prove that all states have complete action policies.

## Mandatory acceptance tests

The next developer must test with Strategy Tester and chart replay. A GitHub commit or text search is not proof.

### Test A — Bullish Session-FPI OB retest

Given:

- first valid Session FPI after 9:30 is bullish;
- a valid bullish OB forms below price;
- price closes above the OB to confirm it;
- a later candle trades into the OB and closes back above the OB top;
- strategy is flat.

Expected:

- BUY is submitted on the retest candle close;
- the OB/foundation is marked used only after order submission;
- no later IMB is required.

### Test B — Bearish mirror

Mirror Test A. A bearish Session FPI plus confirmed bearish OB retest and close below must submit SELL.

### Test C — Post-OB IMB continuation

Given:

- primary OB has confirmed and successfully retested;
- a directional IMB forms afterward;
- price later physically retests the relevant IMB;
- candle closes in the directional side of the IMB;
- strategy is flat.

Expected:

- continuation entry on the first valid retest close;
- no second retest required;
- IMB must be associated with the correct OB sequence.

### Test D — Reject the later invalid buy

For the July 19 reference chart around 10:03:

Expected:

- no buy unless a documented OB retest, post-OB IMB retest, BGOB, or other approved signature is actually present;
- a pause, small consolidation, or inherited `baseEngine` signal is insufficient.

### Test E — Session FPI persists

Given a bullish Session FPI and later phase transitions:

Expected:

- `sessionDirection` remains bullish through AM/lunch/PM until explicit invalidation or reversal mode;
- phase changes do not reset Session FPI state.

### Test F — Macro conflict

Given bullish Session FPI and bearish Macro FPI:

Expected:

- the catalog resolves a conflict/pullback/Judas state;
- the engine still recognizes valid bullish structural foundations;
- the action policy decides BUY, WAIT, or reversal based on the complete case, not because the detector stopped functioning.

### Test G — Catalog completeness

Programmatically enumerate all 1,008 normalized catalog inputs.

For each row verify:

- unique case ID;
- approved bias;
- market state;
- terminal action;
- allowed entry families;
- invalidation rule;
- no unmapped or impossible output.

Some cases may correctly return WAIT/NO TRADE.

### Test H — No duplicate position

Given a later valid signal while already long or short:

Expected:

- no second entry because pyramiding is disabled;
- context may update, but position size does not increase.

### Test I — Full feature preservation

Before and after refactor, verify that the following still exist and function:

- Session and Macro FPI drawings;
- 30-minute dividers;
- OB/IMB/BGOB drawings;
- Judas/reversal state;
- hard stops and structural invalidations;
- break-even logic;
- targets and campaign holding;
- multi-confluence exits;
- force-flat logic;
- entry/exit labels and triangles;
- trade lines;
- interval trade tables;
- NY Session result display;
- trade ledger;
- catalog Data Window fields.

### Test J — Pine compile limits

Expected:

- every library compiles in TradingView;
- no CE10295;
- no missing import/version error;
- no look-ahead warning from `calc_on_order_fills`;
- no same-bar duplicate entry/exit caused by improper state consumption.

## Reference chart expectations

Use the user-provided July 19 MNQ one-minute screenshots as the first regression case:

- expected low-area OB-retest buy around the first orange annotation;
- possible later IMB continuation opportunity around the second orange annotation if flat;
- no unsupported buy around the later consolidation near 10:03.

The developer should ask for the exact TradingView date/symbol/time zone only if the chart cannot be reproduced from the screenshots.