This document is about everything related with installing and running the system through the Raspberry pi 4 Model B

V 1.0:

Changes:

Changed the environment from ubuntu core to ubuntu server, this was to make easier modifying the code on the go without having to make big changes in the system, just having to change and update the code in the Raspberry.
Also made this beacuse i forgot the password i had before :( 

V 1.1:

Once having the hardware set up, (See about it in the hardware.md document) we connect everything, and start the set up process, we will be able to connect to the raspberry, send the updated codes and run them to see the changes in the external screen.

Connection process:  
    1.- Having all the hardware connected; We go to the wifi connections using "win+r" and "ncpa.cpl", there we need to right click on the wifi network we're connected, go to properties, then sahring and enable the option to allow others to connect through this pc connected network.  
    2.- On a new VSCode terminal, write "ssh ubuntu@raspberrypi.local"  
    3.- Once connected, we can run the main.py to see the dashboard 
    
![First dashboard run](images/dash-preliminar.png)

V 1.2:

To send new modified code to the raspberry to run them on the external screen:  

-Connect to the raspberry as previously shown  
-On a new powershell terminal, use "scp -r "C:\Project\route" ubuntu@raspberrypi.local:~/" to send the whole folder or just type the name of the file you want to send  
-Go to the ssh terminal and restart the dashboard to see the changes made using: sudo systemctl restart dashboard.service  

To test the UI faster without sending everything to the Raspberry Pi every single time, I set up a way to run it locally on the PC. 

Local testing process:
1.- Open a new terminal in VSCode (make sure it's running on your local machine, not the SSH one).
2.- Install PySide6 if you haven't already: "pip install PySide6".
3.- Run the script directly with "python main.py".

This opens the dashboard in a window on the computer using fake data, so we can edit the QML and see changes instantly without the hardware.


