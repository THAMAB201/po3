// This Pine Script® code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
//@version=5
indicator("Intraday PO3 MMXM", overlay=true, max_boxes_count=200, max_lines_count=200, max_labels_count=200)

// ============================= Main Settings =============================
groupMain = "- - - - - - - - - - Main Settings - - - - - - - - - -"
po3Number       = input.int(81, "PO3 Number", options=[3,6,9,27,81,243,729,2187,6561,19683,59049,177147], group=groupMain)
bias            = input.string("Bearish", "Session Bias", options=["Bullish","Bearish"], group=groupMain)
useHalfRange    = input.bool(false, "Use Half Range for Projections", group=groupMain,
     tooltip="Bearish: uses bottom half (discount) of the PO3 range containing session high.\nBullish: uses top half (premium) of the PO3 range containing session low.")
projectionCount = input.int(4, "Number of Projections", minval=1, maxval=10, group=groupMain, display=display.none)
rangeShift      = input.string("None", "Source Range Shift", options=["None","Shift Down 1/2","Shift Up 1/2"], group=groupMain,
     tooltip="Shifts the entire source range up or down by half of one source range unit.")

// ============================= Visual Settings =============================
groupVisual     = "- - - - - - - - - - Visual Settings - - - - - - - - - -"
generalTextSize = input.string("normal", "Text Size", options=["tiny","small","normal","large","huge"], group=groupVisual, display=display.none)
showSubEQs      = input.bool(true, "Show Sub-Range EQ Lines", group=groupVisual)
showTable       = input.bool(true, "Show Levels Table", group=groupVisual)
tablePosition   = input.string("top_right", "Table Position", options=["top_left","top_right","bottom_left","bottom_right"], group=groupVisual, display=display.none)
projBorderClrIn = input.color(color.new(#000000, 25), "Projection Box Border Color", group=groupVisual)
subEQClrIn      = input.color(color.new(#000000, 13), "Projection EQ Line Color", group=groupVisual)
projBoxBullClr  = input.color(color.new(#1bb358, 98), "Projection BG — Bullish (green)", group=groupVisual)
projBoxBearClr  = input.color(color.new(#b60e0e, 98), "Projection BG — Bearish (red)", group=groupVisual)
endHour         = input.int(14, "Projection Box End Hour (NY, 24h)", minval=0, maxval=23, group=groupVisual,
     tooltip="Hour of day (New York time, 24-hour format) where the projection box, zones, and line extensions terminate.\nDefault: 14 = 2:00 PM NY")
endMinute       = input.int(0, "Projection Box End Minute", minval=0, maxval=59, group=groupVisual)

// ============================= Source Range Subdivisions =============================
groupSource            = "- - - - - - - - Source Range Subdivisions - - - - - - - -"
showSourceSubdivisions = input.bool(true, "Show Source Range Subdivisions", group=groupSource)
subdivisionType        = input.string("1/8", "Subdivision Type", options=["1/4","1/8"], group=groupSource)
subdivLineColor        = input.color(color.new(#808080, 70), "Subdivision Line Color", group=groupSource, display=display.none)

// ============================= Range High / Range Low Zones =============================
groupGB = "- - - - - - Range High / Range Low Zones - - - - - -"
showRangeZones  = input.bool(true, "Show Range High / Low Zones", group=groupGB,
     tooltip="Detects Range High and Range Low from all key levels:\nsource high/EQ/low, each projection boundary, and each projection EQ.\n\nA zone must be touched by price during the projection window.\nThe highest touched zone = Range High (red).\nThe lowest touched zone = Range Low (green).")
rangeHighClr    = input.color(color.new(#c45050, 70), "Range High Box Color", group=groupGB)
rangeLowClr     = input.color(color.new(#50a070, 70), "Range Low Box Color", group=groupGB)
rangeBoxBorder  = input.color(color.new(#888888, 40), "Zone Border Color", group=groupGB)
showRangeLabels = input.bool(true, "Show Zone Labels", group=groupGB)
rangeLabelSize  = input.string("small", "Zone Label Size", options=["tiny","small","normal","large"], group=groupGB)
rangeLabelTxt   = input.color(color.new(#ffffff, 0), "Zone Label Text Color", group=groupGB)
rangeLabelBg    = input.color(color.new(#000000, 30), "Zone Label BG Color", group=groupGB)
sharedZoneClr   = input.color(color.new(#808080, 72), "Shared Zone Color", group=groupGB, display=display.none)

// ============================= Derived Colors =============================
isBearish       = bias == "Bearish"
sourceBorderClr = isBearish ? color.new(#b05050, 55) : color.new(#50a070, 55)
sourceBoxClr    = isBearish ? color.new(#b05050, 88) : color.new(#50a070, 88)
thickLineClr    = isBearish ? color.new(#c45050, 15) : color.new(#50b070, 15)
projBoxClr      = isBearish ? projBoxBearClr : projBoxBullClr
eqClr           = color.new(#ffffff, 20)
lblTextClr      = color.new(#000000, 0)
tableBgClr      = color.new(#2a2d36, 15)
tableBorderClr  = color.new(#4a4d56, 40)
tableHeaderClr  = isBearish ? color.new(#8b4040, 30) : color.new(#408b60, 30)

// ============================= Helpers =============================
f_textSize(s) =>
    s == "tiny" ? size.tiny : s == "small" ? size.small : s == "large" ? size.large : s == "huge" ? size.huge : size.normal

f_fracLabel(idx, divisions) =>
    if divisions == 4
        switch idx
            1 => "1/4"
            2 => "2/4"
            3 => "3/4"
            => ""
    else
        switch idx
            1 => "1/8"
            2 => "2/8"
            3 => "3/8"
            4 => "4/8"
            5 => "5/8"
            6 => "6/8"
            7 => "7/8"
            => ""

f_price(p) =>
    str.tostring(p, format.mintick)

f_floor_to_tick(p) =>
    math.floor(p / syminfo.mintick) * syminfo.mintick

f_ceil_to_tick(p) =>
    math.ceil(p / syminfo.mintick) * syminfo.mintick

txtSize = f_textSize(generalTextSize)

// ============================= Session Logic =============================
tz        = "America/New_York"
nyHour    = hour(time, tz)
nyMinute  = minute(time, tz)
inSession = (nyHour > 9 or (nyHour == 9 and nyMinute >= 30)) and nyHour < 17

prevNyHour    = hour(time[1], tz)
prevNyMinute  = minute(time[1], tz)
prevInSession = (prevNyHour > 9 or (prevNyHour == 9 and prevNyMinute >= 30)) and nyHour[1] < 17

newSession = inSession and not prevInSession
newDay     = dayofweek != dayofweek[1]
newSession := newSession or (inSession and newDay and not prevInSession)

var float sessHigh      = na
var float sessLow       = na
var int   sessStartTime = na

var float projWindowHigh = na
var float projWindowLow  = na

var float[] projBarHighs = array.new_float()
var float[] projBarLows  = array.new_float()

curDayEndTime      = timestamp(tz, year(time, tz), month(time, tz), dayofmonth(time, tz), endHour, endMinute)
inProjectionWindow = inSession and time <= curDayEndTime

if newSession
    sessHigh       := high
    sessLow        := low
    sessStartTime  := time
    projWindowHigh := na
    projWindowLow  := na
    array.clear(projBarHighs)
    array.clear(projBarLows)

if inSession and not na(sessHigh)
    sessHigh := math.max(sessHigh, high)
    sessLow  := math.min(sessLow, low)

if inProjectionWindow
    projWindowHigh := na(projWindowHigh) ? high : math.max(projWindowHigh, high)
    projWindowLow  := na(projWindowLow) ? low : math.min(projWindowLow, low)

    if barstate.isnew
        array.push(projBarHighs, high)
        array.push(projBarLows, low)
    else if array.size(projBarHighs) > 0
        int lastProjIdx = array.size(projBarHighs) - 1
        array.set(projBarHighs, lastProjIdx, high)
        array.set(projBarLows, lastProjIdx, low)

// ============================= PO3 Range Calculation =============================
refPrice  = isBearish ? nz(projWindowHigh, sessHigh) : nz(projWindowLow, sessLow)
po3Float  = float(po3Number)
rangeIdx  = math.floor(nz(refPrice) / po3Float)
rLow      = rangeIdx * po3Float
rHigh     = (rangeIdx + 1) * po3Float
rEQ       = (rLow + rHigh) / 2.0
halfRange = po3Float / 2.0

float srcHigh = na
float srcLow  = na
float rSize   = na

if useHalfRange
    if isBearish
        srcHigh := rEQ
        srcLow  := rLow
        rSize   := halfRange
    else
        srcHigh := rHigh
        srcLow  := rEQ
        rSize   := halfRange
else
    srcHigh := rHigh
    srcLow  := rLow
    rSize   := po3Float

shiftAmount = rSize / 2.0
if rangeShift == "Shift Down 1/2"
    srcHigh := srcHigh - shiftAmount
    srcLow  := srcLow  - shiftAmount
else if rangeShift == "Shift Up 1/2"
    srcHigh := srcHigh + shiftAmount
    srcLow  := srcLow  + shiftAmount

float projHigh = na
float projLow  = na
float projEQ   = na

if isBearish
    projHigh := srcHigh
    projLow  := srcLow - projectionCount * rSize
    projEQ   := (projHigh + projLow) / 2.0
else
    projLow  := srcLow
    projHigh := srcHigh + projectionCount * rSize
    projEQ   := (projHigh + projLow) / 2.0

// ============================= Drawing Arrays =============================
var box[]   allBoxes     = array.new_box()
var line[]  allLines     = array.new_line()
var label[] allLabels    = array.new_label()
var line[]  subdivLines  = array.new_line()
var label[] subdivLabels = array.new_label()
var table   lvlTable     = na

f_endTime() =>
    timestamp(tz, year(time, tz), month(time, tz), dayofmonth(time, tz), endHour, endMinute)

var int _x1 = 0
var int _x2 = 0

drawBox(bHigh, bLow, bgClr, borderClr) =>
    array.push(allBoxes, box.new(_x1, bHigh, _x2, bLow,
         xloc=xloc.bar_time, bgcolor=bgClr, border_color=borderClr, border_width=1))

drawZone(zoneHigh, zoneLow, bgClr, labelTxt) =>
    array.push(allBoxes, box.new(_x1, zoneHigh, _x2, zoneLow,
         xloc=xloc.bar_time, bgcolor=bgClr, border_color=rangeBoxBorder, border_width=1))
    if showRangeLabels
        float mid = (zoneHigh + zoneLow) / 2.0
        array.push(allLabels, label.new(_x2, mid,
             labelTxt + " " + f_price(zoneHigh) + " / " + f_price(zoneLow),
             xloc=xloc.bar_time, style=label.style_label_left,
             color=rangeLabelBg, textcolor=rangeLabelTxt, size=f_textSize(rangeLabelSize)))

// ============================= Main Draw Block =============================
if inSession and not na(srcHigh) and not na(srcLow) and not na(rSize) and not na(sessStartTime)

    if array.size(allBoxes) > 0
        for i = 0 to array.size(allBoxes) - 1
            box.delete(array.get(allBoxes, i))
    if array.size(allLines) > 0
        for i = 0 to array.size(allLines) - 1
            line.delete(array.get(allLines, i))
    if array.size(allLabels) > 0
        for i = 0 to array.size(allLabels) - 1
            label.delete(array.get(allLabels, i))
    if array.size(subdivLines) > 0
        for i = 0 to array.size(subdivLines) - 1
            line.delete(array.get(subdivLines, i))
    if array.size(subdivLabels) > 0
        for i = 0 to array.size(subdivLabels) - 1
            label.delete(array.get(subdivLabels, i))

    array.clear(allBoxes)
    array.clear(allLines)
    array.clear(allLabels)
    array.clear(subdivLines)
    array.clear(subdivLabels)

    int endTime = f_endTime()
    _x1 := sessStartTime
    _x2 := math.max(endTime, sessStartTime)

    // ============================= Source Range Box =============================
    drawBox(srcHigh, srcLow, sourceBoxClr, sourceBorderClr)

    srcEQ = (srcHigh + srcLow) / 2.0
    array.push(allLines, line.new(_x1, srcEQ, _x2, srcEQ,
         xloc=xloc.bar_time, color=eqClr, style=line.style_dashed, width=1))

    if showSourceSubdivisions
        int divisions = subdivisionType == "1/4" ? 4 : 8
        float srcRange = srcHigh - srcLow
        for j = 1 to divisions - 1
            float sLvl = srcLow + srcRange * j / divisions
            string fracTxt = f_fracLabel(j, divisions)
            if not (divisions == 8 and j == 4)
                array.push(subdivLines, line.new(_x1, sLvl, _x2, sLvl,
                     xloc=xloc.bar_time, color=subdivLineColor, style=line.style_dashed, width=1))
                array.push(subdivLabels, label.new(_x2, sLvl,
                     fracTxt + ": " + f_price(sLvl), xloc=xloc.bar_time,
                     style=label.style_label_left, color=color.new(color.white, 100),
                     textcolor=subdivLineColor, size=txtSize))

    string rlbl = useHalfRange ? str.tostring(po3Number) + " (" + str.tostring(rSize, "#.##") + " half)" : str.tostring(po3Number)
    string slbl = rangeShift == "Shift Down 1/2" ? " v1/2" : rangeShift == "Shift Up 1/2" ? " ^1/2" : ""

    float srcLblY = isBearish ? srcLow : srcHigh
    int srcLblX   = _x1 + int((_x2 - _x1) / 2)
    srcLblStyle   = isBearish ? label.style_label_down : label.style_label_up

    array.push(allLabels, label.new(srcLblX, srcLblY, "Source PO3: " + rlbl + slbl,
         xloc=xloc.bar_time, style=srcLblStyle,
         color=color.new(sourceBorderClr, 40), textcolor=lblTextClr, size=txtSize))
    array.push(allLabels, label.new(_x2, srcHigh, "Src High: " + f_price(srcHigh),
         xloc=xloc.bar_time, style=label.style_label_left,
         color=color.new(color.white, 100), textcolor=lblTextClr, size=txtSize))
    array.push(allLabels, label.new(_x2, srcEQ, "Src EQ: " + f_price(srcEQ),
         xloc=xloc.bar_time, style=label.style_label_left,
         color=color.new(color.white, 100), textcolor=color.new(#a0a0a0, 20), size=txtSize))
    array.push(allLabels, label.new(_x2, srcLow, "Src Low: " + f_price(srcLow),
         xloc=xloc.bar_time, style=label.style_label_left,
         color=color.new(color.white, 100), textcolor=lblTextClr, size=txtSize))

    // ============================= Projection Boxes =============================
    for i = 1 to projectionCount
        float bxHigh = na
        float bxLow  = na

        if isBearish
            bxHigh := srcLow - (i - 1) * rSize
            bxLow  := srcLow - i * rSize
        else
            bxLow  := srcHigh + (i - 1) * rSize
            bxHigh := srcHigh + i * rSize

        drawBox(bxHigh, bxLow, projBoxClr, projBorderClrIn)

        if showSubEQs
            float subEQ = (bxHigh + bxLow) / 2.0
            array.push(allLines, line.new(_x1, subEQ, _x2, subEQ,
                 xloc=xloc.bar_time, color=subEQClrIn, style=line.style_dotted, width=1))
            array.push(allLabels, label.new(_x2, subEQ,
                 "#" + str.tostring(i) + " EQ: " + f_price(subEQ),
                 xloc=xloc.bar_time, style=label.style_label_left,
                 color=color.new(color.white, 100), textcolor=subEQClrIn, size=txtSize))

        if i == projectionCount
            float tLvl = isBearish ? bxHigh : bxLow
            float eLvl = isBearish ? bxLow  : bxHigh

            array.push(allLines, line.new(_x1, tLvl, _x2, tLvl,
                 xloc=xloc.bar_time, color=thickLineClr, width=3, style=line.style_solid))
            array.push(allLabels, label.new(_x2, tLvl, "Terminus: " + f_price(tLvl),
                 xloc=xloc.bar_time, style=label.style_label_left,
                 color=color.new(thickLineClr, 60), textcolor=lblTextClr, size=txtSize))

            array.push(allLines, line.new(_x1, eLvl, _x2, eLvl,
                 xloc=xloc.bar_time, color=thickLineClr, width=3, style=line.style_solid))
            array.push(allLabels, label.new(_x2, eLvl, "Range Extreme: " + f_price(eLvl),
                 xloc=xloc.bar_time, style=label.style_label_left,
                 color=color.new(thickLineClr, 60), textcolor=lblTextClr, size=txtSize))

    // ============================= Intelligent Range High / Low Detection =============================
    // Candidate zones at EVERY key level: source high, EQ, low + each projection boundary and EQ
    // Formula: for bearish, level[k] = srcHigh - k * (rSize / 2), k = 0 to 2*(projectionCount+1)
    //          for bullish, level[k] = srcLow  + k * (rSize / 2), k = 0 to 2*(projectionCount+1)
    if showRangeZones and array.size(projBarHighs) > 0 and not na(projWindowHigh) and not na(projWindowLow)

        float quarterStep = rSize / 4.0
        float bandBelow = 0.111 * rSize
        float bandAbove = 0.110 * rSize
        int totalLevels = 4 * (projectionCount + 1) + 1

        float bestHighCenter = na
        float bestHighTop    = na
        float bestHighBot    = na

        float bestLowCenter  = na
        float bestLowTop     = na
        float bestLowBot     = na

        int numBars = array.size(projBarHighs)

        for k = 0 to totalLevels - 1
            float center = isBearish ? srcHigh - k * quarterStep : srcLow + k * quarterStep
            float zTop   = f_ceil_to_tick(center + bandAbove)
            float zBot   = f_floor_to_tick(center - bandBelow)

            // Check if price touched this zone during projection window
            bool touched = false
            for b = 0 to numBars - 1
                float bH = array.get(projBarHighs, b)
                float bL = array.get(projBarLows, b)
                if bH >= zBot and bL <= zTop
                    touched := true
                    break

            if touched
                if na(bestLowCenter) or center < bestLowCenter
                    bestLowCenter := center
                    bestLowTop    := zTop
                    bestLowBot    := zBot

                if na(bestHighCenter) or center > bestHighCenter
                    bestHighCenter := center
                    bestHighTop    := zTop
                    bestHighBot    := zBot

        // Draw the zones
        if not na(bestLowCenter) and not na(bestHighCenter)
            bool sameZone = math.abs(bestLowCenter - bestHighCenter) < syminfo.mintick
            if sameZone
                drawZone(bestHighTop, bestHighBot, sharedZoneClr, "Range High / Low")
            else
                drawZone(bestLowTop, bestLowBot, rangeLowClr, "Range Low")
                drawZone(bestHighTop, bestHighBot, rangeHighClr, "Range High")
        else
            if not na(bestLowCenter)
                drawZone(bestLowTop, bestLowBot, rangeLowClr, "Range Low")
            if not na(bestHighCenter)
                drawZone(bestHighTop, bestHighBot, rangeHighClr, "Range High")

    // ============================= Levels Table =============================
    if showTable
        if not na(lvlTable)
            table.delete(lvlTable)

        tPos = position.top_right
        if tablePosition == "top_left"
            tPos := position.top_left
        else if tablePosition == "top_right"
            tPos := position.top_right
        else if tablePosition == "bottom_left"
            tPos := position.bottom_left
        else
            tPos := position.bottom_right

        lvlTable := table.new(position=tPos, columns=2, rows=5,
             bgcolor=tableBgClr, border_width=1, border_color=tableBorderClr)

        string po3Lbl = useHalfRange ? str.tostring(rSize, "#.##") + " (1/2 of " + str.tostring(po3Number) + ")" : str.tostring(po3Number)
        string shTxt  = rangeShift == "Shift Down 1/2" ? " v1/2" : rangeShift == "Shift Up 1/2" ? " ^1/2" : ""

        table.cell(lvlTable, 0, 0, "PO3 Projection",
             text_color=lblTextClr, text_size=txtSize, bgcolor=tableHeaderClr)
        table.cell(lvlTable, 1, 0, bias + " | " + po3Lbl + shTxt,
             text_color=lblTextClr, text_size=txtSize, bgcolor=tableHeaderClr)

        table.cell(lvlTable, 0, 1, "PO3 Range High",
             text_color=color.new(#7ab8a0, 0), text_size=txtSize, bgcolor=color.new(#7ab8a0, 88))
        table.cell(lvlTable, 1, 1, f_price(srcHigh),
             text_color=color.new(#7ab8a0, 0), text_size=txtSize, bgcolor=color.new(#7ab8a0, 88))

        table.cell(lvlTable, 0, 2, useHalfRange ? "PO3 1/2: " + str.tostring(rSize, "#.##") : "PO3: " + str.tostring(po3Number),
             text_color=color.new(#a0a0a0, 0), text_size=txtSize, bgcolor=color.new(#a0a0a0, 88))
        table.cell(lvlTable, 1, 2, f_price(projEQ),
             text_color=color.new(#a0a0a0, 0), text_size=txtSize, bgcolor=color.new(#a0a0a0, 88))

        float termPx = isBearish ? srcLow - (projectionCount - 1) * rSize : srcHigh + (projectionCount - 1) * rSize
        table.cell(lvlTable, 0, 3, "Terminus",
             text_color=color.new(#c4a35a, 0), text_size=txtSize, bgcolor=color.new(#c4a35a, 88))
        table.cell(lvlTable, 1, 3, f_price(termPx),
             text_color=color.new(#c4a35a, 0), text_size=txtSize, bgcolor=color.new(#c4a35a, 88))

        table.cell(lvlTable, 0, 4, "Range Extreme",
             text_color=color.new(#c45050, 0), text_size=txtSize, bgcolor=color.new(#c45050, 88))
        table.cell(lvlTable, 1, 4, f_price(isBearish ? projLow : projHigh),
             text_color=color.new(#c45050, 0), text_size=txtSize, bgcolor=color.new(#c45050, 88))
