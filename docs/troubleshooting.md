This document is about all the issues that came up and how they were solved

## V 1.2:

- Overlapping text on speed gauge: There is a bug where a smaller number (like '52') shows up behind the actual speed number on the main gauge. It's probably an extra Text element I forgot to remove or a weird anchoring issue in the QML. Needs to be fixed in the next versions.


## V 1.3:

- RESOLVED: Overlapping text on speed gauge from V1.2 is fixed. The layout is clean now.
- Keep an eye on: Using `Canvas` to draw the gradients and arcs frame-by-frame might be a bit heavy on the Raspberry Pi's GPU. It runs smooth on the PC, but need to test performance on the actual Pi 4 screen later.


## V 2.0

- **Issue:** Permission errors when trying to read the Serial port on the RPi 4.
  **Solution:** Had to add my user to the `dialout` group: `sudo usermod -a -G dialout $USER`. 
  
- **Issue:** Thonny vs VSCode.
  **Note:** Sometimes Thonny keeps the Serial port busy and doesn't let the main dashboard start. I have to make sure to stop the script in Thonny before letting the systemd service take over.

- **Issue:** Baud rate mismatch.
  **Note:** If the data looks like gibberish, check that both the Pico and the RPi 4 are set to 115200.