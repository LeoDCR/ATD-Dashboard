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


## V 2.0

- **Decision:** Switch from Arduino to Raspberry Pi Pico using UART.
  **Context:** Arduino was okay for testing but the logic levels and I2C were giving me headaches.
  **Outcome:** The Pico is way better. It's faster and I can code it in MicroPython.
  
- **Decision:** Separate the sensor logic into its own file (`pico_main.py`).
  **Context:** I need to keep the code that runs on the Pico separate from the main dashboard code. 
  **Outcome:** Created a dedicated script for the Pico. It reads the raw data and spits it out via Serial. 

- **Decision:** Daemonize the Dashboard Process.
  **Context:** The dashboard would close if I disconnected my laptop.
  **Outcome:** Set up the systemd service to run as a background daemon. Now it's bulletproof.


## V2.1: Telemetry Synchronization & Data Filtering

* **UART Buffer Overflow Fix (The "Delay" Issue):** During the initial integration of the Pico and the Raspberry Pi 4, the dashboard experienced a severe visual delay. The UI would lag several seconds behind the physical actions. We diagnosed this as a buffer overflow: the Pico was transmitting data at ~100Hz (`utime.sleep(0.01)`), flooding the Pi's serial port faster than the PySide6 event loop could parse it. The fix was twofold: we throttled the Pico's transmission rate to a stable 20Hz and implemented a buffer flush (`serial_port.reset_input_buffer()`) on the Pi 4 to ensure it only reads the freshest telemetry packet, instantly eliminating the lag.
* **Software Low-Pass Filter for Speed:** The raw hardware interrupts from the Hall effect sensor were too sensitive, causing the speed readout on the dashboard to jitter erratically. Instead of adding a physical RC filter (capacitors/resistors) to the sensor wiring, we solved this entirely via software on the Pico. By storing the most recent speed pulses in a rolling array and calculating the average before sending it over UART, the QML interface now displays perfectly smooth and stable numbers.


## V2.2: UART Buffer Optimization & Boot Traceability

* **"Latest-Packet-Only" UART Parsing:** To completely eliminate UI rendering delays, we overhauled how the Raspberry Pi handles incoming serial data. Instead of processing incoming packets sequentially (which queues up stale data if the Pi's event loop stutters), the `main.py` backend now reads the entire contents of the serial buffer at once (`serial_port.read(in_waiting)`). It then splits the payload and explicitly extracts only the final index `[-1]`. This guarantees the QML dashboard always renders the absolute real-time state of the motorcycle, instantly discarding any micro-backlog of older telemetry.
* **Embedded Boot Sequence Logging:** Added a numbered verbose logging sequence during the application's startup phase. Since this dashboard runs headlessly on a motorcycle, tracing the exact step of failure (e.g., PySide6 initialization, Serial connection, or QML parsing) via systemd logs is critical for on-the-fly debugging without needing to plug in external peripherals.