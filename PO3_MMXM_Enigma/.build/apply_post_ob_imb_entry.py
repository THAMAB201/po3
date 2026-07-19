from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PO3_MMXM_Enigma_Execution_Engine.pine"
text = TARGET.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    text = text.replace(old, new, 1)


# A newly validated OB starts a new post-OB IMB search. Earlier phase IMBs may not
# satisfy the rule "lowest/highest IMB formed after the OB confirmation."
replace_once(
    "            seriesObValidationEndBar := obDecision.bullValidationEndBar\n"
    "            if drawStructureVisuals\n",
    "            seriesObValidationEndBar := obDecision.bullValidationEndBar\n"
    "            bullishImbCandidateFound := false\n"
    "            bullishImbCandidateTop := na\n"
    "            bullishImbCandidateBottom := na\n"
    "            bullishImbFormationBar := na\n"
    "            bullishImbStartTime := na\n"
    "            bullishImbBreakConfirmed := false\n"
    "            bullishImbBreakBar := na\n"
    "            bullishImbCandidateUsed := false\n"
    "            bullPairBearImbFound := false\n"
    "            bullPairBearImbTop := na\n"
    "            bullPairBearImbBottom := na\n"
    "            bullPairBearImbFormationBar := na\n"
    "            bullPairBearImbStartTime := na\n"
    "            bullPairBearImbWindow := -1\n"
    "            bullPairBearImbReclaimConfirmed := false\n"
    "            bullPairBearImbReclaimBar := na\n"
    "            bullPairBearImbUsed := false\n"
    "            if drawStructureVisuals\n",
    "reset bullish post-OB IMB search",
)
replace_once(
    "            seriesObValidationEndBar := obDecision.bearValidationEndBar\n"
    "            if drawStructureVisuals\n",
    "            seriesObValidationEndBar := obDecision.bearValidationEndBar\n"
    "            bearishImbCandidateFound := false\n"
    "            bearishImbCandidateTop := na\n"
    "            bearishImbCandidateBottom := na\n"
    "            bearishImbFormationBar := na\n"
    "            bearishImbStartTime := na\n"
    "            bearishImbBreakConfirmed := false\n"
    "            bearishImbBreakBar := na\n"
    "            bearishImbCandidateUsed := false\n"
    "            bearPairBullImbFound := false\n"
    "            bearPairBullImbTop := na\n"
    "            bearPairBullImbBottom := na\n"
    "            bearPairBullImbFormationBar := na\n"
    "            bearPairBullImbStartTime := na\n"
    "            bearPairBullImbWindow := -1\n"
    "            bearPairBullImbReclaimConfirmed := false\n"
    "            bearPairBullImbReclaimBar := na\n"
    "            bearPairBullImbUsed := false\n"
    "            if drawStructureVisuals\n",
    "reset bearish post-OB IMB search",
)

# Track only IMBs formed after the matching OB has validated. The FVG formation
# candle itself is displacement away from the zone, so the first later overlap and
# outside close is the actionable retest; no redundant extra break-away candle is required.
replace_once(
    "            if intervalImbalanceDirection == 1\n"
    "                bool replaceBullishImbalance = not bullishImbCandidateFound or intervalImbalanceBottom < bullishImbCandidateBottom\n",
    "            if intervalImbalanceDirection == 1\n"
    "                bool bullishPostObImbalanceEligible = bullishObCandidateFound and bullishObBreakConfirmed and not na(bullishObBreakBar) and bar_index >= bullishObBreakBar\n"
    "                bool replaceBullishImbalance = bullishPostObImbalanceEligible and (not bullishImbCandidateFound or intervalImbalanceBottom < bullishImbCandidateBottom)\n",
    "gate bullish IMB to post-OB sequence",
)
replace_once(
    "                    bullishImbStartTime := time[2]\n"
    "                    bullishImbBreakConfirmed := false\n"
    "                    bullishImbBreakBar := na\n"
    "                    bullishImbCandidateUsed := false\n",
    "                    bullishImbStartTime := time[2]\n"
    "                    bullishImbBreakConfirmed := close > intervalImbalanceTop\n"
    "                    bullishImbBreakBar := bullishImbBreakConfirmed ? bar_index : na\n"
    "                    bullishImbCandidateUsed := false\n",
    "arm bullish IMB on formation displacement",
)
replace_once(
    "            else\n"
    "                bool replaceBearishImbalance = not bearishImbCandidateFound or intervalImbalanceTop > bearishImbCandidateTop\n",
    "            else\n"
    "                bool bearishPostObImbalanceEligible = bearishObCandidateFound and bearishObBreakConfirmed and not na(bearishObBreakBar) and bar_index >= bearishObBreakBar\n"
    "                bool replaceBearishImbalance = bearishPostObImbalanceEligible and (not bearishImbCandidateFound or intervalImbalanceTop > bearishImbCandidateTop)\n",
    "gate bearish IMB to post-OB sequence",
)
replace_once(
    "                    bearishImbStartTime := time[2]\n"
    "                    bearishImbBreakConfirmed := false\n"
    "                    bearishImbBreakBar := na\n"
    "                    bearishImbCandidateUsed := false\n",
    "                    bearishImbStartTime := time[2]\n"
    "                    bearishImbBreakConfirmed := close < intervalImbalanceBottom\n"
    "                    bearishImbBreakBar := bearishImbBreakConfirmed ? bar_index : na\n"
    "                    bearishImbCandidateUsed := false\n",
    "arm bearish IMB on formation displacement",
)

replace_once(
    "                if intervalImbalanceDirection == -1\n"
    "                    bool replaceLowerBearImb = not bullPairBearImbFound or na(bullPairBearImbBottom) or intervalImbalanceBottom < bullPairBearImbBottom\n",
    "                if intervalImbalanceDirection == -1\n"
    "                    bool bullishPostObInverseImbEligible = bullishObCandidateFound and bullishObBreakConfirmed and not na(bullishObBreakBar) and bar_index >= bullishObBreakBar\n"
    "                    bool replaceLowerBearImb = bullishPostObInverseImbEligible and (not bullPairBearImbFound or na(bullPairBearImbBottom) or intervalImbalanceBottom < bullPairBearImbBottom)\n",
    "gate bullish inverse IMB to post-OB sequence",
)
replace_once(
    "                else if intervalImbalanceDirection == 1\n"
    "                    bool replaceHigherBullImb = not bearPairBullImbFound or na(bearPairBullImbTop) or intervalImbalanceTop > bearPairBullImbTop\n",
    "                else if intervalImbalanceDirection == 1\n"
    "                    bool bearishPostObInverseImbEligible = bearishObCandidateFound and bearishObBreakConfirmed and not na(bearishObBreakBar) and bar_index >= bearishObBreakBar\n"
    "                    bool replaceHigherBullImb = bearishPostObInverseImbEligible and (not bearPairBullImbFound or na(bearPairBullImbTop) or intervalImbalanceTop > bearPairBullImbTop)\n",
    "gate bearish inverse IMB to post-OB sequence",
)

replace_once(
    "    bool bullAlignedJudasImbReclaimNow = false\n"
    "    bool bearAlignedJudasImbReclaimNow = false\n",
    "    bool bullAlignedJudasImbReclaimNow = false\n"
    "    bool bearAlignedJudasImbReclaimNow = false\n"
    "    bool bullControllerAlignedImbReclaimNow = false\n"
    "    bool bearControllerAlignedImbReclaimNow = false\n",
    "controller-aligned reclaim declarations",
)
replace_once(
    "        bool bullishSequenceContextActive = latestBullAgainstFpiWindow >= 0 or bullishMacro950FoundationExpectation\n"
    "        bool bearishSequenceContextActive = latestBearAgainstFpiWindow >= 0 or bearishMacro950FoundationExpectation\n",
    "        bool bullishControllerFoundationContext = sessionAnchorFpiFound and sessionAnchorDirection == 1\n"
    "        bool bearishControllerFoundationContext = sessionAnchorFpiFound and sessionAnchorDirection == -1\n"
    "        bool bullishSequenceContextActive = latestBullAgainstFpiWindow >= 0 or bullishMacro950FoundationExpectation or bullishControllerFoundationContext\n"
    "        bool bearishSequenceContextActive = latestBearAgainstFpiWindow >= 0 or bearishMacro950FoundationExpectation or bearishControllerFoundationContext\n",
    "controller-aligned sequence contexts",
)
replace_once(
    "        bullAlignedJudasImbReclaimNow := bullOpposingImbReclaimPulseNow and bullObArmed and activeNyPhase == SESSION_PHASE_AM and sessionAnchorFpiFound and sessionAnchorDirection == 1 and macro950Found and macro950Direction == 1 and latestBullAgainstFpiWindow >= 0\n"
    "        bool bullImbRetestNow = bullishImbComponentNow or bullishMacro950ComponentPulseNow or bullAlignedJudasImbReclaimNow\n",
    "        bullAlignedJudasImbReclaimNow := bullOpposingImbReclaimPulseNow and bullObArmed and activeNyPhase == SESSION_PHASE_AM and sessionAnchorFpiFound and sessionAnchorDirection == 1 and macro950Found and macro950Direction == 1 and latestBullAgainstFpiWindow >= 0\n"
    "        bullControllerAlignedImbReclaimNow := bullOpposingImbReclaimPulseNow and bullObArmed and sessionAnchorFpiFound and sessionAnchorDirection == 1\n"
    "        bool bullImbRetestNow = bullishImbComponentNow or bullishMacro950ComponentPulseNow or bullAlignedJudasImbReclaimNow or bullControllerAlignedImbReclaimNow\n",
    "bullish controller-aligned reclaim trigger",
)
replace_once(
    "        bearAlignedJudasImbReclaimNow := bearOpposingImbReclaimPulseNow and bearObArmed and activeNyPhase == SESSION_PHASE_AM and sessionAnchorFpiFound and sessionAnchorDirection == -1 and macro950Found and macro950Direction == -1 and latestBearAgainstFpiWindow >= 0\n"
    "        bool bearImbRetestNow = bearishImbComponentNow or bearishMacro950ComponentPulseNow or bearAlignedJudasImbReclaimNow\n",
    "        bearAlignedJudasImbReclaimNow := bearOpposingImbReclaimPulseNow and bearObArmed and activeNyPhase == SESSION_PHASE_AM and sessionAnchorFpiFound and sessionAnchorDirection == -1 and macro950Found and macro950Direction == -1 and latestBearAgainstFpiWindow >= 0\n"
    "        bearControllerAlignedImbReclaimNow := bearOpposingImbReclaimPulseNow and bearObArmed and sessionAnchorFpiFound and sessionAnchorDirection == -1\n"
    "        bool bearImbRetestNow = bearishImbComponentNow or bearishMacro950ComponentPulseNow or bearAlignedJudasImbReclaimNow or bearControllerAlignedImbReclaimNow\n",
    "bearish controller-aligned reclaim trigger",
)
replace_once(
    "        bool bullInverseImbRetestConfirmation = bullFreshFoundationConfirmation and (bullOpposingImbSignalNow or bullAlignedJudasImbReclaimNow) and bullRevFoundationHasOb and close > bullRevFoundationImbTop\n",
    "        bool bullInverseImbRetestConfirmation = bullFreshFoundationConfirmation and (bullOpposingImbSignalNow or bullAlignedJudasImbReclaimNow or bullControllerAlignedImbReclaimNow) and bullRevFoundationHasOb and close > bullRevFoundationImbTop\n",
    "bullish controller-aligned inverse confirmation",
)
replace_once(
    "        bool bearInverseImbRetestConfirmation = bearFreshFoundationConfirmation and (bearOpposingImbSignalNow or bearAlignedJudasImbReclaimNow) and bearRevFoundationHasOb and close < bearRevFoundationImbBottom\n",
    "        bool bearInverseImbRetestConfirmation = bearFreshFoundationConfirmation and (bearOpposingImbSignalNow or bearAlignedJudasImbReclaimNow or bearControllerAlignedImbReclaimNow) and bearRevFoundationHasOb and close < bearRevFoundationImbBottom\n",
    "bearish controller-aligned inverse confirmation",
)

replace_once(
    "        bool bullSequenceReadyNow = bullFoundationDecision.enterNow and (not cfg.requireFreshFoundationSignal or bullFreshFoundationConfirmation)\n",
    "        bool bullControllerAlignedPostObImbEntry = cfg.allowControllerAlignedFoundationEntry and bullControllerAligned and not bullMacroOriginAligned and bullFreshFoundationConfirmation and (bullInverseImbRetestConfirmation or bullAlignedImbRetestConfirmation) and bullComponentsStillRespected and bullFoundationNotChased\n"
    "        bool bullSequenceReadyNow = (bullFoundationDecision.enterNow or bullControllerAlignedPostObImbEntry) and (not cfg.requireFreshFoundationSignal or bullFreshFoundationConfirmation)\n",
    "bullish session-aligned macro-opposed entry permission",
)
replace_once(
    "        bool bearSequenceReadyNow = bearFoundationDecision.enterNow and (not cfg.requireFreshFoundationSignal or bearFreshFoundationConfirmation)\n",
    "        bool bearControllerAlignedPostObImbEntry = cfg.allowControllerAlignedFoundationEntry and bearControllerAligned and not bearMacroOriginAligned and bearFreshFoundationConfirmation and (bearInverseImbRetestConfirmation or bearAlignedImbRetestConfirmation) and bearComponentsStillRespected and bearFoundationNotChased\n"
    "        bool bearSequenceReadyNow = (bearFoundationDecision.enterNow or bearControllerAlignedPostObImbEntry) and (not cfg.requireFreshFoundationSignal or bearFreshFoundationConfirmation)\n",
    "bearish session-aligned macro-opposed entry permission",
)
replace_once(
    "            reversalFoundationEarlyEntryNow := bullFoundationDecision.earlyReversal\n"
    "            reversalFoundationNarrativeConfirmedNow := bullFoundationDecision.narrativeConfirmed\n",
    "            reversalFoundationEarlyEntryNow := bullFoundationDecision.earlyReversal or bullControllerAlignedPostObImbEntry\n"
    "            reversalFoundationNarrativeConfirmedNow := bullFoundationDecision.narrativeConfirmed\n",
    "mark bullish macro-opposed foundation as early",
)
replace_once(
    "            reversalFoundationEarlyEntryNow := bearFoundationDecision.earlyReversal\n"
    "            reversalFoundationNarrativeConfirmedNow := bearFoundationDecision.narrativeConfirmed\n",
    "            reversalFoundationEarlyEntryNow := bearFoundationDecision.earlyReversal or bearControllerAlignedPostObImbEntry\n"
    "            reversalFoundationNarrativeConfirmedNow := bearFoundationDecision.narrativeConfirmed\n",
    "mark bearish macro-opposed foundation as early",
)

required_markers = [
    "bullishPostObImbalanceEligible",
    "bearishPostObImbalanceEligible",
    "bullControllerAlignedPostObImbEntry",
    "bearControllerAlignedPostObImbEntry",
    "bullControllerAlignedImbReclaimNow",
    "bearControllerAlignedImbReclaimNow",
]
for marker in required_markers:
    if marker not in text:
        raise RuntimeError(f"Missing required marker after patch: {marker}")

TARGET.write_text(text, encoding="utf-8")
print("Applied post-OB lowest/highest IMB first-retest entry logic.")
