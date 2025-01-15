import socket, signal, sys
import threading
from detect import image_processing
from server import update_slots

def handle_signal(sig, frame):
    print('Goodbye!')
    receiver_socket.close()
    sys.exit(0)
    
def handle_client(fd):
	data = None
	camera = "error"
	bytes_received = b''
	while True:
		data = fd.recv(2048)
		data_string = str(data)
		if data_string[2:6] == "INFO":
			bytes_received = b''
			camera = data_string[6]
			size = data_string[7:-1]
			print(size)
			print(camera)
			file_size = int(size)
			fd.send("yes".encode())
			image = open("server/pictures/camera" + camera + ".jpg", "wb")
		elif data_string[2:6] == "DONE":
			break
		elif data:
			if len(bytes_received) < file_size:
				bytes_received += data
			if len(bytes_received) == file_size:
				print("RECEIVED")
				fd.send("received".encode())
				image.write(bytes_received)
				image.close()
				result = image_processing("camera"+camera)
				update_slots(result)

	fd.close()

signal.signal(signal.SIGINT, handle_signal)

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
receiver_socket.bind(("0.0.0.0", 6000))
receiver_socket.listen(10)

while True:
	print("listening...")

	fd, address = receiver_socket.accept()

	print(f"Connected to {address}")

	threading.Thread(target=handle_client,args=(fd,), daemon=True).start() 


