# ai-proj
## Smart Street Parking

### Raspberry Pi Zero 2W setup

- Use the official Raspberry Pi imager to install the Raspberry Pi OS (the recommended one, with desktop environment) on the SD card

- Turn on the Raspberry Pi with the SD card and connect the keyboard and the mouse

- Follow the steps (choose country Portugal, time zone Lisbon, username grupo7, password 1234, and connect to Wi-Fi)

- Skip the updates

- After rebooting run the commands `sudo apt-get update` and `sudo apt-get upgrade`

- To improve the Raspberry Pi's performance you can change the `/boot/config.txt` file by uncommenting the arm_freq line and replacing 800 with 1000

- Install motion: `sudo apt-get install motion`

- Change the `/etc/motion/motion.conf` file to the following settings:
```
daemon off
emulate_motion off
log_file /home/grupo7/motion/log/motion.log
target_dir /home/grupo7/motion 
snapshot_interval 15 (can be written anywhere, for eg after post_capture)
movie_output off
uncomment camera1.conf and write /home/grupo7/motion/configs/camera1.conf
(uncomment the others if you have more cameras)
```
- Create a new directory named `motion` at the `grupo7` directory and subdirs `motion/snapshots`, `motion/log`, `motion/configs`

The following camera instructions are for a PlayStation 3 Eye camera, so it may differ for other cameras:

- Inside `motion/configs` create a file named `camera1.conf` with the following:
```
videodevice /dev/video0
snapshot_filename /snapshots/%v-%Y%m%d%H%M%S-camera1
```
- If there are more cameras do the same for each one, changing to the correct videodevice and filename to camera2, 3, 4, etc.

- Reboot

- Open a terminal, run `sudo motion -n`, and make sure it runs and that snapshots are saved on the `/home/grupo7/motion/snapshots` directory

- Place the `imageUploader.py` and `runUploader.sh` files (which can be found on the `raspberry` folder in the submission code) on the `grupo7` directory

- Make sure you change the IP from `imageUploader.py` to the IP from your server and the correct port

- Run `sudo chmod +x runUploader.sh` to change the script permissions

- Run `sudo nano /etc/rc.local` and before the `exit 0` add the following line: `sudo ./home/grupo7/runUploader.sh`

This will allow using the Raspberry Pi without screen, keyboard and mouse. Simply turn on the Raspberry Pi, wait ~2 minutes (to make sure it boots and doesn't crash), have the server running, plug the camera and it will send pictures automatically. To stop, simply disconnect the camera and wait. The Raspberry Pi will automatically shutdown to prevent memory corruption.

### Server setup

- Download the source code

- Get the `yolov3.weights` file from this url and put it on the `server` directory: 

https://drive.google.com/file/d/1PTEDe5uzjofKoZKoH9DzhhrQHPvuW_DG/view?usp=share_link

- Install the following libraries for Python: OpenCV, psycopg2, Flask, Flask-Cors. If you don't have pip you also need to install it

|       Windows/Linux       |
| :-----------------------: |
| pip install opencv-python |
|   pip install psycopg2    |
|     pip install flask     |
| pip install -U flask-cors |

- Run the `server.py` file (found in the `server` directory) from the `ai-proj` directory with the command `python /server/server.py`

- Run the `socketServer.py` file, also from the `ai-proj` directory, with the command `python /server/socketServer.py`

- For testing you can also run the `detect.py` file separately to analyze the car detection. This file must also be launched from the `ai-proj` directory. If you want to do this please uncomment the final lines of the file so that the `image_processing` function is called, and write the correct number for the camera picture

If you have issues with "file not found" please use the absolute path instead (e.g. `C:/...` or `/home/...`).

###### Some extra notes:

At the moment, the project has 3 cameras set up: camera1 is the camera from the Raspberry Pi, while camera2 and camera3 are pictures used for testing. If you want to test the project without the Raspberry Pi, please use cameras 2 or 3 which already have masks, but it won't be dynamic since the pictures won't be updated. To use the Raspberry Pi, you need to place the camera in a fixed position and build the masks for the detection, identifying each parking spot. We recommend using GIMP. The `mask_builder.xcf` file is a GIMP file which contains an example. The masks are black and white, with white identifying the area of the parking spot, and they must have exactly the same height and width in pixels as the original picture. It is essential that the camera isn't moved after this, since any change will affect the detection. The `spots.txt` file identifies the parking spots for each camera and their coordinates (a line for each parking spot: line 1 is parking spot 1, line 2 is parking spot 2, and so on). So if you want to add more cameras or parking spots, you need to update this file and create the corresponding masks inside a masks folder (e.g. "camera4masks")

### App Setup

We recommend using VSCode with the LiveServer extension. Just install the extension and then you will have a button on the bottom right which says "Go Live". Open the project folder on VSCode, click the "Go Live" button and you should now have a server running on the port shown. A window will open on the browser, click the folder app and the app will start. You can also open the app on your mobile phone if it is connected to the same network as the server, by visiting http://your_server_ip:port/app/index.html.

If asked for permission to use location, please allow it.

To test the app without the Raspberry Pi and detection algorithm, run the `server.py` file with the command `python /server/server.py test`. To change the parameters, use the `test_slots` variable at the beginning of the file.

The parking spots on the map are placed around the IST Alameda campus.