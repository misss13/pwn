# pwn
Projekt na Bezpieczeństwo Bezprzewodowych Sieci Komputerowych. Celem naszego projektu było łamanie haseł do sieci na podstawie handshake’a ze znanym SSID. Do jego realizacji wykorzystaliśmy Pwnagotchi, do którego stworzyliśmy plugin o nazwie uploader.py.
Jego zadaniem jest przesyłanie przechwyconych przez Pwnagotchi handshake’ów i wysyłanie ich wraz
z ssid oraz bssid serwerowi. Serwer natomiast ma za zadanie łamać hasła do wifi, a następnie odsyłać
je z powrotem. W celu ustalenia hasła wykorzystuje słownik haseł, tablice tęczowe, a także
przeprowadza atak siłowy

- ``serwer`` 
    - api  
        - umożliwia sprawdzanie stanu serwera
        - przesłanie pliku handshaka 
        - sprawdzenie czy przesyłanie się powiodło
        - wysłanie pliku z bierzącą zawartością złamanych par ``ssid\thasło``
    - opcje łamania hashy
        - rainbowtables
        - aircrack-ng
        - hashcat  
- ``plugin`` - zawiera kod pluginu do pwnagochi
