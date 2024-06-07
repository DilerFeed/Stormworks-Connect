local port = 5000
local url_frame = "/gif_frame/"
local url_frame_count = "/gif_frame_count"
local gif_frames = {}
local current_frame_index = 0
local is_fetching = false
local frame_count = 0
local transfer_complete = false
local transfer_in_progress = false
local frame_delay = 0.1
local frame_timer = 0
local transfer_progress = 0

function onTick()
    if input.getBool(1) and not is_fetching and not transfer_in_progress then
        async.httpGet(port, url_frame_count)
        transfer_in_progress = true
        transfer_complete = false
        current_frame_index = 0
        gif_frames = {}
        transfer_progress = 0
    end

    if is_fetching then
        if current_frame_index < frame_count then
            async.httpGet(port, url_frame .. current_frame_index)
            current_frame_index = current_frame_index + 1
        else
            is_fetching = false
        end
    end

    if transfer_complete then
        output.setBool(1, true)
    else
        output.setBool(1, false)
    end

    if transfer_complete and not is_fetching then
        frame_timer = frame_timer + 1 / 60
        if frame_timer >= frame_delay then
            frame_timer = frame_timer - frame_delay
            current_frame_index = (current_frame_index + 1) % frame_count
        end
    end
end

function httpReply(port, request_body, response_body)
    if request_body:match(url_frame_count) then
        frame_count = tonumber(response_body)
        if frame_count and frame_count > 0 then
            is_fetching = true
            current_frame_index = 0
            transfer_progress = 0
        else
            transfer_in_progress = false
        end
    else
        local frame_index = tonumber(request_body:match(url_frame .. "(%d+)"))
        if frame_index then
            gif_frames[frame_index] = response_body
            transfer_progress = frame_index / frame_count
            if frame_index == frame_count - 1 then
                transfer_complete = true
                transfer_in_progress = false
                transfer_progress = 1
            end
        end
    end
end

function draw_progress_bar(percentage)
    local width = screen.getWidth()
    local height = screen.getHeight()
    local bar_width = math.floor(width * percentage)
    screen.setColor(0, 0, 0)
    screen.drawRectF(0, 0, width, height)
    screen.setColor(0, 255, 0)
    screen.drawRectF(0, height - 10, bar_width, 10)
    screen.setColor(255, 255, 255)
    screen.drawTextBox(0, height - 20, width, 10, string.format("%d%%", math.floor(percentage * 100)), 0, 0)
end

function onDraw()
    if transfer_in_progress then
        draw_progress_bar(transfer_progress)
    elseif transfer_complete then
        local frame_data = gif_frames[current_frame_index]
        if frame_data then
            local y = 0
            for line in string.gmatch(frame_data, "[^\n]+") do
                local x = 0
                for r, g, b in string.gmatch(line, "(%d+) (%d+) (%d+)") do
                    --    3
                    r, g, b = tonumber(r) / 3, tonumber(g) / 3, tonumber(b) / 3
                    screen.setColor(r, g, b)
                    screen.drawRectF(x, y, 1, 1)
                    x = x + 1
                end
                y = y + 1
            end
        end
    else
        screen.setColor(255, 255, 255)
        screen.drawTextBox(0, 0, screen.getWidth(), screen.getHeight(), "Press button to start GIF transfer", 0, 0)
    end
end
