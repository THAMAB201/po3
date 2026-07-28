# PO3 MMXM Enigma — Continuation Handoff

**Prepared:** 2026-07-27  
**Purpose:** Allow another AI/developer, or a new chat tomorrow, to continue without reconstructing the rules from screenshots and failed revisions.

## Read this before changing code

The strategy is not a generic breakout, ORB, or trend-following system. It is a one-minute, state-driven MMXM execution model based on:

- Session/controller FPI;
- first Macro FPI and Macro range;
- exact 30-minute windows;
- regular OBs, consecutive candle-body OB series, BOLO OBs, IMBs, BGOBs;
- Judas movement opposite the Session FPI;
- later delivery back in Session-FPI direction;
- completed one-minute body closes, retests, respect, invalidation, and interval-end holding decisions.

Do not add EMA, VWAP, RSI, generic trend filters, or made-up structures.

## Critical diagnosis from the latest screenshot

The displayed Session FPI is **bearish**. Therefore:

- a **sell** in bearish Session-FPI direction is a **Session delivery / continuation sell**;
- it is **not a Judas sell**;
- a **buy** against that bearish Session FPI is the Judas side until the bearish controller is invalidated and a bullish controller is formally accepted.

The label `JUDAS-END-SELL` is a semantic/state-classification defect. The current code derives the label from `phase == PHASE_JUDAS`. That confuses a phase transition with the direction/classification of the new trade.

Canonical classification must be direction-based:

```text
trade direction == active Session FPI direction
    => SESSION_DELIVERY / SESSION_RECOVERY / CONTINUATION

trade direction == opposite active Session FPI direction
    => JUDAS
```

`JUDAS_END` may be logged as a transition event, but it must not classify the new same-direction trade as Judas.

## Current experimental source

- Repository: `THAMAB201/po3`
- Branch: `enigma-v9-3-window-narrative`
- File: `enigma/PO3_MMXM_Enigma_Strategy_V9_5_1_Session_Recovery_Decoupled.pine`
- TradingView header: `PO3E951R`
- Imports:
  - `SunovaBeach/PO3MMXMMarketModel/3`
  - `SunovaBeach/PO3MMXMDecisionModel/2`

This source is the current working experiment, not a frozen canonical implementation. It contains progress but still has state-labeling and campaign-classification defects.

## Handoff folder map

1. `01_CANONICAL_LOGIC.md` — complete current rule contract.
2. `02_STATE_MACHINE.md` — required state architecture and pseudocode.
3. `03_DEFINITIONS.md` — FPI, Macro FPI, OB, BOLO, IMB, BGOB, Judas, ORB.
4. `04_CURRENT_CODE_AND_KNOWN_FAILURES.md` — current source, what works, and what is still wrong.
5. `05_ACCEPTANCE_TESTS.md` — replay scenarios that every revision must pass.
6. `06_PROMPT_FOR_NEXT_AI.md` — ready-to-paste continuation prompt.
7. `07_DECISION_LOG.md` — important user decisions and superseded assumptions.
8. `08_SOURCE_MANIFEST.md` — source documents, datasets, and code references.

## Mandatory continuation procedure

1. Read all files in this folder.
2. Restate the classification and state model before editing.
3. Preserve the current source as an immutable baseline.
4. Make one narrowly scoped change at a time.
5. Recompile in TradingView.
6. Replay the locked acceptance examples.
7. Compare trade count, labels, entry times, exit times, P&L, and drawdown against the baseline.
8. Reject the patch if a previously valid hallmark trade disappears.
9. Provide complete replacement code, not partial line-edit instructions.

## Non-negotiable engineering rule

Detection, authority, classification, order submission, and position management must be separate layers. A filter added to authority may not prevent valid OB/BOLO/IMB evidence from being recorded. This coupling caused repeated regressions throughout the prior revisions.
