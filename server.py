# coding: utf-8

import socket
import threading
import time

class ClientThread(threading.Thread):
    """ Here we define the thread that will handle the client
     It will receive the ip and port of the client and the socket
     in th run function, we will handle the connect to client and 
     we relay and check if they are still connected every 5 seconds"""

    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        # print("[+] New thread for %s %s \n" % (self.ip, self.port,))

    def run(self):
        print("Server connection from %s %s \n" % (self.ip, self.port,))        
        # here we send the port of the client to the client.
        self.clientsocket.send(str(self.port).encode())
        # here we receive the message from the client to validate the connection
        message = self.clientsocket.recv(1024).decode()
        # here we check if the client is a relay or a client
        if(message == "adresses_request"):                               # if it is a client, we send the list of relays to the client
            list_to_send = str(ports_list)
            self.clientsocket.send(list_to_send.encode())
        elif(message == "relay_connecting"):                             # if it is a relay, we add it to the list of relays
            ports_list.append(self.port)
            print("Relay ", self.port," connected to the server\n")
        
        # Check if client is still connected
        while True:
            try:
                self.clientsocket.send(b'ping')
                time.sleep(5)
            except socket.error as e:
                self.clientsocket.close()
                if self.port in ports_list:
                    ports_list.remove(self.port)
                break
        return

def main():
    # Here we create the socket and we bind it to the port 9090
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind(('127.0.0.1', 9090))

    while True:
        tcpsock.listen() # 10 is the number of connections that can be queued
        print("Server listening...\n")
        (clientsocket, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port, clientsocket)
        newthread.start()

if __name__ == "__main__":
    ports_list = []
    main()
