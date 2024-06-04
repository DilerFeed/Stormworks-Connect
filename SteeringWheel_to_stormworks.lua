local port = 5000
local url = "/controller_data"

local steering_angle = 0
local gas_pedal = 0
local brake_pedal = 0
local shift_up = false
local shift_down = false
local custom_button_1 = false
local custom_button_2 = false
local custom_button_3 = false
local custom_button_4 = false

function parseData(dataString)
    local result = {}
    for line in dataString:gmatch("[^\r\n]+") do
        local key, value = line:match("([^=]+)=([^=]+)")
        if key and value then
            result[key] = tonumber(value) or (value == "true")
        end
    end
    return result
end

function onTick()
    async.httpGet(port, url)

    --    
    output.setNumber(1, steering_angle)
    output.setNumber(2, gas_pedal)
    output.setNumber(3, brake_pedal)
    output.setBool(4, shift_up)
    output.setBool(5, shift_down)
    output.setBool(6, custom_button_1)
    output.setBool(7, custom_button_2)
    output.setBool(8, custom_button_3)
    output.setBool(9, custom_button_4)
end

function httpReply(port, request_body, response_body)
    local data = parseData(response_body)
    if data then
        steering_angle = data.steering_angle or 0
        gas_pedal = data.gas_pedal or 0
        brake_pedal = data.brake_pedal or 0
        shift_up = data.shift_up == 1
        shift_down = data.shift_down == 1
        custom_button_1 = data.custom_button_1 == 1
        custom_button_2 = data.custom_button_2 == 1
        custom_button_3 = data.custom_button_3 == 1
        custom_button_4 = data.custom_button_4 == 1
    end
end
