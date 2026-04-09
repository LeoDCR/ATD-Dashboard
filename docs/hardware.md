This document is about everything regarding the hardware in the project.


V 1.1:
We already have some hardware working along qith the prevoius code, this consists of: A potenciometer, a temperature sensor, a hall sensor and an external motor.

Also, and more important, we have as the brain of the project, the only connections we have are the power usb-c cable to the raspberry and an Ethernet cable to access ubuntu from our VS Code terminal without needing an external monitor, mouse and keyboard connected to the raspberry.

Right now we do need an external screen to see the changes made in the proyect, but we have the objective to being capable of making changes and seeing them without anything connected, like a test running in VS Code, but that will be seen later.

![First dashboard run](images/design3.png)


V 1.4 Note:
While the UI is now receiving data from the Python backend, the backend is still using placeholder data generation. The next major step is figuring out the best microcontroller communication protocol to get real sensor data from the bike into the Raspberry Pi.

## V 2.0: The Hardware Overhaul

**New Brain: Raspberry Pi Pico**
We officially moved away from the initial Arduino/I2C testing setup and introduced the Raspberry Pi Pico as the dedicated sensor-reading microcontroller. 

**Why the Pico?**
- It runs MicroPython, keeping the entire project's codebase in the Python ecosystem.
- Its 3.3V logic level matches the Raspberry Pi 4 perfectly, avoiding the need for logic level shifters.
- It's incredibly fast and has plenty of GPIOs for all the motorcycle's analog and digital signals.

**Communication: UART**
The communication protocol between the Pico and the Pi 4 was changed to UART (Serial). 
- Pico TX -> Pi 4 RX
- Pico RX -> Pi 4 TX
This proved to be much more stable and easier to debug for continuous data streaming compared to our early I2C attempts.

![First dashboard run](images/setup1.jpeg)