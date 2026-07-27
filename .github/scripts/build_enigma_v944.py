from pathlib import Path
import re

source = Path('enigma/PO3_MMXM_Enigma_Strategy_V9_4_3_Strict_Foundation_Then_IMB.pine')
target = Path('enigma/PO3_MMXM_Enigma_Strategy_V9_4_4_Dynamic_30m_Narrative.pine')
text = source.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if old not in text:
        raise RuntimeError(f'{label} anchor not found')
    text = text.replace(old, new, 1)


def sub_once(pattern: str, replacement: str, label: str) -> None:
    global text
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S | re.M)
    if count != 1:
        raise RuntimeError(f'{label} regex count={count}')
    text = updated


replace_once(
    '"PO3 MMXM Enigma V9.4.3 Strict Foundation Then IMB",\n    shorttitle = "PO3E943F",',
    '"PO3 MMXM Enigma V9.4.4 Dynamic 30m Narrative",\n    shorttitle = "PO3E944D",',
    'title',
)

replace_once(
    'bool allowOpposingImbReclaim = input.bool(true, "Allow Opposing IMB Reclaim", group = G_STRUCTURE)',
    'bool allowOpposingFpiDisrespect = input.bool(true, "Allow Opposing 30m FPI Disrespect Toward Session Bias", group = G_STRUCTURE)',
    'opposing FPI input',
)

regular_body_function = r'''regularBodyObSeed\(int direction, int searchBars, int requiredWindow\) =>.*?^foundationBodyInvalid\(structure, int direction\) =>'''
regular_body_replacement = '''regularBodyObSeed(int direction, int searchBars, int requiredWindow) =>
    result = market.newStructure()
    bool collecting = true
    bool found = false
    float zoneTop = na
    float zoneBottom = na
    float invalidation = na
    float extremeMetric = na
    int extremeBar = na
    int extremeTime = na

    // A regular OB is the consecutive opposing body series immediately
    // preceding the three-candle displacement/FPI. An unrelated candle
    // elsewhere in the lookback cannot become the current foundation.
    for i = 3 to searchBars + 2
        if collecting
            int candleWindow = windowFromTimestamp(time[i])
            bool oppositeCandle = direction == market.DIR_LONG ? close[i] < open[i] : close[i] > open[i]
            if candleWindow != requiredWindow or not oppositeCandle
                collecting := false
            else
                float bodyTop = math.max(open[i], close[i])
                float bodyBottom = math.min(open[i], close[i])
                float metric = direction == market.DIR_LONG ? low[i] : high[i]
                bool moreExtremeNow = na(extremeMetric) or direction == market.DIR_LONG and metric < extremeMetric or direction == market.DIR_SHORT and metric > extremeMetric
                found := true
                zoneTop := na(zoneTop) ? bodyTop : math.max(zoneTop, bodyTop)
                zoneBottom := na(zoneBottom) ? bodyBottom : math.min(zoneBottom, bodyBottom)
                invalidation := na(invalidation) ? metric : direction == market.DIR_LONG ? math.min(invalidation, metric) : math.max(invalidation, metric)
                if moreExtremeNow
                    extremeMetric := metric
                    extremeBar := bar_index - i
                    extremeTime := time[i]

    if found
        market.setStructure(result, direction, market.FAMILY_PRIMARY_OB, zoneTop, zoneBottom, zoneTop, zoneBottom, invalidation, extremeBar, extremeTime, requiredWindow, extremeTime, market.STATUS_ARMED, direction == market.DIR_LONG ? "OB-BULL-01" : "OB-BEAR-01", "CONSECUTIVE_BODY_ORDER_BLOCK")
    result

foundationBodyInvalid(structure, int direction) =>'''
sub_once(regular_body_function, regular_body_replacement, 'regular body OB function')

bind_function = r'''bindImbCandidate\(target, source, foundation, int direction, int requiredWindow\) =>.*?^sameImbSource\(first, second\) =>'''
bind_replacement = '''bindImbCandidate(target, source, foundation, int direction, int requiredWindow) =>
    // The entry IMB must be aligned with the intended move and created by
    // the foundation-confirming displacement or later in this same window.
    // Older and opposite IMBs cannot be relabeled as fresh confirmation.
    bool sourceLive = source.active and not source.used and source.status == market.STATUS_ARMED
    bool sameDirection = source.direction == direction
    bool formedWithOrAfterFoundation = not na(source.breakBar) and not na(foundation.confirmBar) and source.breakBar >= foundation.confirmBar
    bool causal = sourceLive and sameDirection and foundation.active and foundation.status == market.STATUS_CONFIRMED and source.sourceWindow == requiredWindow and windowFromTimestamp(source.sourceTime) == requiredWindow and source.sourceBar >= foundation.sourceBar and formedWithOrAfterFoundation
    bool replace = causal and (not target.active or target.used or target.status == market.STATUS_INVALID or moreExtreme(source.top, source.bottom, target.top, target.bottom, direction))
    if replace
        copyStructure(target, source)
        target.direction := direction
        target.family := market.FAMILY_POST_OB_IMB
        target.parentId := foundation.sourceBar
        target.sourceWindow := requiredWindow
        target.invalidation := direction == market.DIR_LONG ? target.bottom : target.top
        target.status := market.STATUS_ARMED
        target.used := false
        target.confirmBar := na
        target.touching := false
        target.ruleId := direction == market.DIR_LONG ? "BOUND-IMB-BUY" : "BOUND-IMB-SELL"
        target.reason := "ALIGNED_IMB_BOUND_TO_CONFIRMED_FOUNDATION"
    replace

sameImbSource(first, second) =>'''
sub_once(bind_function, bind_replacement, 'IMB binding function')

replace_once(
    'var bool judasCompleted = false',
    'var bool judasCompleted = false\nvar bool judasEntryTaken = false',
    'Judas entry state',
)
replace_once(
    'var bool windowResolved = false',
    'var bool windowResolved = false\nvar int windowAuthority = market.DIR_NONE\nvar bool windowFpiDisrespectedTowardSession = false',
    'window authority state',
)
replace_once(
    '    judasCompleted := false\n\nif newWindow or newSession',
    '    judasCompleted := false\n    judasEntryTaken := false\n\nif newWindow or newSession',
    'session reset',
)
replace_once(
    '    windowResolved := false\n    bullImbCandidate := market.newStructure()',
    '    windowResolved := false\n    windowAuthority := market.DIR_NONE\n    windowFpiDisrespectedTowardSession := false\n    bullImbCandidate := market.newStructure()',
    'window reset',
)
replace_once(
    '        windowFirstFpiBottom := fpiEvent.bottom\n        if drawFpiBoxes',
    '        windowFirstFpiBottom := fpiEvent.bottom\n        windowAuthority := fpiEvent.direction\n        windowFpiDisrespectedTowardSession := false\n        if drawFpiBoxes',
    'first FPI authority initialization',
)

foundation_transition_pattern = r'''        if acceptedFoundation and displacementConfirms\n            targetFoundation\.status := market\.STATUS_BROKEN\n            targetFoundation\.breakBar := bar_index\n            targetFoundation\.touching := false\n\n// Every bar advances the two candidate foundations\..*?bool bearFoundationConfirmedNow = updateFoundationLifecycle\(bearFoundationCandidate, market\.DIR_SHORT\)'''
foundation_transition_replacement = '''        if acceptedFoundation and displacementConfirms
            // Displacement confirms the extreme regular OB or BOLO while its
            // body remains valid. The later retest belongs to the bound IMB.
            targetFoundation.status := market.STATUS_CONFIRMED
            targetFoundation.breakBar := bar_index
            targetFoundation.confirmBar := bar_index
            targetFoundation.touching := false

bool bullFoundationConfirmedNow = bullFoundationCandidate.active and bullFoundationCandidate.status == market.STATUS_CONFIRMED and bullFoundationCandidate.confirmBar == bar_index
bool bearFoundationConfirmedNow = bearFoundationCandidate.active and bearFoundationCandidate.status == market.STATUS_CONFIRMED and bearFoundationCandidate.confirmBar == bar_index'''
sub_once(foundation_transition_pattern, foundation_transition_replacement, 'foundation confirmation transition')

text = text.replace('CURRENT_WINDOW_BULLISH_OB_BOLO_BREAK_RETEST_RESPECT', 'CURRENT_WINDOW_BULLISH_OB_BOLO_DISPLACEMENT_CONFIRM')
text = text.replace('CURRENT_WINDOW_BEARISH_OB_BOLO_BREAK_RETEST_RESPECT', 'CURRENT_WINDOW_BEARISH_OB_BOLO_DISPLACEMENT_CONFIRM')

recovery_header = '''// =============================================================================
// Dynamic current-window recovery narrative
// =============================================================================
bool recoveryWindowEligible = sessionFpiFound and currentWindow >= 0 and (phase != PHASE_JUDAS or not requireLaterWindowForRecovery or currentWindow > judasStartWindow)
'''
recovery_header_new = '''// =============================================================================
// Persistent local-window FPI authority
// Session FPI remains the global objective. A window is permitted to trade
// that objective only when its first FPI aligns or its opposing FPI receives
// a body-close disrespect toward Session-FPI direction. Permission is latched.
// =============================================================================
if sessionFpiFound and windowFirstFpiFound
    if windowFirstFpiDirection == sessionDirection
        bool alignedWindowFailed = windowAuthority == sessionDirection and market.bodyCloseInvalidates(sessionDirection, sessionDirection == market.DIR_LONG ? windowFirstFpiBottom : windowFirstFpiTop, close)
        if alignedWindowFailed
            windowAuthority := -sessionDirection
    else if allowOpposingFpiDisrespect and windowAuthority != sessionDirection
        bool opposingWindowDisrespected = sessionDirection == market.DIR_LONG ? close > windowFirstFpiTop : close < windowFirstFpiBottom
        if opposingWindowDisrespected
            windowAuthority := sessionDirection
            windowFpiDisrespectedTowardSession := true

// =============================================================================
// Dynamic current-window recovery narrative
// =============================================================================
bool recoveryWindowEligible = sessionFpiFound and currentWindow >= 0 and windowFirstFpiFound and windowAuthority == sessionDirection and (phase != PHASE_JUDAS or not requireLaterWindowForRecovery or currentWindow > judasStartWindow)
'''
replace_once(recovery_header, recovery_header_new, 'recovery eligibility')

sub_once(
    r'''    if allowOpposingImbReclaim\n        opposingImb = recoveryDirection == market\.DIR_LONG \? bearImbCandidate : bullImbCandidate\n        if bindImbCandidate\(recoverySupport, opposingImb, recoveryFoundation, recoveryDirection, currentWindow\)\n            windowState := WINDOW_IMB_ARMED\n''',
    '',
    'recovery opposing IMB binding',
)

replace_once(
    'if phase == PHASE_JUDAS and enableJudasTrades and currentWindow >= 0 and judasDirection != market.DIR_NONE and not judasWindowResolved',
    'if phase == PHASE_JUDAS and enableJudasTrades and not judasEntryTaken and currentWindow >= 0 and windowFirstFpiFound and windowAuthority == judasDirection and judasDirection != market.DIR_NONE and not judasWindowResolved',
    'Judas eligibility',
)

sub_once(
    r'''        if allowOpposingImbReclaim\n            bindImbCandidate\(judasSupport, opposingJudasImb, judasFoundation, judasDirection, currentWindow\)\n''',
    '',
    'Judas opposing IMB binding',
)

replace_once(
    '        phase := PHASE_JUDAS\n\n    if drawSignals',
    '        phase := PHASE_JUDAS\n        judasEntryTaken := true\n\n    if drawSignals',
    'Judas entry consumption',
)

replace_once(
    'plot(windowFirstFpiFound ? windowFirstFpiDirection : na, "Window First FPI Direction", display = display.data_window)',
    'plot(windowFirstFpiFound ? windowFirstFpiDirection : na, "Window First FPI Direction", display = display.data_window)\nplot(windowAuthority, "Latched Window Authority", display = display.data_window)\nplot(windowFpiDisrespectedTowardSession ? 1 : 0, "Opposing Window FPI Disrespected Toward Session", display = display.data_window)\nplot(judasEntryTaken ? 1 : 0, "Judas Entry Already Used", display = display.data_window)',
    'diagnostics',
)

text = text.replace('CONFIRMED_OB_BOLO_RETEST_THEN_BOUND_IMB_RETEST_RESPECT', 'CONFIRMED_EXTREME_OB_BOLO_THEN_ALIGNED_IMB_RETEST_RESPECT')
text = text.replace('CONFIRMED_OB_BOLO_RETEST_THEN_BOUND_IMB_RETEST_JUDAS', 'ONE_JUDAS_SEQUENCE_EXTREME_OB_BOLO_THEN_ALIGNED_IMB_RETEST')

required = [
    'shorttitle = "PO3E944D"',
    'CONSECUTIVE_BODY_ORDER_BLOCK',
    'formedWithOrAfterFoundation',
    'windowAuthority == sessionDirection',
    'not judasEntryTaken',
    'judasEntryTaken := true',
    'Latched Window Authority',
]
for marker in required:
    if marker not in text:
        raise RuntimeError(f'missing required marker: {marker}')

target.write_text(text, encoding='utf-8')
