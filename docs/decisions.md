This document is about all the important decisions and why they were taken


V 1.2:

- Decided to run the UI code locally on the PC. Pushing to the Raspberry Pi for every small color or pixel change in the QML was a pain and took way too long.
- Left an overlapping number bug on the speedometer for now. The main goal right now is just to get the general layout and shapes working. I'll fix the text issues later.


V 1.3:

- Big visual upgrade: Moved away from simple text elements and implemented QML `Canvas` to draw a dynamic, color-changing arc for the RPMs and added shapes for battery and temp indicators. It looks way better for the bike.
- To test the animations without wiring up the Pico or writing complex Python logic yet, I added a mock data `Timer` directly inside the `dashboard.qml` file. This simulates the bike revving up and down so I can see the UI reacting in real-time.
- Fixed the overlapping text bug on the speedometer by cleaning up the QML layouts.


V 1.4:

- **The Big Disconnect:** Turned off the mock data `Timer` inside the QML. The frontend is no longer faking the numbers.
- **Python Integration:** Established the real connection between the QML frontend and the Python backend using QML `Connections` targeting the `backend` context property. Now, Python pushes the data, and QML just listens and updates the UI.
- **UI Tweaks:** Added the high/low beam indicators with custom drawn shapes (4 rays instead of a generic icon) and implemented a 10-bar style fuel gauge instead of a boring percentage text. It looks much more "cyberpunk/racing" now.

![First dashboard run](images/design4.png)