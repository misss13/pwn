import os
import sys
import socket
import hashlib

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
        rec = (str(rec.decode("UTF-8"))).replace("\0", "\n").rstrip()
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
    pass

def download_rainbow():
    """Connecting and downloading rainbow tables"""
    pass

def rainbow_tables_checking():
    """Use fast rainbow table"""
    pass

def check_dictionary():
    """Check if dictionary.txt exist"""
    pass

def compute_aircrack_dictionary():
    """Aircrack checking on the run based on dictionary"""
    pass

def compute_cat_bruteforce():
    """Hashcat hashcat rainbow table bruteforcing"""
    pass


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
        socket.close()

    elif(str(r) == "ssid"):
        sending(socket, "ssid0\tpass0\nssid1\tpass1\nssid2\tpass2\n\0")
        socket.close()

    elif(str(r) == "hs"):
        sending(socket, "ok")

        thash = reciving(socket) 
        print(thash)

        sending(socket, "hash_ok")

        fhash = hashlib.sha256()

        f = open('rcv.pcap','wb') #open in binary
        bs = 1
        while(bs):
            bs = socket.recv(1024)
            while (bs):
                f.write(bs)
                fhash.update(bs)
                bs = socket.recv(1024)
            f.close()
        print("RCV END")

        if str(fhash.hexdigest()) == thash:
            print("yay")
            status_last = True
        else:
            print("nay")
            status_last = False

    elif(str(r) == "status"):
        status_last = True
        if status_last:
            sending(socket, "ok")
        else:
            sending(socket, "no")

    else:
        print("coś nie tak")
        socket.close()