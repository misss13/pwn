import os
import sys
import socket


def start():
    """How to start"""
    if len(sys.argv) < 2:
        print("python server.py [loc/ser]")
        quit()
    if sys.argv[1] == "loc":
        print("Server works on loopback [TESTING]")
        host = '127.0.0.1'
        port = 12345 
    else:
        print("-- Server deployed --")
        host = '0.0.0.0'
        port = 12345
    return host, port


def reciving(socket):
    """Reciving and parsing data"""
    try:
        rec = socket.recv(2048)
        rec = (str(rec.decode("UTF-8"))).replace("\0", "\n").replace("\n", "")
    except:
        print("[ERROR] in reciving")
        rec = None
    return rec


def sending(socket, message):
    """Parse and send data"""
    try:
        socket.send(str(message).encode("UTF-8"))
        return True
    except:
        print("[ERROR] in sending")
        return False


def parsing(SSID, password):
    """Parsing txt to format"""
    return str(SSID) + ":" + str(password)

def check_ssid():
    """Checking if rainbow table for ssid is aviale SSID.txt"""

def download_rainbow():
    """Connecting and downloading rainbow tables"""
    #https://freerainbowtables.com/
    #https://www.renderlab.net/projects/WPA-tables/ <- wybraned
    #chyba skipne bo to duże rzeczy są trzeba pobrać wcześniej

def rainbow_tables_checking():
    """Use fast rainbow table"""


def check_dictionary():
    """Check if dictionary.txt exist"""


def compute_aircrack_dictionary():
    """Aircrack checking on the run based on dictionary"""


def compute_cat_bruteforce():
    """Hashcat hashcat rainbow table bruteforcing"""


def send_end(ssid, password, socket):
    """Sending end ending session"""
    if password != None:
        sending(socket, parsing(ssid, password))
        socket.close()
        return True


def client_hello(socket, address):
    """Define handling client connection"""

    r = reciving(socket) 
    print(r)
    if(str(r) == "yoo"):
    #proste potwierdzenie że klient i serwer działa
        sending(socket, "oii")
        print("send")
        ssid = reciving(socket)

        ##Main function
        #phaze 1. checking if password exist in downloaded rainbow table and using it
        if check_ssid(ssid) == True:
            download_rainbow()
            password = rainbow_tables_checking()
            if send_end(ssid, password, socket) == True:
                return True
        
        #phaze 2. realtime checking passwords from dictionary
        password = compute_aircrack_dictionary(ssid)
        if send_end(ssid, password, socket) == True:
            return True
        
        #phaze 3. bruteforce with hashcat
        password = compute_aircrack_dictionary(ssid)
        if send_end(ssid, password, socket) == True:
            return True
    else:
        #os.system("echo yooo")
        socket.close()