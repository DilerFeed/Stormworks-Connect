-- based on https://steamcommunity.com/sharedfiles/filedetails/?id=2435189048

kb = {
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm "
}

res = ""
holdThreshold = 30
hold = 0
holdX = 0
holdY = 0
isPressed = false
scroll_up = false
scroll_down = false

function urlEncode(str)
    if str then
        str = string.gsub(str, "\n", "\r\n")
        str = string.gsub(str, "([^%w %-%_%.%~])",
            function (c) return string.format("%%%02X", string.byte(c)) end)
        str = string.gsub(str, " ", "%%20")
    end
    return str    
end

function onTick()
    inputX = input.getNumber(3)
    inputY = input.getNumber(4)
    isPressed = input.getBool(1)
    scroll_up = input.getBool(2)
    scroll_down = input.getBool(3)
    output.setBool(1, enter)
    if isPressed then
        hold = hold + 1
        holdX = inputX
        holdY = inputY
    else
        hold = 0
    end

    if enter then
        local query = ""
        for i = 1, #res do
            query = query .. string.byte(res, i) .. " "
        end
        query = string.sub(query, 1, -2)
        query = urlEncode(query)
        async.httpGet(5000, "/search?query=" .. query)
        enter = false
    end

    if scroll_up then
        async.httpGet(5000, "/scroll?direction=up")
    elseif scroll_down then
        async.httpGet(5000, "/scroll?direction=down")
    end
end

function isPointInRectangle(x, y, rectX, rectY, rectW, rectH)
    return x > rectX and y > rectY and x < rectX + rectW and y < rectY + rectH
end

function drawButton(x, y, w, h, content, screen, recall, holdRecall, param)
    screen.setColor(30, 30, 30)
    onButton = 0
    if isPressed and isPointInRectangle(inputX, inputY, x - 1, y, w, h) then
        onButton = 1
        screen.setColor(100, 100, 100)
        if hold > holdThreshold then
            screen.setColor(200, 0, 0)
        end
    else
        if hold > holdThreshold and not holdRecall == false and isPointInRectangle(holdX, holdY, x - 1, y, w, h) then
            holdRecall(param)
            hold = 0
            holdX = 0
            holdY = 0
        elseif isPointInRectangle(holdX, holdY, x - 1, y, w, h) then
            recall(param)
            hold = 0
            holdX = 0
            holdY = 0
        end
    end
    screen.drawRectF(x, y, w, h)
    screen.setColor(255, 255, 255)
    screen.drawTextBox(x + 1, y + 1, w - 1, h - 1, content, 0, 0)
    return onButton
end

function emptyFunc() end
function appendChar(chr)
    res = res .. chr
end
function backSpace(nouse)
    res = string.sub(res, 1, -2)
end
function enterKey(nouse)
    enter = true
end

function onDraw()
    w = screen.getWidth()
    h = screen.getHeight()

    screen.setColor(0, 100, 0)
    screen.drawText(5, h / 2 - 9, res)
    screen.drawLine(5, h / 2 - 3, w - 5, h / 2 - 3)

    yShift = h / 2 + 7
    xShift = {7, 7, 9, 11}

    drawButton(w - 20, h / 2, 12, 5, "BS", screen, backSpace, false, false)
    drawButton(xShift[1], h / 2, 12, 5, "En", screen, enterKey, false, false)

    for yAxis = 1, 4 do
        for xAxis = 1, #kb[yAxis] do
            chr = string.sub(kb[yAxis], xAxis, xAxis)
            drawButton(xShift[yAxis] + (xAxis - 1) * 5, yShift + (yAxis - 1) * 6, 4, 5, chr, screen, appendChar, false, chr)
        end
    end
end
