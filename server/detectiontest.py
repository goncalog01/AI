import cv2

import numpy as np


def draw_labels(boxes, confs, img): 
	# indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)
	for i in range(len(boxes)):
		#if i in indexes:
		x, y, w, h = boxes[i]
		color = [0, 0, 255]
		cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
	cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
	w = img.shape[1]*ratio
	h = img.shape[0]*ratio
	cv2.resizeWindow("Image", int(w), int(h))
	cv2.imshow("Image", img)
	return img

def find_cars(path):
	# read image
	img = cv2.imread(path)
	height = img.shape[0]
	width = img.shape[1]
	# start yolo
	yolo = cv2.dnn.readNet("detection/yolov3.weights", "detection/yolov3.cfg")
	layers = yolo.getLayerNames()
	unconnectedLayers = yolo.getUnconnectedOutLayers()
	outLayers = [layers[unconnectedLayers[0]-1], layers[unconnectedLayers[1]-1], layers[unconnectedLayers[2]-1]]
	# prepare the image to perform the analysis
	blob = cv2.dnn.blobFromImage(img, scalefactor=1/255, size=(320, 320), mean=(0, 0, 0), swapRB=True)
	# set the image to be analyzed
	yolo.setInput(blob)
	# analyze
	boxes = []
	confidences = []
	for output in yolo.forward(outLayers):
		for detect in output:
			ids = detect[5:]
			id = np.argmax(ids)
			if(id == 2 or id == 7):
				confidence = ids[id]
				if confidence > 0.3:
					center_x = int(detect[0] * width)
					center_y = int(detect[1] * height)
					w = int(detect[2] * width)
					h = int(detect[3] * height)
					x = int(center_x - w/2)
					y = int(center_y - h / 2)
					boxes.append([x, y, w, h])
					confidences.append(float(confidence))
	img = draw_labels(boxes, confidences, img)
	cv2.waitKey(0)
	x = input("save image?")
	if x=="y" :
		status = cv2.imwrite("parking/saved.jpg", img)
	exit()



		
ratio = 1
find_cars("detection/parking/maskedimg.jpg")



#  article{yolov3,
#  title={YOLOv3: An Incremental Improvement},
#  author={Redmon, Joseph and Farhadi, Ali},
#  journal = {arXiv},
#  year={2018}
#  }