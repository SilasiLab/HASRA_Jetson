# **Overview**:

This system allows the user to host up to 5 mice in their home environment and automatically administer the single pellet reaching test to those animals. The system can run unsupervised and continuously for weeks at a time, allowing all 5 mice to perform an unlimited number of single pellet trials at their leisure. 

The design allows a single mouse at a time to enter the reaching tube. Upon entry, the animal’s RFID tag will be read, and if authenticated, a session will start for that animal. A session is defined as everything that happens from the time an animal enters the reaching tube to when they leave the tube. At the start of a session, the animal’s profile will be read and the task difficulty as well as the left and right preference will be automatically adjusted by moving the pellet presentation arm to the appropriate distance both away from the reaching tube and from right to left. Pellets will continue to be presented periodically until the mouse leaves the tube, at which point the session will end. Video and other data is recorded for the duration of each session. At session end, all the data for the session is saved in an organized way. We also have an auxiliary function for counting the successful rate of displaying a pellet using MobileNetV2 based on tensorflow and keras.

For further analyse, you can check the repository posted here:
https://github.com/SilasiLab/HomecageSinglePellet_Manual

# **Software Installation Jetson/ARM:**

1. Put sd card into host machine
2. Make sure the contents of the sd can be deleted… ie back them up on the host machine if you need them or aren’t sure
3. Use disks utility to format sd card
4. https://developer.nvidia.com/jetson-nano-sd-card-image
Download nano sd card image from the nvidia downloads page… link above\
5. $ /usr/bin/unzip -p ~/Downloads/jetson_nano_devkit_sd_card.zip | sudo /bin/dd of=/dev/sd<x> bs=1M status=progress
6. Use your file manager to eject the sd card once the above process is complete
7. Put a jumper on your nano to allow for power from the barrel jack
8. Put in the sd and give your nano power
9. Allocate all the remaining blocks in your sd to your home fs
10. Go through the setup normally… make a user and pw, etc
11. $ sudo apt-get update && apt-get upgrade
12. $ sudo apt install git-all
13. $ git clone https://github.com/silasilab/hasra_jetson.git
14. $ git clone https://github.com/JetsonHacksNano/CSI-Camera.git
15. $ git clone https://github.com/jetsonhacks/jetsonUtilities.git
16. $ sudo -H pip3 install -U jetson-stats
17. Reboot
18. Dont pip install requirements.txt…
	 - $ pip3 install pyserial
	 - $ pip3 install psutil
19.Remove all function calls in main.py that’re dependent on tk
20. $ sudo apt install libcanberra-gtk-module libcanberra-gtk3-module
21. Setup is_running
	- $ cd ~
	- $ vim is_running.sh
	Write: #!/bin/bash
		pgrep -af main.py
22. Put below line in bashrc
	- $ alias is_running=’/home/homecage24/is_running.sh’
23. Setup rclone by running and going through the steps:
	- $ rclone config
24. Setup cronjobs to run rclone commands to send files to cloud storage
	- $ crontab -e
25. You should also download and install the arduino IDE for if you need to change code on the arduino. Keep in mind that some arduino nanos may use the old bootloader and that you will have to switch this in the IDE if you run into problems when trying to upload code to your arduino.

# **Assembly:**

The detailed assembly manual can be found here:
https://github.com/SilasiLab/HomeCageSinglePellet_server/blob/master/Homecage%20assembly%20manual.pdf



# **Usage**:
### **Running on Jetson with system install**
1. if it's your first time running HASRA on this device you need to run $ cd /home/$USER/HASRA_Jetson && mkdir AnimalProfiles
2. cd into src/client with $ cd /home/$USER/HASRA_Jetson/src/client
3. run the genprofiles script with $ python3 genProfiles.py
4. to start the task run $ cd /home/$USER/HASRA_Jetson/src/client && python3 main.py

# **Troubleshooting**:


6. Optional: If you have a google file stream mounted on this computer, you can choose to upload all the viedos and log files to google drive. You need firstly find out the local path to this google drive folder, in this case it is: `G:\Shared drives\SilasiLabGdrive`.
Since there could be mutiple cage running on the same computer and they can also be stored in the same google cloud folder. You can add a suffix to the project foler name by changing the root folder name from `HomeCageSinglePellet_server` to `HomeCageSinglePellet_server_id`(replace the id by your id) 
In the same folder, open another terminal and activate the virtual environment again, then run `python googleDriveManager.py \path\to\your\cloud\drive\folder`.
The videos and the log files will be stored in `your cloud drive\homecage_id_sync`.

7. You need to put in the RFID tag numbers manually into the profiles. Take mouse 1 as an instance, you need to replace the first line in `HomeCageSinglePellet_server\AnimalProfiles\MOUSE1\MOUSE1_save.txt`. If you do not know your tag number, don't worry. You can scan it on the RFID reader, it will be printed in the Terminal as `[tag number] not recognized`.

8. To test that everything is running correctly, block the IR beam breaker with something
	and scan one of the system’s test tags. If a session starts properly, it’s working. You will also be able to find out hom many pellets have been succefully displayed out of current displays we have as it is shown in the terminal too. 

9. To shut the system down cleanly; 

	- Ensure no sessions are currently running. 
	- Press the quit button on the GUI.
	- Ctrl+c out of the program running in the terminal.


# **Troubleshooting**:

* Is everything plugged in?
* Make sure you are in the correct virtual environment.
* Make sure the HomeCageSinglePellet/config/config.txt file contains the correct configuration. (If the file gets deleted it will be replaced by a default version at system start)
* Make sure there are 1 to 5 profiles in the HomeCageSinglePellet/AnimalProfiles/ directory. Ensure these profiles contain all the appropriate files and that the save.txt file for each animal contains the correct information. 
