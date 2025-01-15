# ai-proj
## Smart Street Parking

#### Raspberry Pi Zero 2W setup:

use the official raspberry pi imager to install the raspberry pi os (the recommended one, with desktop environment) on the sd card

then turn on the raspberry with the sd card and connect keyboard and mouse

follow the steps (choose country Portugal, time zone Lisbon, then username grupo7, password 1234, also connect to wifi)

skip the updates

after rebooting do `sudo apt-get update` and `sudo apt-get upgrade`

(to improve the raspberrys performance you can change the /boot/config.txt file uncommenting the arm_freq line and replacing 800 with 1000)

install motion: `sudo apt-get install motion`

change motion params: `sudo nano /etc/motion/motion.conf`

    Apply these settings:
    
    daemon off
    emulate_motion off
    log_file /home/grupo7/motion/log/motion.log
    target_dir /home/grupo7/motion 
    snapshot_interval 15 (can be written anywhere, for eg after post_capture)
    movie_output off
    uncomment camera1.conf and write /home/grupo7/motion/configs/camera1.conf
    (uncomment the others if you have more cameras)

create motion directory at grupo7 directory and subdirs motion/snapshots, motion/log, motion/configs

the following camera instructions are for a PS3 Eye camera, so may differ for other cameras.

inside configs create a file named camera1.conf and write the following:

`videodevice /dev/video0`

`snapshot_filename /snapshots/%v-%Y%m%d%H%M%S-camera1`

if there are more cameras do the same, changing to the correct videodevice and camera2, 3, 4 etc

reboot

open a terminal and run `sudo motion -n` and make sure it runs and that snapshots are saved on /home/grupo7/motion/snapshots

then at grupo7 directory place the files imageUploader.py and runUploader.sh which can be found at the raspberry folder in the submission code

make sure you change the IP from imageUploader.py with the IP from your server and the correct port.

do `sudo chmod +x runUploader.sh` to change script permissions

then do `sudo nano /etc/rc.local` and add before the exit 0 line: `sudo ./home/grupo7/runUploader.sh`

This will allow using the raspberry without screen, keyboard and mouse. Simply turn on the raspberry, wait 2 minutes +- (to make sure it boots and doesn't crash), have the server running, plug the camera and it will send pictures automatically. To stop, simply disconnect the camera and wait, the raspberry will shutdown automatically to prevent memory corruption.

#### Server setup:

Download the source code. Get the yolov3.weights file from this url: 

https://drive.google.com/file/d/1PTEDe5uzjofKoZKoH9DzhhrQHPvuW_DG/view?usp=share_link

and put it on the server directory.

Install the following libraries for python: psycopg2, opencv, flask, flask_cors. If you don't have pip you also need to install it.

|       Windows/Linux       |
| :-----------------------: |
| pip install opencv-python |
|   pip install psycopg2    |
|     pip install flask     |
| pip install -U flask-cors |

Launch the server.py file (found in /server directory) from the ai-proj directory with `python /server/server.py`. Then run socketServer.py, also from the ai-proj directory with `python /server/socketServer.py`. For testing you can also run the file detect.py separately to analyze the car detection. This file must also be launched from the directory ai-proj. If you want to do this please uncomment the final lines of the file so the function image_processing is called, and write the correct number for the camera picture. 

If you have issues with "file not found" please use the absolute path instead (e.g. C:/ etc etc or /home/ etc etc).

###### Some extra notes:

The project has at the moment 3 cameras set up, camera1 is the camera from the raspberry, camera2 and camera3 are pictures used for testing. If you want to test the project without the raspberry, please use cameras 2 or 3 which already have masks, but it won't be dynamic since the pictures won't be updated. To use the raspberry, you need to place the camera in a fixed position and build the masks for the detection, identifying each parking spot. We recommend using GIMP. The file mask_builder.xcf is a GIMP file which contains an example. The masks are black and white, with white identifying the area of the parking space, and they must have exactly the same height and width in pixels as the original picture. It is essential that the camera isn't moved after this since any change will affect the detection. The file spots.txt identifies the parking spaces for each camera and their coordinates (a parking spot for each line, so line 1 is parking spot 1).

So if you want to add more cameras/spots, you need to update this file and create the corresponding masks inside a masks folder (e.g. "camera4masks")

#### App Setup:

We recommend using VSCode and the LiveServer extension. Just install the extension and then you will have a button on the bottom right which says Go Live. Open the project folder on VSCode, click the Go Live button and you should now have a server running on the port shown. A window will open on the browser, click the folder app and the app will start. You can also open the app on your mobile phone if it is connected to the same network as the server, by visiting http://your_server_ip:port/app/index.html.

If asked for permission to use location, please allow it.

To test the app without the raspberry and detection algorithm, run the server.py with `python /server/server.py test`. To change the parameters, use the test_slots variable at the beginning of the file.

The parking spaces on the map are placed around the alameda campus.







