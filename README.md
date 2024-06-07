**New version v1.1.1.0 is out!**

# Stormworks-Connect
>A multifunctional application for the Stormworks game, allowing the player to exchange data with the real world directly from the game.

![SC_loading_screen](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/8cf1a61f-1e31-47e4-a362-ea75258e27b5)

At the moment, the application has just been born, but is under active development, so new updates are released frequently, as are new features. Don't miss it!

You can find all the controllers that are needed for all program functions to work here - https://steamcommunity.com/sharedfiles/filedetails/?id=3261136897

#

## 1. Transmit any image from your computer to any monitor in the game
In the "Image transmit" tab, in the "Image Transmit" section, simply select the monitor size you currently want to transfer the image to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the image onto the monitor into the controller, it will receive this image and display it on the monitor. Rendering is performed by batch requests that transfer the image in vertical lines in parts.
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

## 3. Transmit any GIF from your computer to any monitor in the game
In the "Image transmit" tab, in the "GIF Transmit" section, simply select the monitor size you currently want to transfer the GIF to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the GIF onto the monitor into the controller, it will start downloading the GIF in parts until it has loaded all its frames into its memory, after which it will begin to play it at the speed of the original. Rendering is performed by batch requests that transfer the gif into parts of frames, after which controller combines parts of the frames into full-fledged frames, and then combines the full-fledged frames into a full-fledged gif. All this happens simultaneously, forming a very efficient algorithm that can transfer megabytes of information in a few seconds.
You need this controller to get the GIF in the game - https://steamcommunity.com/sharedfiles/filedetails/?id=3262978714

![2024-06-0715-20-41-ezgif com-video-to-gif-converter](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/1466cb98-4ba1-488f-9a7e-9f8c9ddf6254)
![2024-06-0715-21-30-ezgif com-video-to-gif-converter](https://github.com/DilerFeed/Stormworks-Connect/assets/33964247/800633ad-96ca-4111-9f26-04ee8340e4a0)

Watch the video to understand how it works:
[![Watch the video to understand how it works](https://img.youtube.com/vi/2FSNrqv12NU/0.jpg)](https://www.youtube.com/watch?v=2FSNrqv12NU)

# Use GitHub releases to download

### All changes from the latest update (v1.1.1.0):
* Now the "Image transmit" tab is divided into two sections: "Image transmit" and "GIF Transmit", which are responsible for the separate functions of transferring regular pictures and transferring GIFs, respectively.
* Now in the "Image transmit" section you can only upload regular images like png, jpg, jpeg, and in the "GIF Transmit" section only gifs. Now the program cannot break in this place.
* New functionality - transferring any GIFs to any monitor in the game. In the "Image transmit" tab, in the "GIF Transmit" section, simply select the monitor size you currently want to transfer the GIF to, check the "fill" box if necessary and upload your image. After pressing the signal button to load the GIF onto the monitor into the controller, it will start downloading the GIF in parts until it has loaded all its frames into its memory, after which it will begin to play it at the speed of the original. Rendering is performed by batch requests that transfer the gif into parts of frames, after which controller combines parts of the frames into full-fledged frames, and then combines the full-fledged frames into a full-fledged gif. All this happens simultaneously, forming a very efficient algorithm that can transfer megabytes of information in a few seconds.
* Now, if a new update has been released, when you receive a notification that it has been released, you can click the "Don't remind me again" button. After this, you will no longer be reminded that a new version of the program has been released.
* In the "Steering wheel" tab, it is now impossible to check the "Swap Gas and Brake Pedals" checkbox if the "Combined Pedals" checkbox is checked, since the program previously did not support the operation of these functionalities at the same time and could break.
* Now ALL settings in the "Steering wheel" tab are saved in a special configuration file in the program folder and after restarting the program they will not be reset to default values. This means that now you only need to set the controls for your steering wheel once.
* A new "Support" tab has been added, where you will find a button that will take you to my page on buymeacoffee.com, where you can support my work if you like it.
