import socket
import select
import errno
import sys
import hashlib

# rozmiar "headera" wiadomości
HEADER_LENGTH = 10

# IP i PORT serwera
IP = "10.0.0.1"
PORT = 12345

# pobieramy od użytkownika username
# my_username = input("Username: ")

# Stworzenie socketa
# socket.AF_INET - rodzina adresów, IPv4, inne przykłady: AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, połączeniowy; socket.SOCK_DGRAM - UDP, bezpołączeniowy, datagramy; socket.SOCK_RAW - surowe pakiety IP
cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Łączymy się z podanym IP i PORTem
cli_socket.connect((IP, PORT))

# Ustawiamy połączenie w tryb nieblokujący, więc call .recv() nie będzie czekał na powodzenie,
# jak coś się przedłuży to wyrzuci wyjątek, który rozwiążemy
cli_socket.setblocking(False)

# Przygotowujemy username i jego header
# Musimy zakodować username na bajty, potem policzyć te bajty i przygotować header wiadomości (o stałym rozmiarze), który też zakodujemy
# username = my_username.encode('utf-8')
# username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
# nadajemy header i username w postaci zakodowanej wiadomości
# cli_socket.send(username_header + username)

cli_socket.send("hs".encode())

sha256 = hashlib.sha256()

read_sockets, write_socket, error_socket = select.select([cli_socket], [], [])

for socks in read_sockets:
    test = socks.recv(1024).decode().strip()
    print(repr(test))

    with open("test.pdf", "rb") as f:
        for byte_block in iter(lambda: f.read(1024), b""):
            sha256.update(byte_block)
            
    cli_socket.send(str(sha256.hexdigest()).encode())

    read_sockets, write_socket, error_socket = select.select([cli_socket], [], [])

    for socks in read_sockets:
        test = socks.recv(1024).decode().strip()
        print(repr(test))

        with open("test.pdf", "rb") as f:
            bs = f.read(1024)
            while (bs):
                socks.send(bs)
                bs = f.read(1024)
            socks.close()

        socks.close()


# cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# cli_socket.connect((IP, PORT))

# cli_socket.send("status".encode())

# read_sockets, write_socket, error_socket = select.select([cli_socket], [], [])

# for socks in read_sockets:
#     test = socks.recv(1024).decode().strip()
#     print(repr(test))

#     socks.close()