import os
import sys
import time
import tqdm
import socket
import hashlib
from os.path import exists
from sendfile import sendfile


TODO_PCAP = [] #queue of files to handle
STATUS_LAST = False #is recent file downloaded right
KNOWN = { "kot":123, "pies":"123asd", "to":None} #ssid:passwd
PCAP_DICT = {} # { hash_handshake:[ssid, bssid] }


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


def password_to_ugly(socket):
    """Create string and send to client"""
    global KNOWN
    try:
        table_string = ""
        for ssid in list(KNOWN):
            if KNOWN[ssid] != None:
                table_string += str(str(ssid) + "\t" + str(KNOWN[ssid]) + "\n")
                KNOWN.pop(ssid)
        os.system("touch ssid-passwords.txt")
        file = open("ssid-passwords.txt",'a')
        file.write(table_string)
        file.close()

        #sending file hash
        #fhash = hashlib.sha256()
        #fhash.update(table_string.encode("UTF-8"))
        #socket.sending(socket, fhash.hexdigest())

        file = open("ssid-passwords.txt",'r')
        
        offset = 0
        while True:
            sent = sendfile(socket.fileno(), file.fileno(), offset, 1024)
            if sent == 0:
                break
            offset += sent
        file.close()
        print("==sent==")
        return True
    except:
        print("[ERROR] in password_to_ugly")
        return False    


def check_ssid(ssid):
    """Checking if rainbow table for ssid is aviable in SSID.txt"""
    try:
        with open('./serwer/manage/SSID.txt', 'r') as file:
            if (str(ssid) in file.read()):
                return True
            return False

    except:
        print("[ERROR] in check_ssid")
        return False


def check_rainbow():
    """Check if rainbow tarball exist"""
    #jest 2022 i wszyscy pluja na tablice tenczowe - fajne byly ale w 2011
    #https://freerainbowtables.com/
    #https://www.renderlab.net/projects/WPA-tables/ <- wybraned tarball7
    #UWAGA!!!! Prosze pobrac tara 7GB i rozpakować wszystkie .hash sciezka w 7gb_set/*.hash
    return exists("./serwer/manage/7gb_set/")

def rainbow_tables_checking(bssid, active_handshake):
    """Use fast rainbow table coWPAtty cuz its not fast as wind - not working most time -.-"""
    try:
        os.system("echo '' > ./serwer/manage/cowpatty_out")
        os.system("echo '' > ./serwer/manage/active_password_cow")
        os.system("cowpatty -f ./serwer/manage/7gb_set/" + str(bssid) + ".hash -s " + str(bssid) + " -r ./serwer/sbin/pcap/" + str(active_handshake) + ".pcap > ./serwer/manage/cowpatty_out")
        os.system("cat ./serwer/manage/cowpatty_out | grep \'The PSK is\' > ./serwer/manage/active_password_cow")
        with open('./serwer/manage/active_password', 'r') as file:
            passw = file.read().rstrip()
        if passw == "":
            return None
        else:
            p = r'"([A-Za-z0-9_\./\\-]*)"'
            m = re.search(p, passw)
            passw = m.group().replace("\"", "")
            return passw
    except:
        print("[ERROR] in check_rainbow")
        return None


def check_dictionary():
    """Check if dictionary.txt exist"""
    return exists("./serwer/manage/dictionary.txt")


def compute_aircrack_dictionary(bssid, active_handshake):
    """Aircrack checking on the run, based on dictionary"""
    try:
        os.system("echo '' > ./serwer/manage/active_password")
        os.system("aircrack-ng -w ./serwer/manage/dictionary.txt -b " + str(bssid) + " ./serwer/sbin/pcap/" + str(active_handshake) + ".pcap -l ./serwer/manage/active_password")
        with open('./serwer/manage/active_password', 'r') as file:
            passw = file.read().rstrip()
        if passw == "":
            return None
        else:
            return passw
    except:
        print("[ERROR] in compute_aircrack_dictionary")
        return None


def compute_cat_bruteforce(active_handshake):
    """Hashcat hashcat rainbow table bruteforcing"""
    try:
        os.system("echo '' > ./manage/active_password_h")
        os.system("echo '' > ./manage/active_password_h1")
        os.system("hcxpcapngtool -o ./serwer/manage/actual.hc22000 -E ./serwer/manage/wordlist ./serwer/sbin/pcap || echo '[ERROR] NO 4th part of EAPOL message'" + str(active_handshake) + ".pcap")
        os.system("hashcat -m 22000 ./serwer/manage/actual.hc22000 -a 3 '?d?d?d?d?d?d?d?d' -o ./serwer/manage/active_password_h")
        os.system("cat ./serwer/manage/active_password_h | cut -d: -f5 | head -n 1 > ./serwer/manage/active_password_h1")
        with open('./serwer/manage/active_password', 'r') as file:
            passw = file.read().rstrip()
        if passw == "":
            return None
        else:
            return passw
    except:
        print("[ERROR] in compute_cat_bruteforce")
        return None


def send_end(ssid, password, socket):
    """Sending end ending session"""
    if password != None:
        sending(socket, parsing(ssid, password))
        socket.close()
        return True

def get_bssid_ssid_hash(txt):
    """Parse data and give strings"""
    ssid, bssid, thash = txt.split("\t")
    return ssid, bssid, thash

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


def file_name_create(nr, folder, name):
    """Create string for storing .pcap files"""
    return str(str(folder) + "/" + str(name) + str(nr) + ".pcap")


def client_hello(socket, address):
    """Define handling client connection"""
    global TODO_PCAP
    global STATUS_LAST
    global PCAP_DICT

    r = reciving(socket) 
    print(">> " + r)

    if(str(r) == "yoo"):
        #check health
        sending(socket, "oii")

    elif(str(r) == "ssid"):
        #send client .txt of all known passwords 
        #nie podoba mi się bo wysyłanie pliku to duża wartosc lepiej pojedynczo wysyłać hasła?
        password_to_ugly(socket)

    elif(str(r) == "hs"):
        #file receiving and integrity check
        try:
            sending(socket, "ok")
            ssidbssidthash = reciving(socket)
            ssid, bssid, thash = get_bssid_ssid_hash(ssidbssidthash)
            print(thash)
            sending(socket, "hash_ok")
            file_path = file_name_create(len(TODO_PCAP), "serwer/sbin/pcap", "rcv")
            fhash = recv_file(file_path, socket)
            file_hash = file_name_create("", "serwer/sbin/pcap", fhash)
            if fhash == thash:
                print("yay")
                STATUS_LAST = True
                TODO_PCAP.append(fhash)
                PCAP_DICT[fhash] = [0,0]
                PCAP_DICT[fhash][0] = ssid
                PCAP_DICT[fhash][1] = bssid
                os.system("mv "+ file_path + " " + file_hash)
            else:
                print("nay")
                STATUS_LAST = False
        except:
            print("[ERROR] in Client_hello - hs")
            STATUS_LAST = False
        print(TODO_PCAP)
        
    elif(str(r) == "status"):
        #status check
        try:
            if STATUS_LAST:
                sending(socket, "ok")
            else:
                sending(socket, "no")
        except:
            print("[ERROR] in status")
        
    else:
        print("Request undefined")
    socket.close()


#============ c r a c k i n g _ s e c t i o n ============#

def phaze_123(ssid, active_handshake,bssid):
    """3 phases for password receiving"""
    #phaze 1. checking if password exist in downloaded rainbow table and using it
    if check_ssid(ssid) == True and check_rainbow() == True:
        download_rainbow()
        password = rainbow_tables_checking()
        return password
    else:
        print("Rainbow tables not aviable")

    #phaze 2. realtime checking passwords from dictionary
    if check_dictionary() == True:
        password = compute_aircrack_dictionary(bssid, active_handshake)
        if password != None:
            print("Password found in dictionary")
            return password
    
    #phaze 3. bruteforce with hashcat 
    password = compute_cat_bruteforce()
    print("Password bruteforced")
    return password


def cracking_main_func():
    """Main function handling cracking"""
    global TODO_PCAP
    global PCAP_DICT
    global KNOWN

    while True:
        if len(TODO_PCAP) == 0:
            time.sleep(1)
            print(".")
        else:
            active_handshake = TODO_PCAP[0]
            ssid = PCAP_DICT[active_handshake][0]
            bssid = PCAP_DICT[active_handshake][1]
            
            ##Main function
            password = phaze_123(ssid, active_handshake, bssid)
            KNOWN[ssid] = password
            #removing item from queue
            PCAP_DICT.pop(active_handshake)
            TODO_PCAP.pop(0)
