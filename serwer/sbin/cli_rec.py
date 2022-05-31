#client na wysylanie pliku test
import os
import socket
import time
from sendfile import sendfile

file = open("wifi.pcap", "rb")
blocksize = os.path.getsize("wifi.pcap")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 12345))
offset = 0
sock.send(str("hs").encode("UTF-8"))

rec = sock.recv(2048)
rec = (str(rec.decode("UTF-8"))).replace("\0", "\n").replace("\n", "")
print(rec)

sock.send(str("b188eb2d279c5facabdb04822b4d32909c5af7d462d9043d5066e5c4134cc7d5").encode("UTF-8"))

rec = sock.recv(2048)
rec = (str(rec.decode("UTF-8"))).replace("\0", "\n").replace("\n", "")

while True:
    sent = sendfile(sock.fileno(), file.fileno(), offset, 1024)
    if sent == 0:
        break  # EOF
    print("przeslano")
    offset += sent