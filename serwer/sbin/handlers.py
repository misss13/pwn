from threading import Thread

class Hi_handler(Thread):
    def __init__(self, function, socket, address):
        Thread.__init__(self, daemon = True)
        self.function= function
        self.socket = socket
        self.address = address

    def run(self):
        self.function(self.socket, self.address)

class Main_handler(Thread):
    def __init__(self, function):
        Thread.__init__(self, daemon = True)
        self.function= function

    def run(self):
        self.function()