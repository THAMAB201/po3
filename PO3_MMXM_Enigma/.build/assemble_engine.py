from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parent / "PO3_MMXM_Enigma_Execution_Engine.pine"
PARTS = [ROOT / f"engine.part{i:02d}" for i in range(1, 10)]

for part in PARTS:
    if not part.exists():
        raise FileNotFoundError(f"Missing engine source part: {part}")

text = "".join(part.read_text(encoding="utf-8") for part in PARTS)


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    "// @description PO3 MMXM Enigma 1.8 full execution engine with a separate 1,008-case catalog audit resolver. Catalog gating is optional and disabled by default.\n"
    "library(\"PO3MMXMEnigmaLib18\", overlay = true, dynamic_requests = true)\n\n"
    "// Keep the proven 1.5 series-OB / inverse-IMB and management engine on its immutable /1 path.\n"
    "import SunovaBeach/PO3MMXMEnigmaLib15/1 as enigmaCore\n"
    "// Publish MMXMCatalogResolver privately as version 1 before publishing this library.\n"
    "import SunovaBeach/MMXMCatalogResolver/1 as catalog\n",
    "// @description PO3 MMXM Enigma execution engine. Coordinates the state manager, validated 1,008-case catalog resolver, FPI/OB/IMB/BGOB logic, order execution, risk management, and chart visuals.\n"
    "library(\"PO3MMXMEnigmaExecutionEngine\", overlay = true, dynamic_requests = true)\n\n"
    "// Publish both dependency libraries privately as version 1 before publishing this engine.\n"
    "import SunovaBeach/PO3MMXMEnigmaStateManager/1 as stateManager\n"
    "import SunovaBeach/PO3MMXMEnigmaCatalogResolver/1 as catalog\n",
    "professional engine header",
)

text = text.replace("enigmaCore.", "stateManager.")

replace_once(
    "    int orderBlockSignalSourceBar = na\n    box orderBlockSignalBox = na\n",
    "    int orderBlockSignalSourceBar = na\n    int orderBlockSignalSourceWindow = -1\n    box orderBlockSignalBox = na\n",
    "order-block source-window declaration",
)
replace_once(
    "            orderBlockSignalSourceBar := obDecision.bullSignalEndBar\n            if drawStructureVisuals\n",
    "            orderBlockSignalSourceBar := obDecision.bullSignalEndBar\n            orderBlockSignalSourceWindow := windowIdFromTimestamp(obDecision.bullSignalStartTime)\n            if drawStructureVisuals\n",
    "bullish order-block source window",
)
replace_once(
    "            orderBlockSignalSourceBar := obDecision.bearSignalEndBar\n            if drawStructureVisuals\n",
    "            orderBlockSignalSourceBar := obDecision.bearSignalEndBar\n            orderBlockSignalSourceWindow := windowIdFromTimestamp(obDecision.bearSignalStartTime)\n            if drawStructureVisuals\n",
    "bearish order-block source window",
)

replace_once(
    "    bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow or openingConfluenceReleaseSignalNow\n    bool signalCameFromFailure = false\n",
    "    bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or macro950BgobSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow\n"
    "    bool effectiveCameFromIntervalFoundation = not priorRespectedFpiReversalSignalNow and not macro950BgobSignalNow and not reversalFoundationSignalNow and intervalFoundationSignalNow\n"
    "    bool signalCameFromFailure = false\n",
    "remove opening-release execution and identify interval source",
)

replace_once(
    "            else\n                strategy.entry(ORDER_ID, strategy.short, qty=cfg.orderQuantity, comment=\"SELL\")\n                sellEntryNow := true\n\n            recordedTradeOpen := true\n",
    "            else\n                strategy.entry(ORDER_ID, strategy.short, qty=cfg.orderQuantity, comment=\"SELL\")\n                sellEntryNow := true\n\n"
    "            // Consume an interval foundation only after TradingView receives the actual order.\n"
    "            if effectiveCameFromIntervalFoundation and currentWindow >= 0\n"
    "                if effectiveDirection == 1\n"
    "                    array.set(intervalBullEntryUsed, currentWindow, true)\n"
    "                else if effectiveDirection == -1\n"
    "                    array.set(intervalBearEntryUsed, currentWindow, true)\n\n"
    "            recordedTradeOpen := true\n",
    "post-order interval consumption",
)

replace_once(
    "    var box sessionResultBox = na\n",
    "    var label sessionResultLabel = na\n",
    "session-result declaration",
)
replace_once(
    "        sessionClosedPoints := 0.0\n        sessionResultBox := na\n        confluenceStatusBox := na\n",
    "        sessionClosedPoints := 0.0\n"
    "        if not na(sessionResultLabel)\n"
    "            label.delete(sessionResultLabel)\n"
    "        sessionResultLabel := na\n"
    "        confluenceStatusBox := na\n",
    "session-result reset",
)

replace_once(
    "            float sessionResultsTop = drawConfluenceStatus ? confluenceBoxBottom - cfg.tradeTableGap : confluenceBoxTop\n"
    "            float sessionResultsBottom = sessionResultsTop - cfg.tradeTableHeight\n"
    "            if drawSessionResults\n"
    "                sessionResultBox := box.new(left=sessionResultsLeft, top=sessionResultsTop, right=sessionResultsRight, bottom=sessionResultsBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=resultColor(sessionClosedPoints), text=\"NY SESSION RESULTS\\n\" + signedPointsText(sessionClosedPoints), text_size=size.large, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)\n"
    "                float dailyLogTop = sessionResultsBottom - cfg.tradeTableGap\n"
    "                float dailyLogBottom = dailyLogTop - cfg.tradeTableHeight * 2.0\n"
    "                dailyTradeLogBox := box.new(left=sessionResultsLeft, top=dailyLogTop, right=sessionResultsRight, bottom=dailyLogBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=color.new(#212529, 8), text=dailyTradeLogText(ledger), text_size=size.normal, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)\n",
    "            if drawSessionResults\n"
    "                float initialSessionRange = math.max(sessionExtremeHigh - sessionExtremeLow, syminfo.mintick * 20.0)\n"
    "                float initialSessionResultY = sessionExtremeHigh + initialSessionRange * 0.04\n"
    "                sessionResultLabel := label.new(x=bar_index, y=initialSessionResultY, text=\"NY SESSION  |  LIVE\\nNET  0.00 PTS  •  0 TRADES\", yloc=yloc.price, style=label.style_label_down, color=resultColor(0.0), textcolor=color.white, size=size.small, textalign=text.align_center)\n"
    "                float dailyLogTop = drawConfluenceStatus ? confluenceBoxBottom - cfg.tradeTableGap : confluenceBoxTop - cfg.tradeTableGap\n"
    "                float dailyLogBottom = dailyLogTop - cfg.tradeTableHeight * 2.0\n"
    "                dailyTradeLogBox := box.new(left=sessionResultsLeft, top=dailyLogTop, right=sessionResultsRight, bottom=dailyLogBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=color.new(#212529, 8), text=dailyTradeLogText(ledger), text_size=size.normal, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)\n",
    "sleek session-result creation",
)

replace_once(
    "        if drawSessionResults and not na(sessionResultBox)\n"
    "            float sessionResultsTop = drawConfluenceStatus ? confluenceBoxBottom - cfg.tradeTableGap : confluenceBoxTop\n"
    "            float sessionResultsBottom = sessionResultsTop - cfg.tradeTableHeight\n"
    "            box.set_top(sessionResultBox, sessionResultsTop)\n"
    "            box.set_bottom(sessionResultBox, sessionResultsBottom)\n"
    "            box.set_text(sessionResultBox, \"NY SESSION RESULTS\\n\" + signedPointsText(sessionClosedPoints))\n"
    "            box.set_bgcolor(sessionResultBox, resultColor(sessionClosedPoints))\n"
    "            if not na(dailyTradeLogBox)\n"
    "                int totalDailyTrades = dailyTradeCount(ledger)\n"
    "                float dailyLogTop = sessionResultsBottom - cfg.tradeTableGap\n"
    "                float dailyLogHeight = cfg.tradeTableHeight * math.max(2.0, 1.0 + totalDailyTrades * 0.55)\n"
    "                box.set_top(dailyTradeLogBox, dailyLogTop)\n"
    "                box.set_bottom(dailyTradeLogBox, dailyLogTop - dailyLogHeight)\n"
    "                box.set_text(dailyTradeLogBox, dailyTradeLogText(ledger))\n",
    "        if drawSessionResults and not na(sessionResultLabel)\n"
    "            float openTradePoints = recordedTradeOpen and strategy.position_size != 0 ? tradePoints(recordedTradeDirection, recordedEntry, close) : 0.0\n"
    "            float sessionNetPoints = sessionClosedPoints + openTradePoints\n"
    "            int totalDailyTrades = dailyTradeCount(ledger)\n"
    "            string sessionState = inSession ? \"LIVE\" : \"FINAL\"\n"
    "            string sessionResultText = \"NY SESSION  |  \" + sessionState + \"\\nNET  \" + signedPointNumber(sessionNetPoints) + \" PTS  •  \" + str.tostring(totalDailyTrades) + \" TRADES\"\n"
    "            float liveSessionRange = math.max(sessionExtremeHigh - sessionExtremeLow, syminfo.mintick * 20.0)\n"
    "            float liveSessionResultY = sessionExtremeHigh + liveSessionRange * 0.04\n"
    "            label.set_x(sessionResultLabel, bar_index)\n"
    "            label.set_y(sessionResultLabel, liveSessionResultY)\n"
    "            label.set_text(sessionResultLabel, sessionResultText)\n"
    "            label.set_color(sessionResultLabel, resultColor(sessionNetPoints))\n"
    "        if drawSessionResults and not na(dailyTradeLogBox)\n"
    "            int totalDailyTradesForLog = dailyTradeCount(ledger)\n"
    "            float dailyLogTop = drawConfluenceStatus ? confluenceBoxBottom - cfg.tradeTableGap : confluenceBoxTop - cfg.tradeTableGap\n"
    "            float dailyLogHeight = cfg.tradeTableHeight * math.max(2.0, 1.0 + totalDailyTradesForLog * 0.55)\n"
    "            box.set_top(dailyTradeLogBox, dailyLogTop)\n"
    "            box.set_bottom(dailyTradeLogBox, dailyLogTop - dailyLogHeight)\n"
    "            box.set_text(dailyTradeLogBox, dailyTradeLogText(ledger))\n",
    "live/final session-result update",
)

for forbidden in (
    "PO3MMXMEnigmaLib18",
    "PO3MMXMEnigmaLib15",
    "SunovaBeach/MMXMCatalogResolver/",
    "enigmaCore.",
    "sessionResultBox",
):
    if forbidden in text:
        raise RuntimeError(f"Forbidden legacy token remains: {forbidden}")

required = (
    'library("PO3MMXMEnigmaExecutionEngine"',
    "SunovaBeach/PO3MMXMEnigmaStateManager/1",
    "SunovaBeach/PO3MMXMEnigmaCatalogResolver/1",
    "orderBlockSignalSourceWindow",
    "intervalFpiRespectConfirmed",
    "currentIntervalObSignal",
    "currentIntervalBgobSignal",
    "effectiveCameFromIntervalFoundation",
    "sessionResultLabel",
    "NY SESSION  |  LIVE",
)
for token in required:
    if token not in text:
        raise RuntimeError(f"Required corrected token missing: {token}")

raw_line = next(line for line in text.splitlines() if "bool rawEffectiveSignalNow" in line)
if "openingConfluenceReleaseSignalNow" in raw_line:
    raise RuntimeError("Opening confluence release still reaches the execution signal")

TARGET.write_text(text, encoding="utf-8")
print(f"Wrote {TARGET} ({len(text.splitlines())} lines)")
