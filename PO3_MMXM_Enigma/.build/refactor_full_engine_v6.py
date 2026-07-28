from pathlib import Path

root = Path(__file__).resolve().parents[1]
engine_path = root / "PO3_MMXM_Enigma_Execution_Engine.pine"
strategy_path = root / "PO3_MMXM_Enigma_Strategy.pine"
text = engine_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    text = text.replace(old, new, 1)


if 'import SunovaBeach/PO3MMXMEnigmaExecutionEngine/2 as baseEngine' in text:
    raise RuntimeError("Compact wrapper detected; full source was not assembled")
if len(text.splitlines()) < 3000:
    raise RuntimeError(f"Full engine unexpectedly short: {len(text.splitlines())} lines")

replace_once(
    "import SunovaBeach/PO3MMXMEnigmaCatalogResolver/1 as catalog\n",
    "import SunovaBeach/PO3MMXMEnigmaCatalogResolver/1 as catalog\n"
    "// Dedicated structural foundation signals; this library never places orders.\n"
    "import SunovaBeach/PO3MMXMEnigmaFoundationEngine/1 as foundation\n",
    "foundation import",
)

# Move the large multi-timeframe visual reconstruction out of run(). The helper
# keeps identical state and drawing code, but removes hundreds of statements from
# the exported execution body that triggered CE10295.
decl_start_marker = "    // Higher-chart visual reconstruction state. Execution remains strictly one-minute;\n"
decl_end_marker = "    var float mtfPrevious1Close = na\n"
decl_start = text.find(decl_start_marker)
if decl_start < 0:
    raise RuntimeError("MTF declaration start not found")
decl_end = text.find(decl_end_marker, decl_start)
if decl_end < 0:
    raise RuntimeError("MTF declaration end not found")
decl_end += len(decl_end_marker)
mtf_declarations = text[decl_start:decl_end]
text = text[:decl_start] + text[decl_end:]

visual_start_marker = "    // Reconstruct the one-minute FPI drawings when the chart itself is 2-15 minutes.\n"
visual_end_marker = "    if sessionStart\n"
visual_start = text.find(visual_start_marker)
if visual_start < 0:
    raise RuntimeError("MTF visual block start not found")
visual_end = text.find(visual_end_marker, visual_start)
if visual_end < 0:
    raise RuntimeError("MTF visual block end not found")
mtf_visual_block = text[visual_start:visual_end]
text = text[:visual_start] + "    renderMtfVisuals(cfg, isHigherVisualTimeframe, isSubMinuteVisualTimeframe, drawStructureVisuals, drawStructureTags)\n\n" + text[visual_end:]

run_marker = "export run(EnigmaConfig cfg) =>\n"
run_index = text.find(run_marker)
if run_index < 0:
    raise RuntimeError("run() definition not found")
helper = (
    "renderMtfVisuals(EnigmaConfig cfg, bool isHigherVisualTimeframe, bool isSubMinuteVisualTimeframe, bool drawStructureVisuals, bool drawStructureTags) =>\n"
    + mtf_declarations
    + "\n"
    + mtf_visual_block
    + "    0\n\n\n"
)
text = text[:run_index] + helper + text[run_index:]

foundation_call = (
    "    foundation.FoundationSignal externalFoundationSignal = foundation.step(\n"
    "        cfg.enableBot and cfg.enableSequenceEngine and isOneMinute,\n"
    "        inSession,\n"
    "        sessionStart,\n"
    "        sessionAnchorFpiFound ? sessionAnchorDirection : 0\n"
    "    )\n"
    "    bool externalFoundationSignalNow = externalFoundationSignal.enterNow\n\n"
)
replace_once(
    "    // Resolve the one effective structural signal for this bar.\n",
    foundation_call + "    // Resolve the one effective structural signal for this bar.\n",
    "foundation signal call",
)

replace_once(
    "    bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow\n",
    "    bool rawEffectiveSignalNow = externalFoundationSignalNow or priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow\n",
    "raw effective signal",
)
replace_once(
    "    bool effectiveCameFromIntervalFoundation = not priorRespectedFpiReversalSignalNow and not macro950BgobSignalNow and not reversalFoundationSignalNow and intervalFoundationSignalNow\n",
    "    bool effectiveCameFromIntervalFoundation = not externalFoundationSignalNow and not priorRespectedFpiReversalSignalNow and not macro950BgobSignalNow and not reversalFoundationSignalNow and intervalFoundationSignalNow\n",
    "interval source identity",
)
replace_once(
    "    int effectiveDirection = priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalDirection : macro950BgobSignalNow ? macro950BgobSignalDirection : reversalFoundationSignalNow ? reversalFoundationSignalDirection : intervalFoundationSignalNow ? intervalFoundationSignalDirection : sessionAnchorDirection\n",
    "    int effectiveDirection = externalFoundationSignalNow ? externalFoundationSignal.direction : priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalDirection : macro950BgobSignalNow ? macro950BgobSignalDirection : reversalFoundationSignalNow ? reversalFoundationSignalDirection : intervalFoundationSignalNow ? intervalFoundationSignalDirection : sessionAnchorDirection\n",
    "effective direction",
)
replace_once(
    "    float effectiveTop = priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalTop : macro950BgobSignalNow ? macro950BgobSignalTop : reversalFoundationSignalNow ? reversalFoundationSignalTop : intervalFoundationSignalNow ? intervalFoundationSignalTop : sessionConfluenceMasterTop\n",
    "    float effectiveTop = externalFoundationSignalNow ? externalFoundationSignal.zoneTop : priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalTop : macro950BgobSignalNow ? macro950BgobSignalTop : reversalFoundationSignalNow ? reversalFoundationSignalTop : intervalFoundationSignalNow ? intervalFoundationSignalTop : sessionConfluenceMasterTop\n",
    "effective top",
)
replace_once(
    "    float effectiveBottom = priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalBottom : macro950BgobSignalNow ? macro950BgobSignalBottom : reversalFoundationSignalNow ? reversalFoundationSignalBottom : intervalFoundationSignalNow ? intervalFoundationSignalBottom : sessionConfluenceMasterBottom\n",
    "    float effectiveBottom = externalFoundationSignalNow ? externalFoundationSignal.zoneBottom : priorRespectedFpiReversalSignalNow ? priorRespectedFpiReversalBottom : macro950BgobSignalNow ? macro950BgobSignalBottom : reversalFoundationSignalNow ? reversalFoundationSignalBottom : intervalFoundationSignalNow ? intervalFoundationSignalBottom : sessionConfluenceMasterBottom\n",
    "effective bottom",
)
replace_once(
    "    float effectiveSl = macro950BgobSignalNow ? macroBgobMidpointStop : reversalFoundationSignalNow ? (effectiveDirection == 1 ? effectiveBottom : effectiveTop) : effectiveDirection == 1 ? intervalThreeCandleLow : intervalThreeCandleHigh\n",
    "    float effectiveSl = externalFoundationSignalNow ? externalFoundationSignal.stopPrice : macro950BgobSignalNow ? macroBgobMidpointStop : reversalFoundationSignalNow ? (effectiveDirection == 1 ? effectiveBottom : effectiveTop) : effectiveDirection == 1 ? intervalThreeCandleLow : intervalThreeCandleHigh\n",
    "effective stop",
)
replace_once(
    "    int effectiveWindow = priorRespectedFpiReversalSignalNow ? currentWindow : reversalFoundationSignalNow ? reversalFoundationSignalWindow : currentWindow\n",
    "    int effectiveWindow = externalFoundationSignalNow ? currentWindow : priorRespectedFpiReversalSignalNow ? currentWindow : reversalFoundationSignalNow ? reversalFoundationSignalWindow : currentWindow\n",
    "effective window",
)
replace_once(
    "    int effectiveSourceKind = priorRespectedFpiReversalSignalNow ? SOURCE_PRIOR_FPI_RETEST : macro950BgobSignalNow ? SOURCE_BGOB : reversalFoundationSignalNow ? SOURCE_REVERSAL_FOUNDATION : intervalFoundationSignalNow ? intervalFoundationSignalKind : sessionConfluenceMasterKind\n",
    "    int effectiveSourceKind = externalFoundationSignalNow ? (externalFoundationSignal.sourceKind == 1 ? SOURCE_ORDER_BLOCK : SOURCE_REVERSAL_FOUNDATION) : priorRespectedFpiReversalSignalNow ? SOURCE_PRIOR_FPI_RETEST : macro950BgobSignalNow ? SOURCE_BGOB : reversalFoundationSignalNow ? SOURCE_REVERSAL_FOUNDATION : intervalFoundationSignalNow ? intervalFoundationSignalKind : sessionConfluenceMasterKind\n",
    "effective source",
)
replace_once(
    "    bool effectiveInitialRetest = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or not reversalFoundationSignalNow\n",
    "    bool effectiveInitialRetest = externalFoundationSignalNow or priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or not reversalFoundationSignalNow\n",
    "effective initial retest",
)
replace_once(
    "    bool effectiveCounterToController = sessionAnchorFpiFound and effectiveDirection != sessionAnchorDirection\n",
    "    bool effectiveCounterToController = sessionAnchorFpiFound and effectiveDirection != sessionAnchorDirection\n"
    "    bool externalFoundationAuthority = externalFoundationSignalNow and sessionAnchorFpiFound and effectiveDirection == sessionAnchorDirection\n",
    "foundation authority",
)

replace_once(
    "    bool catalogDirectionAllowed = not cfg.enforceCatalogGate or not catalogAvailable or (effectiveDirection == 1 ? catalogDecision.terminalAction == catalog.ACTION_BUY_ELIGIBLE : effectiveDirection == -1 ? catalogDecision.terminalAction == catalog.ACTION_SELL_ELIGIBLE : true)\n",
    "    bool catalogDirectionAllowed = externalFoundationAuthority or not cfg.enforceCatalogGate or not catalogAvailable or (effectiveDirection == 1 ? catalogDecision.terminalAction == catalog.ACTION_BUY_ELIGIBLE : effectiveDirection == -1 ? catalogDecision.terminalAction == catalog.ACTION_SELL_ELIGIBLE : true)\n",
    "catalog permission",
)
replace_once(
    "    bool effectiveDirectionAllowedByMacro950 = priorRespectedFpiReversalSignalNow ? true : macro950BgobSignalNow ? true : earlyCounterControllerFoundationSignal ? true : macroExpectedFoundationSignal ? true : sequenceAlignedEarlyPermission ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : effectiveMacroDirectionMatches and effectiveMacroTransitionConfirmed\n",
    "    bool effectiveDirectionAllowedByMacro950 = externalFoundationAuthority ? true : priorRespectedFpiReversalSignalNow ? true : macro950BgobSignalNow ? true : earlyCounterControllerFoundationSignal ? true : macroExpectedFoundationSignal ? true : sequenceAlignedEarlyPermission ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : effectiveMacroDirectionMatches and effectiveMacroTransitionConfirmed\n",
    "macro permission",
)
replace_once(
    "    bool effectiveDirectionAllowedBySession = priorRespectedFpiReversalSignalNow ? true : macro950BgobSignalNow ? true : earlyCounterControllerFoundationSignal ? true : macroExpectedFoundationSignal ? true : sequenceAlignedEarlyPermission ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : not sessionAnchorFpiFound or effectiveDirection == sessionAnchorDirection or counterSessionBeyondAnchor\n",
    "    bool effectiveDirectionAllowedBySession = externalFoundationAuthority ? true : priorRespectedFpiReversalSignalNow ? true : macro950BgobSignalNow ? true : earlyCounterControllerFoundationSignal ? true : macroExpectedFoundationSignal ? true : sequenceAlignedEarlyPermission ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : not sessionAnchorFpiFound or effectiveDirection == sessionAnchorDirection or counterSessionBeyondAnchor\n",
    "session permission",
)
replace_once(
    "    bool effectiveDirectionAllowedByConfluence = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or (reversalModeActive ? effectiveDirection == reversalModeDirection : intervalFoundationSignalNow or not sessionConfluenceBiasActive or effectiveDirection == sessionAnchorDirection)\n",
    "    bool effectiveDirectionAllowedByConfluence = externalFoundationAuthority or priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or (reversalModeActive ? effectiveDirection == reversalModeDirection : intervalFoundationSignalNow or not sessionConfluenceBiasActive or effectiveDirection == sessionAnchorDirection)\n",
    "confluence permission",
)
replace_once(
    "    bool campaignSignalCompatible = priorRespectedFpiReversalSignalNow or qualifiedEarlyFoundationAuthority or not campaignHoldActive or effectiveDirection == recordedTradeDirection\n",
    "    bool campaignSignalCompatible = externalFoundationAuthority or priorRespectedFpiReversalSignalNow or qualifiedEarlyFoundationAuthority or not campaignHoldActive or effectiveDirection == recordedTradeDirection\n",
    "campaign compatibility",
)
replace_once(
    "    bool intervalAuthoritySignalCompatible = priorRespectedFpiReversalSignalNow or qualifiedEarlyFoundationAuthority or not priorIntervalHoldActive or effectiveDirection == recordedTradeDirection\n",
    "    bool intervalAuthoritySignalCompatible = externalFoundationAuthority or priorRespectedFpiReversalSignalNow or qualifiedEarlyFoundationAuthority or not priorIntervalHoldActive or effectiveDirection == recordedTradeDirection\n",
    "interval compatibility",
)
replace_once(
    "    bool campaignReentryDirectionCompatible = priorRespectedFpiReversalSignalNow ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : not campaignReentryAlignedOnly or effectiveDirection == sessionAnchorDirection\n",
    "    bool campaignReentryDirectionCompatible = externalFoundationAuthority ? true : priorRespectedFpiReversalSignalNow ? true : reversalModeActive ? effectiveDirection == reversalModeDirection : not campaignReentryAlignedOnly or effectiveDirection == sessionAnchorDirection\n",
    "reentry compatibility",
)
replace_once(
    "    bool reversalModeWindowSupports = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or not reversalModeActive or (currentWindow >= 0 and array.get(selectedByWindow, currentWindow) and array.get(intervalFpiOriginalDirection, currentWindow) == reversalModeDirection)\n",
    "    bool reversalModeWindowSupports = externalFoundationAuthority or priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or not reversalModeActive or (currentWindow >= 0 and array.get(selectedByWindow, currentWindow) and array.get(intervalFpiOriginalDirection, currentWindow) == reversalModeDirection)\n",
    "reversal-mode compatibility",
)
replace_once(
    "    bool standardSignalLocksClear = (authoritativeMacroStructureSignal or qualifiedEarlyFoundationAuthority or ordinaryWaitLocksClear) and not mandatoryStructureExitNow and not targetWindowLock and not openingFpiWindowLock and not enigmaBlocksEffectiveDirection\n",
    "    bool standardSignalLocksClear = (authoritativeMacroStructureSignal or qualifiedEarlyFoundationAuthority or ordinaryWaitLocksClear) and not mandatoryStructureExitNow and not targetWindowLock and not openingFpiWindowLock and not enigmaBlocksEffectiveDirection\n"
    "    bool externalFoundationLocksClear = not mandatoryStructureExitNow and not targetWindowLock and not enigmaBlocksEffectiveDirection\n",
    "foundation execution locks",
)
replace_once(
    "    bool effectiveDirectionAllowedByLocation = not cfg.enforcePremiumDiscountEntries or na(activeDealingRangeEquilibrium) or (effectiveDirection == 1 ? effectiveLocationReference <= activeDealingRangeEquilibrium : effectiveLocationReference >= activeDealingRangeEquilibrium)\n",
    "    bool effectiveDirectionAllowedByLocation = externalFoundationAuthority or not cfg.enforcePremiumDiscountEntries or na(activeDealingRangeEquilibrium) or (effectiveDirection == 1 ? effectiveLocationReference <= activeDealingRangeEquilibrium : effectiveLocationReference >= activeDealingRangeEquilibrium)\n",
    "location permission",
)
replace_once(
    "    bool effectiveSignalNow = rawEffectiveSignalNow and (priorRespectedFpiReversalSignalNow or standardSignalLocksClear) and reversalModeWindowSupports and campaignSignalCompatible and intervalAuthoritySignalCompatible and confirmedNarrativeSignalCompatible and campaignReentryDirectionCompatible and effectiveDirectionAllowedByMacro950 and effectiveDirectionAllowedBySession and effectiveDirectionAllowedByConfluence and effectiveDirectionAllowedByLocation and oppositeEffectiveSignalBodyConfirmed and catalogDirectionAllowed\n",
    "    bool effectiveSignalNow = rawEffectiveSignalNow and (externalFoundationAuthority ? externalFoundationLocksClear : (priorRespectedFpiReversalSignalNow or standardSignalLocksClear)) and reversalModeWindowSupports and campaignSignalCompatible and intervalAuthoritySignalCompatible and confirmedNarrativeSignalCompatible and campaignReentryDirectionCompatible and effectiveDirectionAllowedByMacro950 and effectiveDirectionAllowedBySession and effectiveDirectionAllowedByConfluence and effectiveDirectionAllowedByLocation and oppositeEffectiveSignalBodyConfirmed and catalogDirectionAllowed\n",
    "effective execution signal",
)

for required in (
    "PO3MMXMEnigmaFoundationEngine/1",
    "renderMtfVisuals(",
    "externalFoundationSignalNow",
    "externalFoundationAuthority",
    "externalFoundationLocksClear",
):
    if required not in text:
        raise RuntimeError(f"Required modular token missing: {required}")

if "baseEngine" in text or "PO3MMXMEnigmaExecutionEngine/2" in text:
    raise RuntimeError("Previous-version wrapper remains in full engine")
if len(text.splitlines()) < 3000:
    raise RuntimeError("Refactored full engine lost substantial source")

engine_path.write_text(text, encoding="utf-8")

strategy_text = strategy_path.read_text(encoding="utf-8")
for old_version in ("/5", "/4", "/3"):
    strategy_text = strategy_text.replace(f"PO3MMXMEnigmaExecutionEngine{old_version}", "PO3MMXMEnigmaExecutionEngine/6")
strategy_text = strategy_text.replace("version 5", "version 6").replace("version 4", "version 6").replace("version 3", "version 6")
if "PO3MMXMEnigmaExecutionEngine/6" not in strategy_text:
    raise RuntimeError("Strategy import was not updated to engine /6")
strategy_path.write_text(strategy_text, encoding="utf-8")

print(f"Wrote full modular engine: {len(text.splitlines())} lines")
