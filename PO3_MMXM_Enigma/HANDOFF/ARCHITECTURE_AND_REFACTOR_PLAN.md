# PO3 MMXM Enigma — Architecture and Refactor Plan

## Objective

Refactor the complete full engine so it compiles under Pine Script limits without deleting behavior.

The prior approximately 4,000-line engine failed with CE10295 because too much logic was concentrated inside one exported `run()` body. The failed workaround replaced that source with a roughly 400-line coordinator that imported the old `/2` engine. That did not modify the core logic and must not be repeated.

## Required architecture

Use five permanent scripts if the full engine cannot fit cleanly into four:

```text
PO3 MMXM Enigma Strategy
        ↓
PO3MMXMEnigmaExecutionEngine
        ├── PO3MMXMEnigmaSignalEngine
        ├── PO3MMXMEnigmaStateManager
        └── PO3MMXMEnigmaCatalogResolver
```

### `PO3MMXMEnigmaStateManager`

Keep reusable state and trade-management structures here:

- OB/IMB/BGOB state records;
- retest counters;
- foundation respect/disrespect state;
- expansion and giveback tracking;
- trade ledger helpers;
- management-state transitions.

### `PO3MMXMEnigmaCatalogResolver`

Keep the complete 1,008-case mapping here:

- normalized Session FPI state;
- Macro FPI state;
- price location;
- sweep/Judas state;
- structure state;
- approved direction;
- terminal action and allowed entry families.

Catalog enforcement should be configurable, but the execution engine must consume the resolved state rather than leaving it as a display-only audit.

### `PO3MMXMEnigmaSignalEngine` — new helper library

Move pure signal detection and state transitions out of the oversized execution body:

- session and 30-minute time/window state;
- Session FPI detection and persistent authority;
- Macro FPI detection;
- local OB detection, validation, and BOLO retest;
- IMB creation and parent-OB association;
- BGOB confirmation;
- Judas/pullback and reversal-state transitions;
- generation of typed signal candidates.

This library should not place strategy orders. It should return structured signals and authority state to the execution engine.

Suggested exported types:

```pine
export type AuthorityState
    int sessionDirection
    int macroDirection
    int resolvedDirection
    int marketState
    int catalogCaseId
    bool reversalMode

export type FoundationSignal
    bool valid
    int direction
    int entryFamily
    int sourceWindow
    int sourceBar
    float zoneTop
    float zoneBottom
    float invalidationPrice
    bool sessionAligned
    bool macroAligned

export type SignalOutput
    AuthorityState authority
    FoundationSignal primaryObRetest
    FoundationSignal postObImbRetest
    FoundationSignal bgobSignal
    FoundationSignal priorFpiReversal
```

### `PO3MMXMEnigmaExecutionEngine`

Keep this as the coordinator:

- call the signal engine;
- select the highest-priority valid signal;
- enforce flat/pyramiding/order timing rules;
- place `strategy.entry`, `strategy.exit`, and `strategy.close` orders;
- maintain trade management and holding logic;
- draw chart objects and reporting visuals;
- expose `EnigmaOutput` to the strategy shell.

The coordinator should not redetect the same OB, IMB, or FPI independently. There must be one source of truth for each state.

### `PO3 MMXM Enigma` strategy shell

The shell should remain small:

- user inputs;
- construction of the config object;
- one call to the execution engine;
- alerts and Data Window plots.

## Function decomposition inside the signal engine

Split the main logic into focused functions instead of one giant `run()` body:

```text
updateSessionClock()
updateFpiState()
updateMacroFpiState()
updateOrderBlockState()
updateImbalanceState()
updateBgobState()
updateJudasAndReversalState()
resolveCatalogState()
buildPrimaryObRetestSignal()
buildPostObImbSignal()
buildBgobSignal()
buildPriorFpiReversalSignal()
selectSignalCandidate()
```

Use user-defined types to pass grouped state instead of hundreds of local variables.

## Critical state rules

### Session FPI persistence

Do not reset the Session FPI when the market enters a new 30-minute phase, lunch, or PM session. Store it as session-level state and reset it only at the next session start.

### Source ownership

Every signal must carry:

- source bar;
- source timestamp;
- source 30-minute window;
- parent OB identifier;
- related IMB identifier;
- entry family.

This prevents old unrelated IMBs from authorizing a new OB and prevents same-window rules from accidentally blocking cross-window reversal foundations.

### Entry consumption

Do not mark an interval or foundation as used while constructing a candidate. Mark it used only after the execution engine actually submits the order.

### No breakout-only execution

A breakout may arm a foundation. It does not execute by itself. The execution event must be the required retest and directional close.

## Signal priority

When flat and more than one signal appears on the same bar, use a deterministic priority such as:

1. hard reversal/invalidation transition;
2. primary Session-FPI-aligned OB retest;
3. confirmed BGOB;
4. post-OB IMB retest;
5. prior respected FPI reversal;
6. no trade.

The exact priority can be adjusted, but it must be explicit and testable.

## Preserving the full system

The refactor must retain all existing visuals and management behavior unless a requirement explicitly replaces them.

Do not remove code merely to compile. Move it into functions or a helper library.

Before changing any behavior, create a feature inventory from the full source and verify that every feature has a destination in the new architecture.

## Versioning procedure

Use stable filenames and titles. Publish new immutable TradingView versions only after the source compiles.

Do not advance the strategy import until the new engine version has been successfully published.

Never claim TradingView compilation success based only on GitHub text generation or a source-level string check.