**Version 1.2.0.0 is out!**

# Stormworks-Connect
>A multifunctional application for the Stormworks game, allowing the player to exchange data with the real world directly from the game.

![SC_loading_screen](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/8cf1a61f-1e31-47e4-a362-ea75258e27b5)

At the moment, the application has just been born, but is under active development, so new updates are released frequently, as are new features. Don't miss it!

You can find all the controllers that are needed for all program functions to work here - https://steamcommunity.com/sharedfiles/filedetails/?id=3261136897

#

## 1. Transmit any image from your computer to any monitor in the game
In the "Image transmit" tab, in the "Image Transmit" section, simply select the monitor size you currently want to transfer the image to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the image onto the monitor into the controller, it will receive this image and display it on the monitor. Rendering is performed by batch requests that transfer the image in vertical lines in parts.
You need this controller to get the image in the game - https://steamcommunity.com/sharedfiles/filedetails/?id=3256896125

![Знімок екрана 2024-06-14 143744](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/a249e8a4-0560-4852-8aa9-29a4975f2c38)
![Знімок екрана 2024-06-14 144519](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/5708533b-ad04-4c93-bd85-3c1ada59ac8e)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/yDV3IyEmLcY/0.jpg)](https://www.youtube.com/watch?v=yDV3IyEmLcY)

## 2. Connect any steering wheel with pedals to the game
In the "Steering wheel" tab, select your steering wheel from above. All axes and buttons will be assigned automatically. But automatic assignment can be wrong, so it is possible to manually assign the steering wheel, pedals and buttons. To do this, simply click on the button to assign the functionality you need and follow the instructions in the new window. Supports pedal inversion and composite pedal mode, where the gas and brake pedals have a single output. Supports 6 custom buttons, 2 of which count as gear shift (use only with paddle shift or simple forward plus/reverse minus gearbox). Data transfer occurs thanks to http requests.
You need this controller to work with this feature - https://steamcommunity.com/sharedfiles/filedetails/?id=3261140680

![Знімок екрана 2024-06-04 151055](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/593d4b62-78fb-465b-b9d0-93f88be6a93d)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/JS2815DQp7o/0.jpg)](https://www.youtube.com/watch?v=JS2815DQp7o)

## 3. Transmit any GIF from your computer to any monitor in the game
In the "Image transmit" tab, in the "GIF Transmit" section, simply select the monitor size you currently want to transfer the GIF to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the GIF onto the monitor into the controller, it will start downloading the GIF in parts until it has loaded all its frames into its memory, after which it will begin to play it at the speed of the original. Rendering is performed by batch requests that transfer the gif into parts of frames, after which controller combines parts of the frames into full-fledged frames, and then combines the full-fledged frames into a full-fledged gif. All this happens simultaneously, forming a very efficient algorithm that can transfer megabytes of information in a few seconds.
You need this controller to get the GIF in the game - https://steamcommunity.com/sharedfiles/filedetails/?id=3262978714

![2024-06-0715-20-41-ezgif com-video-to-gif-converter](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/1466cb98-4ba1-488f-9a7e-9f8c9ddf6254)
![2024-06-0715-21-30-ezgif com-video-to-gif-converter](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/800633ad-96ca-4111-9f26-04ee8340e4a0)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/2FSNrqv12NU/0.jpg)](https://www.youtube.com/watch?v=2FSNrqv12NU)

## 4. The first ever working in-game (text) web browser in Stormworks
Just run the program, then subscribe to the in-game browser page in the workshop. In the list of buildings (vehicles), you will see a corresponding building that contains 2 controllers and a monitor, correctly connected to each other. You can use them separately, just go to the edit menu of one of the controllers and save, but building for a subscription will help you understand how to connect them correctly. Type your query on the small monitor and press EN (Enter), you can also use the BS button to delete entered characters. After pressing Enter, the program will process your request and send a list of 50 answers to your search query to the second controller, which will draw them on the monitor. Use the scroll buttons marked in blue (to the left of the keyboard) to navigate through the list of search results. Touch the desired search result on your monitor to read the contents of that page. The browser only supports text content, so that's what you'll see. Text content is displayed in pieces of approximately 500 characters without breaking words, which can also be scrolled through with the same scrolling buttons, so you can read ALL text content of any page.
You need this building, consisting of two controllers and the components necessary for them, in order to try out this feature - https://steamcommunity.com/sharedfiles/filedetails/?id=3267509700

![Знімок екрана 2024-06-13 144159](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/3767343f-65b1-4f55-9175-b05207738b36)
![Знімок екрана 2024-06-13 144316](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/590ecd8c-a6d0-44c6-a6d3-a1d4806ee950)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/bTid7PzwMoY/0.jpg)](https://www.youtube.com/watch?v=bTid7PzwMoY)
###
Well, how is this really possible? How is it possible to implement a web browser in a game where you can only write code that does not have access to the Internet?

So look at the picture. When you type a query on the keyboard and press the Enter button, the keyboard controller encodes the query in ASCII, then sends it in an http request to the application, and also notifies the web browser controller that a new search query has been sent. The web browser controller goes into wait mode for search results, at which time the program uses Google search to receive results for your request. When all the results are received, the program sends a response to the web browser controller that the search results have been received and at the same time sends the first batch of 3 results. At this moment, the web browser controller goes into the status of viewing search results; it expects either clicks on the scroll buttons, or clicks on the monitor on one of the search results. If one of the scrolling buttons was pressed, the web browser controller sends an http request to the program to receive the other 3 search results depending on the current index of the search results page. If a touch click was made on one of the search results, the controller sends an http request to the program to parse the text content of the search result at a certain index, and at this moment goes into a waiting state. When the parsing is successful, the program breaks it into 500-character pieces so that there are no word breaks, and also converts continuous lines into separate lines to fill more monitor space with text. After this, the program sends a response to the web browser controller that the text is ready to be sent and at the same time sends the first piece of formatted text. The web browser controller takes this piece and displays it on the screen. At this moment, the web browser controller goes into mode for viewing the text content of the page - it expects either a click on the scroll buttons or a new search query, which it can learn about from a signal from the keyboard controller. If one of the scrolling buttons was pressed, the web browser controller sends an http request to the program to receive another piece of text depending on the current index of the text piece of the page content. If a signal is received from the keyboard controller, the current state of the web browser controller is reset and it goes to the initial state where it again expects results from the program. And so on and so forth.

![wb_sc](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/25ea593e-499c-4b53-86d8-178d1be38b2e)

# Use GitHub releases to download

### All changes from the latest update (v1.2.0.0):
* Now in the "Image transmit" tab you can upload images and GIFs both from computer files and via a link from the Internet.
* Now all tabs also have an icon next to their name, which adds beauty to the program and can be simply convenient.
* New functionality - the first ever working in-game (text) web browser in Stormworks. Just run the program, then subscribe to the in-game browser page in the workshop. In the list of buildings (vehicles), you will see a corresponding building that contains 2 controllers and a monitor, correctly connected to each other. You can use them separately, just go to the edit menu of one of the controllers and save, but building for a subscription will help you understand how to connect them correctly. Type your query on the small monitor and press EN (Enter), you can also use the BS button to delete entered characters. After pressing Enter, the program will process your request and send a list of 50 answers to your search query to the second controller, which will draw them on the monitor. Use the scroll buttons marked in blue (to the left of the keyboard) to navigate through the list of search results. Touch the desired search result on your monitor to read the contents of that page. The browser only supports text content, so that's what you'll see. Text content is displayed in pieces of approximately 500 characters without breaking words, which can also be scrolled through with the same scrolling buttons, so you can read ALL text content of any page.
* The "Info" tab is now divided into two halves. The left side contains the same functionality that was previously in the "Info" tab. The right side is new and contains a list of functionality that the program has. Click on the functionality you are interested in and this will open in the browser in the workshop the page of the controller that is needed for its operation.

### Credits:
* GIF in the support tab https://tenor.com/gy0XRBe3HbB.gif
* <a href="https://www.flaticon.com/free-icons/steering-wheel" title="steering-wheel icons">Steering-wheel icons created by Mayor Icons - Flaticon</a>
* <a href="https://www.flaticon.com/free-icons/thumbnail" title="thumbnail icons">Thumbnail icons created by Mayor Icons - Flaticon</a>
* <a href="https://www.flaticon.com/free-icons/info" title="info icons">Info icons created by afif fudin - Flaticon</a>
* <a href="https://www.flaticon.com/free-icons/coin" title="coin icons">Coin icons created by Mayor Icons - Flaticon</a>
