import socket
import os
import threading
import hashlib

# Create Socket (TCP) Connection
ServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a connection...')
ServerSocket.listen(5)
HashTable = {}


# Function : For each client
def threaded_client(connection):

    # Request Username
    connection.send(str.encode(
        'Do you want to login or to sign up ? [l/s] : '))
    print('\n')
    l_s = connection.recv(2048)

    if l_s == b's':

        connection.send(str.encode('ENTER USERNAME : '))  # Request Username
        name = connection.recv(2048)
        connection.send(str.encode('ENTER PASSWORD : '))  # Request Password
        password = connection.recv(2048)
        password = password.decode()
        name = name.decode()
        # Password hash using SHA256
        password = hashlib.sha256(str.encode(password)).hexdigest()
        # REGISTERATION PHASE
        # If new user,  regiter in Hashtable Dictionary
        if name not in HashTable:
            HashTable[name] = password
            connection.send(str.encode('Registeration successful'))
            print('Registered : ', name)
            print("{:<8} {:<20}".format('USER', 'PASSWORD'))
            for k, v in HashTable.items():
                label, num = k, v
                print("{:<8} {:<20}".format(label, num))
            print("-------------------------------------------")

        else:
            # If already existing user, check if the entered password is correct
            if (HashTable[name] == password):
                # Response Code for Connected Client
                connection.send(str.encode('Saving Failed'))
                print('Saving Failed : ', name)
            else:
                HashTable[name] = password
                connection.send(str.encode('Registeration Successful'))
                print('Registered : ', name)
                print("{:<8} {:<20}".format('USER', 'PASSWORD'))
                for k, v in HashTable.items():
                    label, num = k, v
                    print("{:<8} {:<20}".format(label, num))
                print("-------------------------------------------")
    elif l_s == b'l':
        connection.send(str.encode('ENTER USERNAME : '))  # Request Username
        name = connection.recv(2048)
        connection.send(str.encode('ENTER PASSWORD : '))  # Request Password
        password = connection.recv(2048)
        password = password.decode()
        name = name.decode()
        # Password hash using SHA256
        password = hashlib.sha256(str.encode(password)).hexdigest()
        # REGISTERATION PHASE
        # If new user,  regiter in Hashtable Dictionary
        if name not in HashTable:
            HashTable[name] = password
            connection.send(str.encode('Login Failed'))
            print('Login Failed : you have to change your name or/and your password')
            print("-------------------------------------------")

        else:
            # If already existing user, check if the entered password is correct
            if (HashTable[name] == password):
                # Response Code for Connected Client
                connection.send(str.encode('Connection Successful'))
                print('Connection : ', name)
                print("-------------------------------------------")
            else:
                HashTable[name] = password
                print("-------------------------------------------")


while True:
    Client, address = ServerSocket.accept()
    client_handler = threading.Thread(
        target=threaded_client,
        args=(Client,)
    )
    client_handler.start()
    ThreadCount += 1
    print('Connection Request: ' + str(ThreadCount))
ServerSocket.close()
