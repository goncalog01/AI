import cv2
import glob
import os
import numpy as np
from server import update_slots


def find_cars(img, yolo, outLayers, parkingSpot):
	# prepare the image to perform the analysis
	blob = cv2.dnn.blobFromImage(img, scalefactor=1/255, size=(320, 320), mean=(0, 0, 0), swapRB=True)
	# set the image to be analyzed
	yolo.setInput(blob)
	# analyze
	for result in yolo.forward(outLayers):
		for detect in result:
			ids = detect[5:]
			id = np.argmax(ids)
			if(id == 2 or id == 7): # 2 --> car || 7 --> truck
				if ids[id] > 0.3:
					# print(f"CAR DETECTED AT PARKING SPOT Nº {parkingSpot}")
					return 1
	return 0

def get_file_names(camera):
    os.chdir(f"server/{camera}masks")
    spots = []
    for file in glob.glob("mask*"):
        spots.append([file, 0])
    return spots

def split_image(camera, yolo, outLayers):
	path = f"server/pictures/{camera}.jpg"
	# read image to analyze
	img = cv2.imread(path)
	# get the masks file names
	spots = get_file_names(camera)
	#i = 0  # this is just to allow image saving for testing
	for spot in spots:
		mask = spot[0]
		# get parkingSpot number
		spot[0] = int((mask[4:])[:-4])
		maskImg = cv2.imread(mask, 0)
		# apply mask to image
		maskedImg = cv2.bitwise_and(img, img, mask=maskImg)
		# crop image to improve car detection
		roi = np.argwhere(maskImg)
		a, b = roi.max(axis=0)
		x, y = roi.min(axis=0)
		croppedImg = maskedImg[x:a, y:b]
        # uncomment to view the mask and the generated masked image
		#cv2.imshow('Mask', maskImg)
		#cv2.imshow('Result', croppedImg)
		#cv2.waitKey(0)
		# uncomment and change path if necessary to save the maskedimage for further testing
		#if i == 5:
			# status = cv2.imwrite("*yourfullpathhere*/maskedimg.jpg", croppedImg)
		#i = i+1
		spot[1] = find_cars(croppedImg, yolo, outLayers, spot[0])
	return spots

			

def image_processing(camera):
	# start yolo
	yolo = cv2.dnn.readNet("server/yolov3.weights", "server/yolov3.cfg")
	layers = yolo.getLayerNames()
	unconnectedLayers = yolo.getUnconnectedOutLayers()
	outLayers = [layers[unconnectedLayers[0]-1], layers[unconnectedLayers[1]-1], layers[unconnectedLayers[2]-1]]
	result = split_image(camera, yolo, outLayers)
	os.chdir("../..")
	print(result)
	return result

# Uncomment to test detection
#result = image_processing("camera2")  # this line will print the detection result (0 for no car, 1 for car detected)
#update_slots(result)  # to test server-app with detection. if you uncomment this line you have to have the server and app running to see changes

#  article{yolov3,
#  title={YOLOv3: An Incremental Improvement},
#  author={Redmon, Joseph and Farhadi, Ali},
#  journal = {arXiv},
#  year={2018}
#  }