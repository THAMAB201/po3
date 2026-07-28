# Source Manifest

## Repository source

### Current experimental strategy

- Repository: `THAMAB201/po3`
- Branch: `enigma-v9-3-window-narrative`
- Path: `enigma/PO3_MMXM_Enigma_Strategy_V9_5_1_Session_Recovery_Decoupled.pine`
- Header: `PO3E951R`

### Current dependencies

- `SunovaBeach/PO3MMXMMarketModel/3`
- `SunovaBeach/PO3MMXMDecisionModel/2`

The next AI must inspect the actual exported types/functions in these libraries before changing BGOB, BOLO, FPI, or signal construction logic.

## Canonical and historical user files

The user’s file library contains these important sources. Attach or retrieve them when continuing in a new environment.

### Canonical architecture

- `MMXM_Complete_Decision_Architecture_v4.md`
  - Canonical deterministic architecture freeze dated 2026-07-18.
  - Includes hierarchy, controller state, Macro state, structural rules, and risk authority.
  - Note: its older “Lunch neutral” wording is superseded by the later explicit three-controller-session rule in this handoff.

### Outcome catalog

- `MMXM_Core_Outcome_Catalog_v4.csv`
  - Structured truth table with Session/Macro combinations, location, sweeps, structure, resolved state, terminal action, and reason.
  - Approximately 1,008 combinations were a project requirement.

### AI build prompt

- `MMXM_30m_AI_Build_Prompt_v3.md`
  - Requires deterministic closed-candle processing.
  - Explicitly forbids invented rules and unrelated indicators.

### Restored strategy reference

- `MMXM_Bot_Strategy_Entries_Restored.pine`
  - Important older source preserving delayed FPI recovery, Macro continuation, retest requirements, and entry families.
  - Use as a behavior reference, not automatically as the new baseline.

### Historical 30-minute strategy

- `Sunova_MMXM_30M_Macro_Strategy_v2.txt`
  - Contains prior explicit purpose statements:
    - first FPI establishes direction;
    - one fresh setup per 30-minute interval;
    - FPI is context, not raw entry;
    - entries from BGOB/confirmed OB/BOLO/IMB/Macro reclaim.

### Earlier Enigma references

- `PO3_MMXM_Enigma_V9_2_1_Opening_Low_Fix.pine`
- `PO3_MMXM_Enigma_V9_2_1_Opening_Patch.pine`
- prior R5 modular rebuild folder and associated acceptance tests.

These contain useful management/output logic but are not automatically authoritative over the latest user instructions.

## Latest screenshot evidence

Conversation image dated 2026-07-27 around 3:35 PM mobile TradingView:

- instrument: NQ one-minute;
- displayed Session FPI: bearish;
- strategy label: `JUDAS-END-SELL`;
- user correction: the sell is not Judas because it is in bearish FPI direction.

This example is formalized as `AT-001` in `05_ACCEPTANCE_TESTS.md`.

## Current code status

- Current strategy has not been certified as fully correct.
- Pine compilation must be confirmed in TradingView after every edit.
- Profitability on a selected range is not sufficient proof; all hallmark replay examples must pass.
- Labels are currently not reliable proof of internal classification.

## Recommended version-control layout

```text
controls/
    frozen profitable baseline

experiments/
    one branch per narrow patch

handoff/PO3_MMXM_2026-07-27/
    canonical current instructions

tests/
    replay scenario manifests and expected traces
```

## Required next source snapshot

Before the next logic edit, save an immutable copy of `PO3E951R` under a control filename or tag. Record:

- commit SHA;
- TradingView strategy properties;
- symbol/contract;
- date range;
- total P&L;
- maximum drawdown;
- profitable trade percentage;
- screenshots for each hallmark example.

Without a frozen control, progress cannot be measured and regressions will continue to alternate between examples.
