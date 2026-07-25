# V9.2.2 — Post-Disrespect Judas Continuation Patch

This patch keeps Session FPI direction structural, but permits confirmed OB/IMB/BGOB entries in the temporary disrespect/Judas direction.

## 1. Add this input under `G_PROTOCOL`

```pine
bool allowPostDisrespectJudasEntries = input.bool(true, "Trade Structures After Session FPI Disrespect", group = G_PROTOCOL)
```

## 2. Replace the entire `Structure permissions and creation` permission header

Replace:

```pine
int judasDirection = structuralDirection == market.DIR_NONE ? market.DIR_NONE : -structuralDirection
bool allowBothInventories = phase == PHASE_JUDAS and not judasCompleted
bool allowBullStructures = sessionFpiFound and (structuralDirection == market.DIR_LONG or allowBothInventories and judasDirection == market.DIR_LONG)
bool allowBearStructures = sessionFpiFound and (structuralDirection == market.DIR_SHORT or allowBothInventories and judasDirection == market.DIR_SHORT)
```

with:

```pine
int judasDirection = structuralDirection == market.DIR_NONE ? market.DIR_NONE : -structuralDirection

// Keep a hidden standby inventory in both directions from the moment the
// Session FPI is known. The opposite inventory cannot confirm or execute until
// the Session FPI receives a completed body-close disrespect.
bool standbyCounterInventory = enableJudasTrades and not judasCompleted
bool allowBullStructures = sessionFpiFound and (structuralDirection == market.DIR_LONG or standbyCounterInventory)
bool allowBearStructures = sessionFpiFound and (structuralDirection == market.DIR_SHORT or standbyCounterInventory)

// The Session-FPI direction may confirm normally. The opposite direction may
// confirm only during the active Judas phase after FPI disrespect.
bool bullCanConfirm = sessionFpiFound and (
     structuralDirection == market.DIR_LONG or
     allowPostDisrespectJudasEntries and phase == PHASE_JUDAS and judasDirection == market.DIR_LONG)
bool bearCanConfirm = sessionFpiFound and (
     structuralDirection == market.DIR_SHORT or
     allowPostDisrespectJudasEntries and phase == PHASE_JUDAS and judasDirection == market.DIR_SHORT)

// Opposite standby structures are tracked but remain hidden before disrespect.
bool showBullInventory = showStructureBoxes and (
     structuralDirection == market.DIR_LONG or
     phase == PHASE_JUDAS and judasDirection == market.DIR_LONG)
bool showBearInventory = showStructureBoxes and (
     structuralDirection == market.DIR_SHORT or
     phase == PHASE_JUDAS and judasDirection == market.DIR_SHORT)
```

## 3. Change the four drawing conditions in structure creation

Use `showBullInventory` for bullish IMB/OB boxes and `showBearInventory` for bearish IMB/OB boxes.

```pine
if armMoreExtreme(bullImb, candidate, market.DIR_LONG) and showBullInventory
...
if armMoreExtreme(bearImb, candidate, market.DIR_SHORT) and showBearInventory
...
if armMoreExtreme(bullOb, obSeed, market.DIR_LONG) and showBullInventory
...
if armMoreExtreme(bearOb, obSeed, market.DIR_SHORT) and showBearInventory
```

For the Post-OB IMB box use:

```pine
bool showPostObInventory = showStructureBoxes and (
     fpiEvent.direction == structuralDirection or
     phase == PHASE_JUDAS and fpiEvent.direction == judasDirection)
if armMoreExtreme(postObImb, candidate, fpiEvent.direction) and showPostObInventory
```

## 4. Replace the five structure-signal declarations

Replace:

```pine
bullObSignal = enablePrimaryOb ? updateRetest(bullOb, market.FAMILY_PRIMARY_OB, "OB-BULL-02", "PRIMARY_BULL_OB_RETEST") : market.newSignal()
bearObSignal = enablePrimaryOb ? updateRetest(bearOb, market.FAMILY_PRIMARY_OB, "OB-BEAR-02", "PRIMARY_BEAR_OB_RETEST") : market.newSignal()
bullImbSignal = enableGenericImb ? updateRetest(bullImb, market.FAMILY_IMB_RETEST, "IMB-BULL-02", "BULL_IMB_RETEST") : market.newSignal()
bearImbSignal = enableGenericImb ? updateRetest(bearImb, market.FAMILY_IMB_RETEST, "IMB-BEAR-02", "BEAR_IMB_RETEST") : market.newSignal()
postObSignal = enablePostObImb ? updateRetest(postObImb, market.FAMILY_POST_OB_IMB, "POSTOB-02", "POST_OB_IMB_RETEST") : market.newSignal()
```

with:

```pine
bullObSignal = enablePrimaryOb and bullCanConfirm ? updateRetest(bullOb, market.FAMILY_PRIMARY_OB, "OB-BULL-02", "PRIMARY_BULL_OB_RETEST") : market.newSignal()
bearObSignal = enablePrimaryOb and bearCanConfirm ? updateRetest(bearOb, market.FAMILY_PRIMARY_OB, "OB-BEAR-02", "PRIMARY_BEAR_OB_RETEST") : market.newSignal()
bullImbSignal = enableGenericImb and bullCanConfirm ? updateRetest(bullImb, market.FAMILY_IMB_RETEST, "IMB-BULL-02", "BULL_IMB_RETEST") : market.newSignal()
bearImbSignal = enableGenericImb and bearCanConfirm ? updateRetest(bearImb, market.FAMILY_IMB_RETEST, "IMB-BEAR-02", "BEAR_IMB_RETEST") : market.newSignal()
bool postObCanConfirm = postObImb.active and (
     postObImb.direction == structuralDirection or
     allowPostDisrespectJudasEntries and phase == PHASE_JUDAS and postObImb.direction == judasDirection)
postObSignal = enablePostObImb and postObCanConfirm ? updateRetest(postObImb, market.FAMILY_POST_OB_IMB, "POSTOB-02", "POST_OB_IMB_RETEST") : market.newSignal()
```

## 5. Gate BGOB confirmation, not BGOB tracking

Inside the BGOB loop, immediately after `bool confirms = ...`, add:

```pine
bool bgobCanConfirm = direction == structuralDirection or
     allowPostDisrespectJudasEntries and phase == PHASE_JUDAS and direction == judasDirection
```

Change:

```pine
else if retest and confirms
```

to:

```pine
else if retest and confirms and bgobCanConfirm
```

This keeps opposite BGOBs dormant before disrespect and allows a fresh retest/confirm after disrespect.

## 6. Do not redeclare `judasDirection` in Selection

Delete the second occurrence of:

```pine
int judasDirection = structuralDirection == market.DIR_NONE ? market.DIR_NONE : -structuralDirection
```

Keep:

```pine
int permittedDirection = phase == PHASE_JUDAS and not judasCompleted ? judasDirection : structuralDirection
```

## 7. Label post-disrespect entries clearly

Immediately after `permittedSignal = ...`, add:

```pine
if permittedSignal.valid and phase == PHASE_JUDAS and permittedSignal.direction == judasDirection
    permittedSignal.ruleId := "JUDAS-" + permittedSignal.ruleId
    permittedSignal.reason := "SESSION_FPI_DISRESPECT_POST_RETEST_CONFIRM"
```

Expected behavior for a bullish Session FPI:

```text
Bullish Session FPI
→ completed close below FPI
→ structural bias remains bullish
→ tactical phase becomes bearish Judas
→ highest stored bearish OB/IMB/BGOB waits for a fresh post-disrespect retest
→ bearish close confirms
→ JUDAS-... SELL
→ hold until later-window bullish reversal foundation confirms
```
