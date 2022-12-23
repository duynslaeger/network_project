import socket
from cryptography.fernet import Fernet
import threading
import requests
import webbrowser


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, key):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.key = key
        self.clientsocket = clientsocket
        # print("[+] New thread for %s %s \n" % (self.ip, self.port,))

    def run(self):
        # print("Realy connection from %s %s \n" % (self.ip, self.port,))
      while True:  
        message = self.clientsocket.recv(163840).decode()
        message = eval(message)
        # print("The message received at the relay ", self.port," is: ", message,"\n")
        if(message[0] == "key_request"):
            self.clientsocket.send(self.key)
            self.clientsocket.close()
        elif(message[0] == "send_to_next"):
            submessage = message[1]
            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(submessage.encode()).decode()
            decrypted = eval(decrypted)
            if(decrypted[0] == "last_node"):
                
                exec(str(decrypted[1]), globals(), locals())      
                respons = f'{locals()["response"]}'
                resp = str(respons)
                encr = fernet.encrypt(resp.encode())
                self.clientsocket.send(encr)
            else:
                relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                relay_socket.connect(('127.0.0.1', int(decrypted[0])))
                relay_socket.send(str(['send_to_next', decrypted[1]]).encode())
                resp = relay_socket.recv(16384)
                encr = fernet.encrypt(resp)
                self.clientsocket.send(encr)
                relay_socket.close()


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
        # print("Relay listening...\n")
        (clientsocket, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port, clientsocket, key)
        newthread.start()


if __name__ == "__main__":
    main()
