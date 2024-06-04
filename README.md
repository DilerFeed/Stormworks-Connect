# Stormworks-Connect
>A multifunctional application for the Stormworks game, allowing the player to exchange data with the real world directly from the game.

![SC_loading_screen](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/8cf1a61f-1e31-47e4-a362-ea75258e27b5)

At the moment, the application has just been born, , but is under active development, so new updates are released frequently, as are new features. Don't miss it!

#

## 1. Transmit any image from your computer to any monitor in the game
In the "Image transmit" tab, simply select the monitor size you currently want to transfer the image to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the image onto the monitor into the controller, it will receive this image and display it on the monitor. Rendering is performed by batch requests that transfer the image in vertical lines in parts.
You need this controller to get the image in the game - https://steamcommunity.com/sharedfiles/filedetails/?id=3256896125

![Знімок екрана 2024-06-04 140627](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/a0b456ab-7f85-443f-b47f-d051b31e5748)
![Знімок екрана 2024-06-04 153939](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/5fbbf182-c634-454a-b214-6f7b754b6b10)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/yDV3IyEmLcY/0.jpg)](https://www.youtube.com/watch?v=yDV3IyEmLcY)

## 2. Connect any steering wheel with pedals to the game
In the "Steering wheel" tab, select your steering wheel from above. All axes and buttons will be assigned automatically. But automatic assignment can be wrong, so it is possible to manually assign the steering wheel, pedals and buttons. To do this, simply click on the button to assign the functionality you need and follow the instructions in the new window. Supports pedal inversion and composite pedal mode, where the gas and brake pedals have a single output. Supports 6 custom buttons, 2 of which count as gear shift (use only with paddle shift or simple forward plus/reverse minus gearbox). Data transfer occurs thanks to http requests.
You need this controller to work with this feature - https://steamcommunity.com/sharedfiles/filedetails/?id=3261140680

![Знімок екрана 2024-06-04 151055](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/593d4b62-78fb-465b-b9d0-93f88be6a93d)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/JS2815DQp7o/0.jpg)](https://www.youtube.com/watch?v=JS2815DQp7o)

# Use GitHub releases to download

I understand that questions may arise regarding why I did not leave the code for the program that you are downloading here. Well, the thing is that I want to develop this program further and for now I don’t want to reveal the principle of its operation, although I am sure that people who understand at least a little about programming will already understand it from the lua code of the controller.

#

### All changes from the latest update (v1.1.0.0):
* The program code has been completely redesigned, now it supports an object-oriented approach and can be easily extended.
* Now the program has a tab structure that will allow you to add a lot of new functionality. Tabs for this update: "Image transmit", "Steering wheel", "Info".
* The program now also supports dark theme. The theme is installed automatically at startup to the same as the system one, but can be changed in the "Info" tab.
* All information that was related to the operation of the local server of the application, its version, authorship and links to the author’s profiles were transferred to the “Info” tab.
* All functionality for transmitting images has been moved to the “Image transmit” tab.
* Added new functionality that allows you to connect any steering wheel with pedals to the Stormworks game in the "Steering wheel" tab. To connect, it is enough for the steering wheel to work like a joystick (most likely they all work like this).
* In the "Steering wheel" tab, select your steering wheel from above. All axes and buttons will be assigned automatically. But automatic assignment can be wrong, so it is possible to manually assign the steering wheel, pedals and buttons. To do this, simply click on the button to assign the functionality you need and follow the instructions in the new window. Supports pedal inversion and composite pedal mode, where the gas and brake pedals have a single output. Supports 6 custom buttons, 2 of which count as gear shift (use only with paddle shift or simple forward plus/reverse minus gearbox).
* Starting from this version, when you start the program, if you have access to the Internet, the program will inform you that a new version has been released, if indeed one has been released.
