import socket
from cryptography.fernet import Fernet
import threading


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9090))
my_adress = int(s.recv(1024).decode())
s.send("relay_connecting".encode())


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port,))

    def run(self):
        print("Connexion de %s %s" % (self.ip, self.port,))


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(('127.0.0.1', my_adress))

while True:
    tcpsock.listen(10)
    print("Relay launched")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()

    message = clientsocket.recv(1024).decode()
    print("Message received from client is: ", message)
    if(message == "key_request"):
        key = Fernet.generate_key()
        clientsocket.send(key)

    ## ----- TO DO -----
    # if(message == "send_to_next"):
    #     message = clientsocket.recv(4096).decode()
    #     fernet = Fernet(key)
    #     fernet.decrypt(message.decode())
    #-----------------