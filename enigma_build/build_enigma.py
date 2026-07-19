from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "enigma_build"
PARTS = [
    "chunk_01.txt",
    "chunk_01b.txt",
    "chunk_02.txt",
    "chunk_03.txt",
    "chunk_04.txt",
    "chunk_05.txt",
    "chunk_06.txt",
    "chunk_07.txt",
    "chunk_08.txt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one regex match, found {count}")
    return updated


source = "\n".join((BUILD / part).read_text(encoding="utf-8").rstrip("\n") for part in PARTS) + "\n"

# Preserve the permanent TradingView library title. Only its publication revision changes.
if 'library("PO3MMXMEnigmaCore", overlay = true, dynamic_requests = true)' not in source:
    raise RuntimeError("Stable PO3MMXMEnigmaCore library declaration is missing")

# Track the actual interval that produced the validated series order block.
source = replace_once(
    source,
    "    int orderBlockSignalSourceBar = na\n    box orderBlockSignalBox = na",
    "    int orderBlockSignalSourceBar = na\n    int orderBlockSignalSourceWindow = -1\n    box orderBlockSignalBox = na",
    "add order-block source window state",
)
source = replace_once(
    source,
    "                        orderBlockSignalSourceBar := bullishObCandidateEndBar",
    "                        orderBlockSignalSourceBar := bullishObCandidateEndBar\n                        orderBlockSignalSourceWindow := windowIdFromTimestamp(bullishObCandidateStartTime)",
    "capture bullish order-block source window",
)
source = replace_once(
    source,
    "                        orderBlockSignalSourceBar := bearishObCandidateEndBar",
    "                        orderBlockSignalSourceBar := bearishObCandidateEndBar\n                        orderBlockSignalSourceWindow := windowIdFromTimestamp(bearishObCandidateStartTime)",
    "capture bearish order-block source window",
)
source = replace_once(
    source,
    "        if orderBlockSignalNow\n            if orderBlockSignalDirection == 1",
    "        if orderBlockSignalNow and orderBlockSignalSourceWindow == currentWindow\n            if orderBlockSignalDirection == 1",
    "restrict interval OB validation to its source interval",
)
source = replace_once(
    source,
    "addConfluence(confluenceKind, confluenceSourceBar, confluenceWindow, confluenceTop, confluenceBottom, confluenceBoundary, confluenceValid, confluenceStructureBox, SOURCE_ORDER_BLOCK, orderBlockSignalSourceBar, currentWindow, sessionAnchorDirection, orderBlockSignalTop, orderBlockSignalBottom, orderBlockSignalBox)",
    "addConfluence(confluenceKind, confluenceSourceBar, confluenceWindow, confluenceTop, confluenceBottom, confluenceBoundary, confluenceValid, confluenceStructureBox, SOURCE_ORDER_BLOCK, orderBlockSignalSourceBar, orderBlockSignalSourceWindow, sessionAnchorDirection, orderBlockSignalTop, orderBlockSignalBottom, orderBlockSignalBox)",
    "retain OB confluence under its true source interval",
)

old_interval_block = """        bool intervalIsDisrespected = array.get(intervalFpiDisrespected, currentWindow)
        bool rawStructureSignal = orderBlockSignalNow or bgobSignalNow
        int rawStructureDirection = orderBlockSignalNow ? orderBlockSignalDirection : bgobSignalDirection
        bool returnedToPreviousSessionFpi = false
        for previousWindow = phaseStartWindow(activeNyPhase) to LAST_WINDOW_ID
            if previousWindow < currentWindow and array.get(selectedByWindow, previousWindow)
                float previousTop = array.get(intervalFpiTop, previousWindow)
                float previousBottom = array.get(intervalFpiBottom, previousWindow)
                if not na(previousTop) and not na(previousBottom) and low <= previousTop and high >= previousBottom
                    returnedToPreviousSessionFpi := true

        bool newSessionHighBreakout = not na(sessionExtremeHigh) and close > sessionExtremeHigh
        bool newSessionLowBreakout = not na(sessionExtremeLow) and close < sessionExtremeLow
        bool bullishFpiStateAllows = reversalModeActive ? reversalModeDirection == 1 and intervalOriginalDirection == 1 : intervalOriginalDirection == 1 or (intervalIsDisrespected and intervalOriginalDirection == -1)
        bool bearishFpiStateAllows = reversalModeActive ? reversalModeDirection == -1 and intervalOriginalDirection == -1 : intervalOriginalDirection == -1 or (intervalIsDisrespected and intervalOriginalDirection == 1)
        bool bullishCounterControllerSetup = sessionAnchorFpiFound and sessionAnchorDirection == -1
        bool bearishCounterControllerSetup = sessionAnchorFpiFound and sessionAnchorDirection == 1
        bool bullishStructurePairReady = array.get(intervalBullObValidated, currentWindow) and array.get(intervalBullImbValidated, currentWindow)
        bool bearishStructurePairReady = array.get(intervalBearObValidated, currentWindow) and array.get(intervalBearImbValidated, currentWindow)
        bool bullishFoundationReady = array.get(intervalBullStructureValidated, currentWindow) and (not bullishCounterControllerSetup or bullishStructurePairReady)
        bool bearishFoundationReady = array.get(intervalBearStructureValidated, currentWindow) and (not bearishCounterControllerSetup or bearishStructurePairReady)
        bool bullishCounterSessionAuthorized = reversalModeActive and reversalModeDirection == 1 ? true : sessionAnchorDirection != -1 or returnedToPreviousSessionFpi or newSessionHighBreakout
        bool bearishCounterSessionAuthorized = reversalModeActive and reversalModeDirection == -1 ? true : sessionAnchorDirection != 1 or returnedToPreviousSessionFpi or newSessionLowBreakout
        bool bullishTriggerNow = bullishCounterControllerSetup ? rawStructureSignal and rawStructureDirection == 1 : reversalModeActive ? rawStructureSignal and rawStructureDirection == 1 : (rawStructureSignal and rawStructureDirection == 1) or (sessionAnchorDirection == -1 and (returnedToPreviousSessionFpi or newSessionHighBreakout))
        bool bearishTriggerNow = bearishCounterControllerSetup ? rawStructureSignal and rawStructureDirection == -1 : reversalModeActive ? rawStructureSignal and rawStructureDirection == -1 : (rawStructureSignal and rawStructureDirection == -1) or (sessionAnchorDirection == 1 and (returnedToPreviousSessionFpi or newSessionLowBreakout))

        if bullishFpiStateAllows and bullishFoundationReady and bullishCounterSessionAuthorized and bullishTriggerNow and not bullishSequenceContext and not array.get(intervalBullEntryUsed, currentWindow)
            intervalFoundationSignalNow := true
            intervalFoundationSignalDirection := 1
            intervalFoundationSignalTop := array.get(intervalBullStructureTop, currentWindow)
            intervalFoundationSignalBottom := array.get(intervalBullStructureBottom, currentWindow)
            intervalFoundationSignalKind := array.get(intervalBullStructureKind, currentWindow)
            array.set(intervalBullEntryUsed, currentWindow, true)
        else if bearishFpiStateAllows and bearishFoundationReady and bearishCounterSessionAuthorized and bearishTriggerNow and not bearishSequenceContext and not array.get(intervalBearEntryUsed, currentWindow)
            intervalFoundationSignalNow := true
            intervalFoundationSignalDirection := -1
            intervalFoundationSignalTop := array.get(intervalBearStructureTop, currentWindow)
            intervalFoundationSignalBottom := array.get(intervalBearStructureBottom, currentWindow)
            intervalFoundationSignalKind := array.get(intervalBearStructureKind, currentWindow)
            array.set(intervalBearEntryUsed, currentWindow, true)
"""

new_interval_block = """        bool intervalIsDisrespected = array.get(intervalFpiDisrespected, currentWindow)
        bool intervalFpiRespectConfirmed = array.get(intervalFpiRespected, currentWindow) and not intervalIsDisrespected

        // Ordinary interval execution must come from a fresh, fully validated structure
        // produced by this exact 30-minute interval. Older phase-wide structures remain
        // available to the dedicated sequence/confluence engine, but cannot masquerade
        // as the current interval's executable OB or BGOB.
        bool currentIntervalObSignal = orderBlockSignalNow and orderBlockSignalSourceWindow == currentWindow
        bool currentIntervalBgobSignal = bgobSignalNow and bgobSignalWindow == currentWindow
        bool rawStructureSignal = currentIntervalObSignal or currentIntervalBgobSignal
        int rawStructureDirection = currentIntervalObSignal ? orderBlockSignalDirection : currentIntervalBgobSignal ? bgobSignalDirection : 0

        bool returnedToPreviousSessionFpi = false
        for previousWindow = phaseStartWindow(activeNyPhase) to LAST_WINDOW_ID
            if previousWindow < currentWindow and array.get(selectedByWindow, previousWindow)
                float previousTop = array.get(intervalFpiTop, previousWindow)
                float previousBottom = array.get(intervalFpiBottom, previousWindow)
                if not na(previousTop) and not na(previousBottom) and low <= previousTop and high >= previousBottom
                    returnedToPreviousSessionFpi := true

        bool newSessionHighBreakout = not na(sessionExtremeHigh) and close > sessionExtremeHigh
        bool newSessionLowBreakout = not na(sessionExtremeLow) and close < sessionExtremeLow

        // FPI formation or a directional breakout is context only. The selected FPI must
        // first complete acceptance, a later physical retest, and an outside close.
        bool bullishFpiStateAllows = intervalFpiRespectConfirmed and intervalOriginalDirection == 1 and (not reversalModeActive or reversalModeDirection == 1)
        bool bearishFpiStateAllows = intervalFpiRespectConfirmed and intervalOriginalDirection == -1 and (not reversalModeActive or reversalModeDirection == -1)

        bool bullishValidatedOb = array.get(intervalBullObValidated, currentWindow)
        bool bearishValidatedOb = array.get(intervalBearObValidated, currentWindow)
        bool bullishValidatedBgob = array.get(intervalBullStructureValidated, currentWindow) and array.get(intervalBullStructureKind, currentWindow) == SOURCE_BGOB
        bool bearishValidatedBgob = array.get(intervalBearStructureValidated, currentWindow) and array.get(intervalBearStructureKind, currentWindow) == SOURCE_BGOB
        bool bullishFoundationReady = intervalFpiRespectConfirmed and (bullishValidatedOb or bullishValidatedBgob)
        bool bearishFoundationReady = intervalFpiRespectConfirmed and (bearishValidatedOb or bearishValidatedBgob)

        // A prior-FPI return or HH/LL breakout may authorize the narrative, but neither
        // can create an order without the fresh same-interval structural pulse above.
        bool bullishCounterSessionAuthorized = reversalModeActive and reversalModeDirection == 1 ? true : sessionAnchorDirection != -1 or returnedToPreviousSessionFpi or newSessionHighBreakout
        bool bearishCounterSessionAuthorized = reversalModeActive and reversalModeDirection == -1 ? true : sessionAnchorDirection != 1 or returnedToPreviousSessionFpi or newSessionLowBreakout
        bool bullishTriggerNow = rawStructureSignal and rawStructureDirection == 1
        bool bearishTriggerNow = rawStructureSignal and rawStructureDirection == -1

        if bullishFpiStateAllows and bullishFoundationReady and bullishCounterSessionAuthorized and bullishTriggerNow and not bullishSequenceContext and not array.get(intervalBullEntryUsed, currentWindow)
            intervalFoundationSignalNow := true
            intervalFoundationSignalDirection := 1
            intervalFoundationSignalTop := array.get(intervalBullStructureTop, currentWindow)
            intervalFoundationSignalBottom := array.get(intervalBullStructureBottom, currentWindow)
            intervalFoundationSignalKind := array.get(intervalBullStructureKind, currentWindow)
        else if bearishFpiStateAllows and bearishFoundationReady and bearishCounterSessionAuthorized and bearishTriggerNow and not bearishSequenceContext and not array.get(intervalBearEntryUsed, currentWindow)
            intervalFoundationSignalNow := true
            intervalFoundationSignalDirection := -1
            intervalFoundationSignalTop := array.get(intervalBearStructureTop, currentWindow)
            intervalFoundationSignalBottom := array.get(intervalBearStructureBottom, currentWindow)
            intervalFoundationSignalKind := array.get(intervalBearStructureKind, currentWindow)
"""
source = replace_once(source, old_interval_block, new_interval_block, "replace permissive interval-entry resolver")

# A retained opening confluence may release a waiting state, but it cannot directly place an order.
source = replace_once(
    source,
    "    // Resolve the one effective structural signal for this bar.\n    bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow or openingConfluenceReleaseSignalNow",
    "    // Resolve the one effective structural signal for this bar.\n    bool effectiveCameFromIntervalFoundation = not priorRespectedFpiReversalSignalNow and not reversalFoundationSignalNow and intervalFoundationSignalNow\n    bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow",
    "remove breakout/confluence-only direct entry path",
)

# Consume an interval direction only after TradingView is actually sent an entry order.
source = replace_once(
    source,
    """            if effectiveDirection == 1
                strategy.entry(ORDER_ID, strategy.long, qty=cfg.orderQuantity, comment="BUY")
                buyEntryNow := true
            else
                strategy.entry(ORDER_ID, strategy.short, qty=cfg.orderQuantity, comment="SELL")
                sellEntryNow := true

            recordedTradeOpen := true""",
    """            if effectiveDirection == 1
                strategy.entry(ORDER_ID, strategy.long, qty=cfg.orderQuantity, comment="BUY")
                buyEntryNow := true
            else
                strategy.entry(ORDER_ID, strategy.short, qty=cfg.orderQuantity, comment="SELL")
                sellEntryNow := true

            if effectiveCameFromIntervalFoundation and currentWindow >= 0
                if effectiveDirection == 1
                    array.set(intervalBullEntryUsed, currentWindow, true)
                else
                    array.set(intervalBearEntryUsed, currentWindow, true)

            recordedTradeOpen := true""",
    "consume interval entry state only after an order",
)

# Replace the old result box with one compact professional label that remains on its day.
source = replace_once(
    source,
    "    var box sessionResultBox = na",
    "    var label sessionResultLabel = na",
    "replace session result box state with label state",
)
source = replace_once(
    source,
    "        sessionResultBox := na\n        confluenceStatusBox := na",
    "        sessionResultLabel := na\n        confluenceStatusBox := na",
    "reset current session result label without deleting history",
)

session_creation_pattern = re.escape("        if (drawConfluenceStatus or drawSessionResults) and isOneMinute\n") + r".*?" + re.escape("                dailyTradeLogBox := box.new(left=sessionResultsLeft, top=dailyLogTop, right=sessionResultsRight, bottom=dailyLogBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=color.new(#212529, 8), text=dailyTradeLogText(ledger), text_size=size.normal, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)")
session_creation_replacement = """        if (drawConfluenceStatus or drawSessionResults) and isOneMinute
            int sessionResultsLeft = minuteTimestamp(SESSION_OPEN_MINUTE) + 60000
            int sessionResultsRight = minuteTimestamp(SESSION_END_MINUTE) - 60000
            float confluenceBoxTop = sessionPriceLow - cfg.tradeTableGap - cfg.tradeTableHeight - cfg.tradeTableGap
            float confluenceBoxBottom = confluenceBoxTop - cfg.tradeTableHeight
            if drawConfluenceStatus
                confluenceStatusBox := box.new(left=sessionResultsLeft, top=confluenceBoxTop, right=sessionResultsRight, bottom=confluenceBoxBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=color.new(#343a40, 12), text=confluenceSummary(sessionAnchorDirection, sessionFpiRegime, 0, na, confluenceBoundary, confluenceValid, reversalModeActive, reversalModeDirection, 0, 0), text_size=size.large, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)
            if drawSessionResults
                sessionResultLabel := label.new(x=bar_index, y=high, text="NY SESSION  |  LIVE\\nNET  0.00 PTS  •  0 TRADES", xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(#343a40, 5), textcolor=color.white, size=size.small, textalign=text.align_center)
                float dailyLogTop = (drawConfluenceStatus ? confluenceBoxBottom : confluenceBoxTop) - cfg.tradeTableGap
                float dailyLogBottom = dailyLogTop - cfg.tradeTableHeight * 2.0
                dailyTradeLogBox := box.new(left=sessionResultsLeft, top=dailyLogTop, right=sessionResultsRight, bottom=dailyLogBottom, xloc=xloc.bar_time, border_color=color.new(color.black, 0), border_width=2, bgcolor=color.new(#212529, 8), text=dailyTradeLogText(ledger), text_size=size.normal, text_color=color.white, text_halign=text.align_center, text_valign=text.align_center, text_font_family=font.family_monospace)"""
source = regex_once(source, session_creation_pattern, session_creation_replacement, "create professional session result label")

session_update_pattern = re.escape("        if drawSessionResults and not na(sessionResultBox)\n") + r".*?" + re.escape("                box.set_text(dailyTradeLogBox, dailyTradeLogText(ledger))")
session_update_replacement = """        if drawSessionResults and not na(sessionResultLabel)
            float openTradePoints = recordedTradeOpen and not na(recordedEntry) ? tradePoints(recordedTradeDirection, recordedEntry, close) : 0.0
            float displayedSessionPoints = sessionClosedPoints + openTradePoints
            int displayedTradeCount = dailyTradeCount(ledger)
            float displayedSessionHigh = inSession ? math.max(nz(sessionExtremeHigh, high), high) : nz(sessionExtremeHigh, high)
            float displayedSessionLow = inSession ? math.min(nz(sessionExtremeLow, low), low) : nz(sessionExtremeLow, low)
            float visibleSessionRange = math.max(displayedSessionHigh - displayedSessionLow, syminfo.mintick * 40.0)
            float resultLabelY = displayedSessionHigh + visibleSessionRange * 0.045
            string resultStatus = sessionEnded ? "FINAL" : "LIVE"
            string tradeWord = displayedTradeCount == 1 ? "TRADE" : "TRADES"
            string resultLabelText = "NY SESSION  |  " + resultStatus + "\\nNET  " + signedPointsText(displayedSessionPoints) + "  •  " + str.tostring(displayedTradeCount) + " " + tradeWord
            color resultLabelColor = displayedSessionPoints > 0 ? color.new(#1b4332, 5) : displayedSessionPoints < 0 ? color.new(#7f1d1d, 5) : color.new(#343a40, 5)
            label.set_x(sessionResultLabel, bar_index)
            label.set_y(sessionResultLabel, resultLabelY)
            label.set_text(sessionResultLabel, resultLabelText)
            label.set_color(sessionResultLabel, resultLabelColor)
            label.set_textcolor(sessionResultLabel, color.white)
            if not na(dailyTradeLogBox)
                float dailyLogTop = (drawConfluenceStatus ? confluenceBoxBottom : confluenceBoxTop) - cfg.tradeTableGap
                float dailyLogHeight = cfg.tradeTableHeight * math.max(2.0, 1.0 + displayedTradeCount * 0.55)
                box.set_top(dailyTradeLogBox, dailyLogTop)
                box.set_bottom(dailyTradeLogBox, dailyLogTop - dailyLogHeight)
                box.set_text(dailyTradeLogBox, dailyTradeLogText(ledger))"""
source = regex_once(source, session_update_pattern, session_update_replacement, "update professional session result label")
source = source.replace("// Centered session-wide confluence and result boxes remain beneath every ledger.", "// Keep the confluence stack beneath the ledger and the compact session result label above price.")

# Source-level validation: these checks are deliberately strict so a partial patch cannot be published.
required_markers = [
    "bool intervalFpiRespectConfirmed",
    "bool currentIntervalObSignal",
    "bool currentIntervalBgobSignal",
    "bool effectiveCameFromIntervalFoundation",
    "array.set(intervalBullEntryUsed, currentWindow, true)",
    "array.set(intervalBearEntryUsed, currentWindow, true)",
    "var label sessionResultLabel = na",
    "NY SESSION  |  ",
]
for marker in required_markers:
    if marker not in source:
        raise RuntimeError(f"Required updated marker missing: {marker}")

for forbidden in [
    "bool rawEffectiveSignalNow = priorRespectedFpiReversalSignalNow or reversalFoundationSignalNow or intervalFoundationSignalNow or openingConfluenceReleaseSignalNow",
    "if drawSessionResults and not na(sessionResultBox)",
    "var box sessionResultBox = na",
]:
    if forbidden in source:
        raise RuntimeError(f"Forbidden legacy path remains: {forbidden}")

if source.count('library("PO3MMXMEnigmaCore"') != 1:
    raise RuntimeError("Library title changed or duplicated")
if source.count("array.set(intervalBullEntryUsed, currentWindow, true)") != 1:
    raise RuntimeError("Bull interval use must be consumed only at actual order execution")
if source.count("array.set(intervalBearEntryUsed, currentWindow, true)") != 1:
    raise RuntimeError("Bear interval use must be consumed only at actual order execution")

core_path = ROOT / "PO3_MMXM_Enigma_Core.pine"
core_path.write_text(source, encoding="utf-8")

report = [
    "PO3 MMXM Enigma stable build",
    f"core_lines={len(source.splitlines())}",
    "library_title=PO3MMXMEnigmaCore",
    "strict_fpi_acceptance_retest=true",
    "same_interval_structure_trigger=true",
    "breakout_only_entry=false",
    "consume_interval_only_on_order=true",
    "session_result_label=true",
]
(ROOT / "enigma_build" / "build_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
