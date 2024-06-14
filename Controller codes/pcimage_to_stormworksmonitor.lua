local port = 5000
local url = "/column"
local image_data = {}
local image_width = 288
local image_height = 160
local current_column = 0
local is_fetching = false

function onTick()
    if input.getBool(1) and not is_fetching then
        is_fetching = true
        current_column = 0
    end

    if is_fetching then
        if current_column < image_width then
            async.httpGet(port, url .. "?x=" .. current_column)
            current_column = current_column + 1
        else
            is_fetching = false
        end
    end
end

function httpReply(port, request_body, response_body)
    local x = request_body:match("x=(%d+)")
    x = tonumber(x)
    if x then
        image_data[x] = {}
        for y, line in ipairs(split(response_body, "\n")) do
            local r, g, b = line:match("(%d+) (%d+) (%d+)")
            r, g, b = tonumber(r), tonumber(g), tonumber(b)
            image_data[x][y] = {r, g, b}
        end
    end
end

function split(inputstr, sep)
    if sep == nil then
        sep = "%s"
    end
    local t = {}
    for str in string.gmatch(inputstr, "([^" .. sep .. "]+)") do
        table.insert(t, str)
    end
    return t
end

function onDraw()
    for x, column in pairs(image_data) do
        for y, pixel in ipairs(column) do
            local screen_x = x - 1
            local screen_y = y - 1
            if type(pixel) == "table" then
                screen.setColor(pixel[1], pixel[2], pixel[3])
                screen.drawRectF(screen_x, screen_y, 1, 1)
            end
        end
    end
end