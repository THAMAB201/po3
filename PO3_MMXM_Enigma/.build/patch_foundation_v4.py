from pathlib import Path

root = Path(__file__).resolve().parents[1]
engine = root / "PO3_MMXM_Enigma_Execution_Engine.pine"
strategy = root / "PO3_MMXM_Enigma_Strategy.pine"
text = engine.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)

replace_once(
    "// @description Compact PO3 MMXM Enigma execution coordinator. Reuses the proven version-2 engine and adds the post-OB lowest/highest IMB first-retest entry path without exceeding Pine's main-body compilation limit.",
    "// @description Compact PO3 MMXM Enigma execution coordinator. Reuses the version-2 engine and adds local OB-retest plus post-OB directional IMB first-retest entries across every catalog state without exceeding Pine's main-body compilation limit.",
    "description",
)

replace_once(
    "    var int bullishObConfirmBar = na\n\n    var bool bearishRunActive = false",
    "    var int bullishObConfirmBar = na\n    var bool bullishObRetested = false\n\n    var bool bearishRunActive = false",
    "bullish OB retest state",
)
replace_once(
    "    var int bearishObConfirmBar = na\n\n    var bool bullishImbFound = false",
    "    var int bearishObConfirmBar = na\n    var bool bearishObRetested = false\n\n    var bool bullishImbFound = false",
    "bearish OB retest state",
)
replace_once(
    "        bullishObConfirmBar := na\n        bullishImbFound := false",
    "        bullishObConfirmBar := na\n        bullishObRetested := false\n        bullishImbFound := false",
    "reset bullish OB retest",
)
replace_once(
    "        bearishObConfirmBar := na\n        bearishImbFound := false",
    "        bearishObConfirmBar := na\n        bearishObRetested := false\n        bearishImbFound := false",
    "reset bearish OB retest",
)

replace_once(
    "        // A bullish OB is the lowest completed run of consecutive down-close candles.",
    "        // Every newly completed down-close run can become the active local bullish OB.",
    "bullish OB comment",
)
replace_once(
    "        else if bullishRunActive\n            bool replaceBullishCandidate = not bullishCandidateFound or bullishRunBottom < bullishCandidateBottom\n            if replaceBullishCandidate\n                bullishCandidateFound := true\n                bullishCandidateTop := bullishRunTop\n                bullishCandidateBottom := bullishRunBottom\n                bullishCandidateEndBar := bullishRunEndBar\n            bullishRunActive := false",
    "        else if bullishRunActive\n            bullishCandidateFound := true\n            bullishCandidateTop := bullishRunTop\n            bullishCandidateBottom := bullishRunBottom\n            bullishCandidateEndBar := bullishRunEndBar\n            bullishRunActive := false",
    "use latest bullish OB candidate",
)
replace_once(
    "        // A bearish OB is the highest completed run of consecutive up-close candles.",
    "        // Every newly completed up-close run can become the active local bearish OB.",
    "bearish OB comment",
)
replace_once(
    "        else if bearishRunActive\n            bool replaceBearishCandidate = not bearishCandidateFound or bearishRunTop > bearishCandidateTop\n            if replaceBearishCandidate\n                bearishCandidateFound := true\n                bearishCandidateTop := bearishRunTop\n                bearishCandidateBottom := bearishRunBottom\n                bearishCandidateEndBar := bearishRunEndBar\n            bearishRunActive := false",
    "        else if bearishRunActive\n            bearishCandidateFound := true\n            bearishCandidateTop := bearishRunTop\n            bearishCandidateBottom := bearishRunBottom\n            bearishCandidateEndBar := bearishRunEndBar\n            bearishRunActive := false",
    "use latest bearish OB candidate",
)

replace_once(
    "            bullishObConfirmBar := bar_index\n            bullishImbFound := false",
    "            bullishObConfirmBar := bar_index\n            bullishObRetested := false\n            bullishImbFound := false",
    "clear bullish retest on new OB",
)
replace_once(
    "            bearishObConfirmBar := bar_index\n            bearishImbFound := false",
    "            bearishObConfirmBar := bar_index\n            bearishObRetested := false\n            bearishImbFound := false",
    "clear bearish retest on new OB",
)

replace_once(
    "        // The displacement candle that validates the OB may also form the first eligible\n        // imbalance, so formation on the confirmation bar is intentionally allowed.\n        if imbalanceDir != 0 and bullishObConfirmed and not na(bullishObConfirmBar) and bar_index >= bullishObConfirmBar",
    "        bool bullishObRetestNow = bullishObConfirmed and not bullishObRetested and bar_index > bullishObConfirmBar and low <= bullishObTop and high >= bullishObBottom and close > bullishObTop\n        if bullishObRetestNow\n            bullishObRetested := true\n\n        bool bearishObRetestNow = bearishObConfirmed and not bearishObRetested and bar_index > bearishObConfirmBar and high >= bearishObBottom and low <= bearishObTop and close < bearishObBottom\n        if bearishObRetestNow\n            bearishObRetested := true\n\n        // After the local OB has validated and successfully retested, retain the lowest\n        // bullish IMB or highest bearish IMB created afterward.\n        if imbalanceDir == 1 and bullishObConfirmed and bullishObRetested and not na(bullishObConfirmBar) and bar_index > bullishObConfirmBar",
    "OB retest and bullish IMB arming",
)
replace_once(
    "        if imbalanceDir != 0 and bearishObConfirmed and not na(bearishObConfirmBar) and bar_index >= bearishObConfirmBar",
    "        if imbalanceDir == -1 and bearishObConfirmed and bearishObRetested and not na(bearishObConfirmBar) and bar_index > bearishObConfirmBar",
    "bearish directional IMB arming",
)

replace_once(
    "        float phaseMidpoint = not na(phaseHigh) and not na(phaseLow) ? (phaseHigh + phaseLow) * 0.5 : close\n        bool bullishLocationAllowed = not cfg.enforcePremiumDiscountEntries or close <= phaseMidpoint\n        bool bearishLocationAllowed = not cfg.enforcePremiumDiscountEntries or close >= phaseMidpoint\n\n",
    "",
    "remove premium-discount block",
)
replace_once(
    "        bool bullishComponentsRespected = bullishObConfirmed and close >= bullishObBottom and (bullishImbDirection == -1 or close >= bullishImbBottom)\n        float bullishExtension = bullishObConfirmed ? math.max(0.0, close - bullishObTop) : 1000000.0\n        bool bullishNotChased = bullishExtension <= cfg.maximumEarlyFoundationExtensionPoints\n        bool bullishControllerAligned = controllerFound and controllerDirection == 1\n        bool bullishRetestNow = bullishImbFound and not bullishImbUsed and bar_index > bullishImbFormationBar and bullishZoneOverlap and bullishOutsideClose\n\n        if cfg.allowControllerAlignedFoundationEntry and bullishControllerAligned and bullishRetestNow and bullishComponentsRespected and bullishLocationAllowed and bullishNotChased",
    "        bool bullishComponentsRespected = bullishObConfirmed and bullishObRetested and close >= bullishObBottom and close >= bullishImbBottom\n        bool bullishControllerAligned = controllerFound and controllerDirection == 1\n        bool bullishDirectionEnabled = bullishControllerAligned ? cfg.allowControllerAlignedFoundationEntry : cfg.allowEarlyCounterControllerFoundationEntry\n        bool bullishRetestNow = bullishImbFound and not bullishImbUsed and bar_index > bullishImbFormationBar and bullishZoneOverlap and bullishOutsideClose\n\n        if bullishDirectionEnabled and bullishRetestNow and bullishComponentsRespected",
    "bullish entry across catalog states",
)
replace_once(
    "        bool bearishComponentsRespected = bearishObConfirmed and close <= bearishObTop and (bearishImbDirection == 1 or close <= bearishImbTop)\n        float bearishExtension = bearishObConfirmed ? math.max(0.0, bearishObBottom - close) : 1000000.0\n        bool bearishNotChased = bearishExtension <= cfg.maximumEarlyFoundationExtensionPoints\n        bool bearishControllerAligned = controllerFound and controllerDirection == -1\n        bool bearishRetestNow = bearishImbFound and not bearishImbUsed and bar_index > bearishImbFormationBar and bearishZoneOverlap and bearishOutsideClose\n\n        if cfg.allowControllerAlignedFoundationEntry and bearishControllerAligned and bearishRetestNow and bearishComponentsRespected and bearishLocationAllowed and bearishNotChased",
    "        bool bearishComponentsRespected = bearishObConfirmed and bearishObRetested and close <= bearishObTop and close <= bearishImbTop\n        bool bearishControllerAligned = controllerFound and controllerDirection == -1\n        bool bearishDirectionEnabled = bearishControllerAligned ? cfg.allowControllerAlignedFoundationEntry : cfg.allowEarlyCounterControllerFoundationEntry\n        bool bearishRetestNow = bearishImbFound and not bearishImbUsed and bar_index > bearishImbFormationBar and bearishZoneOverlap and bearishOutsideClose\n\n        if bearishDirectionEnabled and bearishRetestNow and bearishComponentsRespected",
    "bearish entry across catalog states",
)

for forbidden in (
    "bullishLocationAllowed",
    "bearishLocationAllowed",
    "bullishNotChased",
    "bearishNotChased",
    "replaceBullishCandidate",
    "replaceBearishCandidate",
):
    if forbidden in text:
        raise RuntimeError(f"Legacy gate remains: {forbidden}")

for required in (
    "bullishObRetested",
    "bearishObRetested",
    "bullishDirectionEnabled",
    "bearishDirectionEnabled",
    "imbalanceDir == 1",
    "imbalanceDir == -1",
):
    if required not in text:
        raise RuntimeError(f"Required logic missing: {required}")

engine.write_text(text, encoding="utf-8")

strategy_text = strategy.read_text(encoding="utf-8")
if "PO3MMXMEnigmaExecutionEngine/3" not in strategy_text:
    raise RuntimeError("Strategy is not currently importing engine /3")
strategy_text = strategy_text.replace("PO3MMXMEnigmaExecutionEngine/3", "PO3MMXMEnigmaExecutionEngine/4", 1)
strategy_text = strategy_text.replace("version 3", "version 4", 1)
strategy.write_text(strategy_text, encoding="utf-8")

print("Patched execution engine and strategy for version 4")
