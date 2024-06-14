-- this code is minified
query=""
response=""
fetch=false
scroll_cooldown=0
scroll_delay=30
viewing_page=false
page_content=""
current_page_index=0
selected_link_index=-1
touch_delay=20
touch_timer=0
is_loading=false
status_check_delay=100
status_check_timer=0
screen_width=0
screen_height=0
touch_x=0
touch_y=0
prev_touch_x=0
prev_touch_y=0
search_in_progress=false
function resetVariables()
response=""
fetch=false
scroll_cooldown=0
viewing_page=false
page_content=""
current_page_index=0
selected_link_index=-1
touch_timer=0
is_loading=false
status_check_timer=0
search_in_progress=false
end

function onTick()
screen_width=input.getNumber(1)
screen_height=input.getNumber(2)
touch_x=input.getNumber(3)
touch_y=input.getNumber(4)
scroll_up=input.getBool(2)
scroll_down=input.getBool(3)
enter_pressed=input.getBool(1)
if enter_pressed then
resetVariables()
search_in_progress=true
async.httpGet(5000,"/search_status"
)
end
if scroll_cooldown==0 then
if scroll_up then
if viewing_page then
current_page_index=math.max(0,current_page_index-1)
async.httpGet(5000,"/page_part?index="
..current_page_index)else async.httpGet(5000,"/scroll?direction=up"
)
end
scroll_cooldown=scroll_delay
elseif scroll_down then
if viewing_page then
current_page_index=current_page_index+1
async.httpGet(5000,"/page_part?index="
..current_page_index)else async.httpGet(5000,"/scroll?direction=down"
)
end
scroll_cooldown=scroll_delay
end
else scroll_cooldown=scroll_cooldown-1 
end
if not viewing_page then
if touch_x~=0 and touch_y~=0 and(touch_x~=prev_touch_x or touch_y~=prev_touch_y)then
checkTouch(touch_x,touch_y)
elseif selected_link_index~=-1 and not is_loading then
async.httpGet(5000,"/page_content?url="
..response_links[selected_link_index])
viewing_page=true
selected_link_index=-1
touch_timer=0
is_loading=true
end
end
prev_touch_x=touch_x
prev_touch_y=touch_y
if is_loading and status_check_timer<=0 then
async.httpGet(5000,"/page_status"
)
status_check_timer=status_check_delay
end
if status_check_timer>0 then
status_check_timer=status_check_timer-1 
end
end

function checkTouch(a,b)
local c=30
local d=math.floor(b/c)*2+2
local e={}
for f in string.gmatch(response,"([^\n]+)"
)do
table.insert(e,f)
end
if e[d]then
selected_link_index=d
touch_timer=touch_timer+1
if touch_timer>touch_delay then
async.httpGet(5000,"/page_content?url="
..e[d])
viewing_page=true
selected_link_index=-1
touch_timer=0
is_loading=true
end
else selected_link_index=-1
touch_timer=0
end
touch_x=0
touch_y=0
end

function httpReply(g,h,i)
if g==5000 then
if viewing_page then
if string.find(i,'"status": "loading"'
)then
page_content="Loading..."
elseif string.find(i,'"status": "loaded"'
)then
is_loading=false
status_check_timer=0
async.httpGet(5000,"/page_part?index="
..current_page_index)else page_content=i
is_loading=false
end
else 
if string.find(i,'"status": "searching"'
)then
async.httpGet(5000,"/search_status"
)
elseif string.find(i,'"status": "complete"'
)then
async.httpGet(5000,"/result"
)
search_in_progress=false
else response=i
search_in_progress=false
end
end
end
end

function onDraw()
screen.setColor(0,0,0)
screen.drawRectF(0,0,screen.getWidth()
,screen.getHeight()
)
if search_in_progress then
drawLoading()
elseif viewing_page then
drawPageContent()
else drawSearchResults()
end
end

function drawLoading()
screen.setColor(255,255,255)
screen.drawText(screen_width/2-30,screen_height/2-5,"Loading..."
)
end

function drawSearchResults()
local e={}
for f in string.gmatch(response,"([^\n]+)"
)do
table.insert(e,f)
end
local b=0
for j=1,#e,2 do
if e[j]then
screen.setColor(0,0,255)
screen.drawText(5,b,e[j])
end
b=b+10
if e[j+1]then
if selected_link_index==j+1 then
screen.setColor(128,128,128)else screen.setColor(255,255,255)
end
screen.drawText(5,b,e[j+1])
end
b=b+20 
end
end

function drawPageContent()
local e={}
for f in string.gmatch(page_content,"([^\n]+)"
)do
table.insert(e,f)
end
local b=0
for j=1,#e do
screen.setColor(255,255,255)
screen.drawText(5,b,e[j])
b=b+10 
end
end
