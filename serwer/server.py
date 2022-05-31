import time
import socket
from sbin import *

#imagine more than 3 connections with running hashcat
CONNECTIONS=3

if __name__=="__main__":
    host, port = start()
    print(host, port)

    #server connection TCP
    ServerSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) 
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print("[ERROR]: " + str(e))
    ServerSocket.listen(CONNECTIONS)

    #Thread handling cracking processess
    main_thread = Main_handler(cracking_main_func)
    main_thread.start()

    #client connect
    while True:
        socket, address = ServerSocket.accept()
        hi_thread = Hi_handler(client_hello, socket, address)
        hi_thread.start()

        #server cpu sanity
        time.sleep(0.05)
    ServerSocket.close()