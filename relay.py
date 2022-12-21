import socket
from cryptography.fernet import Fernet
import threading
import requests


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, key):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.key = key
        self.clientsocket = clientsocket
        print("[+] New thread for %s %s" % (self.ip, self.port,))

    def run(self):
        print("Connection from %s %s" % (self.ip, self.port,))
        message = self.clientsocket.recv(1024).decode()
        message = eval(message)
        print("Message received from client is: ", message)
        if(message[0] == "key_request"):
            self.clientsocket.send(self.key)
            self.clientsocket.close()
        elif(message[0] == "send_to_next"):
            submessage = message[1]
            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(submessage.encode()).decode()
            decrypted = eval(decrypted)
            if(decrypted[0] == "last_node"):
                resp = eval(decrypted[1])
                resp = str(resp)
                self.clientsocket.send(resp.encode())
            else:
                relay_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                relay_socket.connect(('127.0.0.1', int(decrypted[0])))
                relay_socket.send(str(['send_to_next', decrypted[1]]).encode())
                resp = relay_socket.recv(4096)
                relay_socket.close()
                self.clientsocket.send(resp)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9090))
    my_adress = int(s.recv(1024).decode())
    s.send("relay_connecting".encode())

    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind(('127.0.0.1', my_adress))

    key = Fernet.generate_key()
    while True:
        tcpsock.listen(10)
        print("Relay listening...")
        (clientsocket, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port, clientsocket, key)
        newthread.start()


if __name__ == "__main__":
    main()
