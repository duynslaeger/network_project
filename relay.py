import socket
from cryptography.fernet import Fernet
import threading
import requests


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
        message = clientsocket.recv(4096).decode()
        message = eval(message)
        print("Message received from client is: ", message[0])
        if(message[0] == "key_request"):
            self.clientsocket.send(key)
            self.clientsocket.close()
        elif(message[0] == "send_to_next"):
            submessage = message[1]
            print("message received")
            print(submessage)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(submessage.encode()).decode()
            print("decrypted")
            print(decrypted)
            decrypted = eval(decrypted)
            
            if(decrypted[0] == "last_node"):
                resp = eval(decrypted[1])
                resp = str(resp)
                self.clientsocket.send(resp.encode())
            else :
                print("sending to next node")
                relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                relay_socket.connect(('127.0.0.1', int(decrypted[0])))
                relay_socket.send(str(['send_to_next',decrypted[1]]).encode())
                print("message sent")
                print("waiting for response")
                resp= relay_socket.recv(4096)
                relay_socket.close()
                self.clientsocket.send(resp)

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(('127.0.0.1', my_adress))

key = Fernet.generate_key()
print("Relay launched")
while True:
    tcpsock.listen(10)
    print("En écoute...")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()

    
            
            

    #-----------------
