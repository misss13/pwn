import os
import sys
import tqdm
import socket
import hashlib
from sendfile import sendfile


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


def recv_file(file_name, socket):
    """Reciving file function with returning hash"""
    try:
        fhash = hashlib.sha256()
        file = open(file_name,'wb')
        bs = socket.recv(1024)
        while (bs):
            file.write(bs)
            fhash.update(bs)
            bs = socket.recv(1024)
        file.close()
        print("===file-received===")
        return(fhash.hexdigest())
    except:
        print("[ERROR] in recv_file function")
        return None


def client_hello(socket, address):
    """Define handling client connection"""

    r = reciving(socket) 
    print(r)

    if(str(r) == "yoo"):
        #proste potwierdzenie że klient i serwer działa
        sending(socket, "oii")
        socket.close()

    elif(str(r) == "ssid"):
        #sending(socket, "ssid0\tpass0\nssid1\tpass1\nssid2\tpass2\n\0") 🤮🤮🤮🤮
        socket.close()

    elif(str(r) == "hs"):
        #file receiving and integrity check
        try:
            sending(socket, "ok")
            thash = reciving(socket) 
            print(thash)
            sending(socket, "hash_ok")
            fhash = recv_file("rcv.pcap", socket)
            if fhash == thash:
                print("yay")
                status_last = True
            else:
                print("nay")
                status_last = False
        except:
            print("[ERROR] in Client_hello - hs")
            status_last = False
        socket.close()

    elif(str(r) == "status"):
        status_last = True
        if status_last:
            sending(socket, "ok")
        else:
            sending(socket, "no")
    
    else:
        print("coś nie tak")
        socket.close()