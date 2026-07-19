# Prompt for the Next AI / Chat

Copy everything below into the new chat and attach or link the repository files.

---

You are taking over development of a TradingView Pine Script v6 strategy named **PO3 MMXM Enigma**.

Repository:

- owner/repo: `THAMAB201/po3`
- branch: `enigma-professional-package`
- project folder: `PO3_MMXM_Enigma`
- handoff folder: `PO3_MMXM_Enigma/HANDOFF`

Read these files before proposing code:

1. `HANDOFF/README_FIRST.md`
2. `HANDOFF/TRADING_LOGIC_SPEC.md`
3. `HANDOFF/ARCHITECTURE_AND_REFACTOR_PLAN.md`
4. `HANDOFF/KNOWN_FAILURES_AND_ACCEPTANCE_TESTS.md`
5. the complete current and historical Pine sources in `PO3_MMXM_Enigma`

## Non-negotiable instruction

Do not replace the full engine with a reduced wrapper. Do not delete features to make the code compile.

The approximately 400-line current Execution Engine is a failed wrapper that imports the old full `PO3MMXMEnigmaExecutionEngine/2`. Publications `/3`, `/4`, and `/5` are failed experimental builds.

Recover the complete full-engine source that produced `/2` or the earlier complete 1.8 engine. Refactor that full source into functions and, if required, create a second execution-related library named `PO3MMXMEnigmaSignalEngine`.

The target architecture is:

```text
PO3 MMXM Enigma Strategy
        ↓
PO3MMXMEnigmaExecutionEngine
        ├── PO3MMXMEnigmaSignalEngine
        ├── PO3MMXMEnigmaStateManager
        └── PO3MMXMEnigmaCatalogResolver
```

The refactor must preserve the entire system: FPI, Macro FPI, 30-minute FPI, OB, IMB, BGOB, Judas, reversal state, entries, exits, holding, management, drawings, result tables, trade ledger, and the 1,008-case catalog.

## Primary entry rule that is currently broken

For a bullish setup:

```text
First valid Session FPI after 9:30 is bullish
→ keep bullish Session FPI authority across later phases
→ detect a valid local bullish OB below price
→ OB confirms when price closes above its top with bullish displacement
→ price later physically retests the OB
→ wick penetration is allowed if the body does not invalidate it
→ retest candle closes back above the OB top
→ BUY immediately on that close
```

A later IMB is not required for this primary OB entry.

Mirror this exactly for bearish Session FPI and bearish OB retest/close below.

## Separate continuation rule

After an OB has confirmed and successfully retested:

```text
track the relevant directional IMB formed afterward
→ first later physical retest of that IMB
→ directional close beyond the IMB boundary
→ continuation entry if flat
```

Do not wait for a second retest. Do not attach an old unrelated IMB to the new OB.

## July 19 regression case

The user supplied MNQ one-minute screenshots showing:

- bullish Session FPI;
- a confirmed bullish OB near the session low;
- a retest and close above that OB around the first orange mark — this must BUY;
- a later possible IMB continuation setup around the second orange mark if flat;
- an unsupported buy around the later 10:03 consolidation — this must not BUY without a valid documented signature.

## 1,008-case requirement

The catalog must not remain display-only. Every one of the 1,008 valid normalized combinations must map to:

- approved direction;
- market state;
- allowed entry families;
- terminal action: BUY, SELL, WAIT, REVERSAL, or NO TRADE;
- invalidation condition.

This does not mean forcing a trade in every state. It means every state has a complete executable decision path.

## Compile requirement

The old full engine produced Pine error CE10295 because the main body was too long.

Fix this by decomposing the complete logic into helper functions and/or the new Signal Engine library. Do not solve it by importing the old engine and adding a small overlay.

## Working method

Before writing code:

1. identify the exact full source file that must be refactored;
2. give a feature inventory proving nothing will be removed;
3. restate the primary OB entry, continuation IMB entry, Session FPI persistence, Macro conflict handling, and catalog role;
4. show the proposed function/library split;
5. wait for confirmation if any rule is genuinely ambiguous.

When coding:

- provide complete replacement files, not fragments;
- use stable professional filenames without development numbers;
- do not advance a TradingView import version until that library has actually compiled and been published;
- never claim TradingView compilation success unless it was confirmed in TradingView;
- preserve all visuals and management features unless explicitly instructed otherwise.

Start by auditing the repository and explaining which full source you will refactor and how you will prevent feature loss.

---