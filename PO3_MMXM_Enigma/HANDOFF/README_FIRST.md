# PO3 MMXM Enigma — Read This First

This folder is the handoff package for another AI or developer.

## Project objective

Build the complete TradingView strategy **PO3 MMXM Enigma** without deleting existing logic or replacing the full engine with a small wrapper.

The finished strategy must:

- preserve the complete FPI, Macro FPI, OB, IMB, BGOB, Judas, reversal, holding, exit, reporting, and visual systems;
- classify all 1,008 catalog combinations;
- allow every catalog state to reach a defined action: buy, sell, wait, pullback, reversal, or no-trade;
- execute only when the required price-action signature confirms;
- compile within Pine Script limits by splitting the full engine into helper functions and, if needed, a second execution-related library.

## Current truth

The current approximately 400-line `PO3_MMXM_Enigma_Execution_Engine.pine` is **not the full engine**. It imports the old full `PO3MMXMEnigmaExecutionEngine/2` publication and adds supplemental logic on top.

That wrapper approach is rejected. It caused the chart behavior to remain controlled by old logic and created misleading claims that the core engine had been fixed.

Treat engine publications `/3`, `/4`, and `/5` as failed experimental builds. Do not use them as the foundation of the final refactor.

## Required starting point

Recover and work from the complete full-engine source that produced `PO3MMXMEnigmaExecutionEngine/2` or the earlier full 1.8 engine source. Refactor that source rather than rewriting a reduced substitute.

The Pine error that forced the refactor was:

`The main body of the script is too long. Try wrapping code in functions (CE10295)`

The correct solution is to split the full logic into functions and/or another library, not remove features.

## Permanent professional names

- `PO3_MMXM_Enigma_State_Manager.pine` → `PO3MMXMEnigmaStateManager`
- `PO3_MMXM_Enigma_Catalog_Resolver.pine` → `PO3MMXMEnigmaCatalogResolver`
- `PO3_MMXM_Enigma_Signal_Engine.pine` → `PO3MMXMEnigmaSignalEngine` — new helper library if needed
- `PO3_MMXM_Enigma_Execution_Engine.pine` → `PO3MMXMEnigmaExecutionEngine`
- `PO3_MMXM_Enigma_Strategy.pine` → `PO3 MMXM Enigma`

Do not put development numbers such as `Lib15`, `Lib18`, `_1_8`, `v5`, or `Final_Final` in permanent filenames or TradingView titles. TradingView publication numbers belong only in import paths.

## Files in this handoff

- `TRADING_LOGIC_SPEC.md` — authoritative strategy behavior
- `ARCHITECTURE_AND_REFACTOR_PLAN.md` — how to preserve the full engine while fixing CE10295
- `KNOWN_FAILURES_AND_ACCEPTANCE_TESTS.md` — what is currently wrong and how to prove the fix
- `PROMPT_FOR_NEXT_AI.md` — a ready-to-paste prompt for a new AI/chat

The next developer must first restate the logic and proposed architecture. Do not begin another reduced rewrite before confirming those requirements.