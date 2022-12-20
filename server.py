# coding: utf-8

import socket
import threading

# To find automatically the private local adress run :
# host = socket.gethostbyname(socket.gethostname()) (won't work if using virtual box. If using it, it will take the ip adress of the virtual machine)
# Dans notre cas, c'est une bonne chose si le serveur accepte toutes les requêtes
# Ici on a deux socket, un hosting socket (tcpsock) et un individual socket used for communicating with an individual client

ports_list = []


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port,))

    def run(self):
        print("Connexion de %s %s" % (self.ip, self.port,))


# AF_INET means it is used for internet
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SOCK_STREAM -> TCP
# SOCK_DGRAM -> UDP
# ???? Qu'est ce que ça fait, ça ? ????
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 127.0.0.1 ip of local host (juste sur cet ordinateur)
tcpsock.bind(('127.0.0.1', 9090))

while True:
    tcpsock.listen(10)
    print("En écoute...")
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()

    ports_list.append(port)
    print(ports_list)

    # Ici, j'envoie au client son port pour qu'il puisse le connaitre
    clientsocket.send(str(port).encode())

    message = clientsocket.recv(1024).decode()
    print("Message from client is: ", message)
    if(message == "adresses_request"):
        list_to_send = str(ports_list)
        clientsocket.send(list_to_send.encode())
