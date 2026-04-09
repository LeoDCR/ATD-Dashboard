This document is about all the important decisions and why they were taken


V 1.2:

- Decided to run the UI code locally on the PC. Pushing to the Raspberry Pi for every small color or pixel change in the QML was a pain and took way too long.
- Left an overlapping number bug on the speedometer for now. The main goal right now is just to get the general layout and shapes working. I'll fix the text issues later.


V 1.3:

- Big visual upgrade: Moved away from simple text elements and implemented QML `Canvas` to draw a dynamic, color-changing arc for the RPMs and added shapes for battery and temp indicators. It looks way better for the bike.
- To test the animations without wiring up the Pico or writing complex Python logic yet, I added a mock data `Timer` directly inside the `dashboard.qml` file. This simulates the bike revving up and down so I can see the UI reacting in real-time.
- Fixed the overlapping text bug on the speedometer by cleaning up the QML layouts.