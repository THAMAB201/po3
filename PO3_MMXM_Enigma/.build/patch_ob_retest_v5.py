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
    "// @description Compact PO3 MMXM Enigma execution coordinator. Reuses the version-2 engine and adds local OB-retest plus post-OB directional IMB first-retest entries across every catalog state without exceeding Pine's main-body compilation limit.",
    "// @description Compact PO3 MMXM Enigma execution coordinator. Uses the first NY Session FPI as direction, enters directly on a confirmed local OB retest, and also supports later post-OB IMB retests across every catalog state.",
    "description",
)

replace_once(
    "    var int bullishObConfirmBar = na\n    var bool bullishObRetested = false\n",
    "    var int bullishObConfirmBar = na\n    var bool bullishObRetested = false\n    var bool bullishObUsed = false\n",
    "bullish OB used state",
)
replace_once(
    "    var int bearishObConfirmBar = na\n    var bool bearishObRetested = false\n",
    "    var int bearishObConfirmBar = na\n    var bool bearishObRetested = false\n    var bool bearishObUsed = false\n",
    "bearish OB used state",
)

replace_once(
    "    if sessionStart or phaseChanged\n        activePhase := currentPhase\n        controllerFound := false\n        controllerDirection := 0\n        phaseHigh := high\n",
    "    // The first FPI after 09:30 is the Session FPI and remains the controller all day.\n    if sessionStart\n        controllerFound := false\n        controllerDirection := 0\n\n    if sessionStart or phaseChanged\n        activePhase := currentPhase\n        phaseHigh := high\n",
    "preserve Session FPI across phases",
)

replace_once(
    "        bullishObConfirmBar := na\n        bullishObRetested := false\n        bullishImbFound := false\n",
    "        bullishObConfirmBar := na\n        bullishObRetested := false\n        bullishObUsed := false\n        bullishImbFound := false\n",
    "reset bullish OB used",
)
replace_once(
    "        bearishObConfirmBar := na\n        bearishObRetested := false\n        bearishImbFound := false\n",
    "        bearishObConfirmBar := na\n        bearishObRetested := false\n        bearishObUsed := false\n        bearishImbFound := false\n",
    "reset bearish OB used",
)

replace_once(
    "            bullishObConfirmBar := bar_index\n            bullishObRetested := false\n            bullishImbFound := false\n",
    "            bullishObConfirmBar := bar_index\n            bullishObRetested := false\n            bullishObUsed := false\n            bullishImbFound := false\n",
    "new bullish OB resets use",
)
replace_once(
    "            bearishObConfirmBar := bar_index\n            bearishObRetested := false\n            bearishImbFound := false\n",
    "            bearishObConfirmBar := bar_index\n            bearishObRetested := false\n            bearishObUsed := false\n            bearishImbFound := false\n",
    "new bearish OB resets use",
)

replace_once(
    "        bool bullishObRetestNow = bullishObConfirmed and not bullishObRetested and bar_index > bullishObConfirmBar and low <= bullishObTop and high >= bullishObBottom and close > bullishObTop\n        if bullishObRetestNow\n            bullishObRetested := true\n\n        bool bearishObRetestNow = bearishObConfirmed and not bearishObRetested and bar_index > bearishObConfirmBar and high >= bearishObBottom and low <= bearishObTop and close < bearishObBottom\n        if bearishObRetestNow\n            bearishObRetested := true\n",
    "        bool bullishFpiActive = controllerFound and controllerDirection == 1\n        bool bearishFpiActive = controllerFound and controllerDirection == -1\n\n        // Primary entry: Session FPI direction + confirmed local OB + first successful retest/close.\n        bool bullishObRetestNow = bullishObConfirmed and not bullishObRetested and bar_index > bullishObConfirmBar and low <= bullishObTop and high >= bullishObBottom and close > bullishObTop\n        if bullishObRetestNow\n            bullishObRetested := true\n            if bullishFpiActive and not bullishObUsed\n                bullishObUsed := true\n                buySignal := true\n                signalZoneTop := bullishObTop\n                signalZoneBottom := bullishObBottom\n                signalObTop := bullishObTop\n                signalObBottom := bullishObBottom\n                signalSourceBar := bullishObConfirmBar\n\n        bool bearishObRetestNow = bearishObConfirmed and not bearishObRetested and bar_index > bearishObConfirmBar and high >= bearishObBottom and low <= bearishObTop and close < bearishObBottom\n        if bearishObRetestNow\n            bearishObRetested := true\n            if bearishFpiActive and not bearishObUsed\n                bearishObUsed := true\n                sellSignal := true\n                signalZoneTop := bearishObTop\n                signalZoneBottom := bearishObBottom\n                signalObTop := bearishObTop\n                signalObBottom := bearishObBottom\n                signalSourceBar := bearishObConfirmBar\n",
    "direct OB retest entries",
)

replace_once(
    "        if bullishDirectionEnabled and bullishRetestNow and bullishComponentsRespected\n",
    "        if not buySignal and bullishDirectionEnabled and bullishRetestNow and bullishComponentsRespected\n",
    "OB entry takes priority over IMB buy",
)
replace_once(
    "        if bearishDirectionEnabled and bearishRetestNow and bearishComponentsRespected\n",
    "        if not sellSignal and bearishDirectionEnabled and bearishRetestNow and bearishComponentsRespected\n",
    "OB entry takes priority over IMB sell",
)

replace_once(
    'label.new(bar_index, low, "BUY\\nPOST-OB IMB", style = label.style_label_up, color = color.new(#198754, 0), textcolor = color.white, size = size.small)',
    'label.new(bar_index, low, "BUY\\nOB/IMB FOUNDATION", style = label.style_label_up, color = color.new(#198754, 0), textcolor = color.white, size = size.small)',
    "buy label",
)
replace_once(
    'label.new(bar_index, high, "SELL\\nPOST-OB IMB", style = label.style_label_down, color = color.new(#c92a2a, 0), textcolor = color.white, size = size.small)',
    'label.new(bar_index, high, "SELL\\nOB/IMB FOUNDATION", style = label.style_label_down, color = color.new(#c92a2a, 0), textcolor = color.white, size = size.small)',
    "sell label",
)

for required in (
    "bullishFpiActive",
    "bearishFpiActive",
    "bullishObUsed",
    "bearishObUsed",
    "Primary entry: Session FPI direction",
):
    if required not in text:
        raise RuntimeError(f"Required v5 logic missing: {required}")

engine.write_text(text, encoding="utf-8")

strategy_text = strategy.read_text(encoding="utf-8")
if "PO3MMXMEnigmaExecutionEngine/4" not in strategy_text:
    raise RuntimeError("Strategy is not importing engine /4")
strategy_text = strategy_text.replace("PO3MMXMEnigmaExecutionEngine/4", "PO3MMXMEnigmaExecutionEngine/5", 1)
strategy_text = strategy_text.replace("version 4", "version 5", 1)
strategy.write_text(strategy_text, encoding="utf-8")

print("Patched direct FPI-aligned OB retest entry and strategy version 5")
