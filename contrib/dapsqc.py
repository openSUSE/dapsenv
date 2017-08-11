import socket
import sys

HOST, PORT = "localhost", 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(bytes(sys.argv[1], "utf-8"))

    received = str(sock.recv(1024), "utf-8")

print("Sent:     {}".format(sys.argv[1]))
print("Received: {}".format(received))
