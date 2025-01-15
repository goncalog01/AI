import socket, os, glob

sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.connect(("192.168.1.79", 6000))

os.chdir("/home/grupo7/motion/snapshots")
snaps = []
for snap in glob.glob("*camera*"):
    image = open(snap, "rb")
    size = os.path.getsize(snap)
    sender_socket.sendall(("INFO"+snap[-5]+str(size)).encode())
    got_info = str(sender_socket.recv(1024))
    if got_info[2:5] == "yes":
        image_bytes = image.read(size)
        sender_socket.sendall(image_bytes)
        image_received = str(sender_socket.recv(1024))
        if image_received[2:10] != "received":
            break
    image.close()
    os.remove(image.name)

sender_socket.sendall("DONE".encode())
sender_socket.close()