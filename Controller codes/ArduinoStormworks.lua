local port = 5000
local url = "/arduino_data"

local bool_in = {false, false, false, false}
local digit_in = {0, 0, 0, 0}

local bool_out = {false, false, false, false}
local digit_out = {0, 0, 0, 0}

local tick_counter = 0

function parseData(response_body)
    local result = {}
    for key, value in response_body:gmatch('"([^"]+)":([^,}]+)') do
        value = value:gsub("[^%d]", "")
        result[key] = tonumber(value) or 0
    end
    return result
end

function updateOutputs(data)
    for i = 1, 4 do
        bool_out[i] = data["bool_out" .. i] == 1
    end
    for i = 5, 8 do
        digit_out[i - 4] = data["digit_out" .. i] or 0
    end
end

function onTick()
    tick_counter = tick_counter + 1

    if tick_counter % 6 == 0 then
        tick_counter = 0
        async.httpGet(port, url .. "?bool_in1=" .. (input.getBool(1) and 1 or 0) ..
                              "&bool_in2=" .. (input.getBool(2) and 1 or 0) ..
                              "&bool_in3=" .. (input.getBool(3) and 1 or 0) ..
                              "&bool_in4=" .. (input.getBool(4) and 1 or 0) ..
                              "&digit_in5=" .. string.format("%.2f", input.getNumber(5)) ..
                              "&digit_in6=" .. string.format("%.2f", input.getNumber(6)) ..
                              "&digit_in7=" .. string.format("%.2f", input.getNumber(7)) ..
                              "&digit_in8=" .. string.format("%.2f", input.getNumber(8)))
        for i = 1, 4 do
	        output.setBool(i, bool_out[i])
	    end
	    for i = 5, 8 do
	        output.setNumber(i, digit_out[i - 4])
	    end
    end
end

function httpReply(port, request_body, response_body)
    local data = parseData(response_body)
    if data then
        updateOutputs(data)
    end
end
