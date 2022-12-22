import socket
import time
from cryptography.fernet import Fernet
import numpy as np
import select


Server_HOST = '127.0.0.1' # Host IP
Server_PORT = 9090 # Arbitrary unused port

# Creates a socket to establish a TCP between the client and the gateway
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connects to the gateway
s.connect((Server_HOST, Server_PORT))
my_adress = int(s.recv(1024).decode())

print("\nHello ! Welcome to our TOR network.\n \nIn this network, you have the choice between opening a web page, exctracting informations about a github user or authenticate to our server.\n")

answer = input("What would you like to do ? [web/git/server] : ")


# Preparation of the messages
if(answer == "web"):
    print("\n")
    url = input(
        "Please paste the link of the web site you would like to visit (https:// required) : ")
    print("\n")
    message = "webbrowser.open('" + str(url) + "')"

elif(answer == "git"):
    print("\n")
    user = input(
        "Please enter the git username you want informations about : ")
    print("\n")
    message = "requests.get('https://api.github.com/users/" + \
        str(user) + "').json()"
elif(answer == "server"):
    message = str(['127.0.0.1', 1233])
    print("\n")
    pass

# Request the list of the addresses to the gateway
s.send("adresses_request".encode())
nodes_ports = s.recv(4096)
nodes_ports = eval(nodes_ports.decode())

length = len(nodes_ports)
rgen = np.random.default_rng()

# Now we choose the length of the path randomly
if(len(nodes_ports) == 1):
    rand_path_length = 1
else:
    rand_path_length = rgen.integers(low=1, high=length, size=1)[0]

path_addresses = []
used = [my_adress]
count = 0

# Select randomly "rand_path_length" number of relays
# The list "used" ensure that a relay won't be selected twice
while(count < rand_path_length):
    if(length == 1):
        rand_index = 0
    else:
        rand_index = rgen.integers(low=0, high=length - 1, size=1)[0]
    if(nodes_ports[rand_index] not in used):
        path_addresses.append(int(nodes_ports[rand_index]))
        used.append(int(nodes_ports[rand_index]))
        count += 1

# Asking every relays of the path to generate an enryption key
# And then register them in the "keys" list
keys = []
for relay_port in path_addresses:
    relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        relay_socket.connect((Server_HOST, relay_port))
        relay_socket.send(str(['key_request']).encode())
        # indicate that the socket is non-blocking
        relay_socket.setblocking(0)
        ready = select.select([relay_socket], [], [], 5)
        if ready[0]:
            response = relay_socket.recv(1024).decode()
            keys.append(response)
    except:
        print("connection failed")
        pass

# Preparation of the onion. We start with the message reserved for the last node
f = Fernet(keys[-1])
new_message = ['last_node', message]
message = f.encrypt(str(new_message).encode()).decode()

# Here we prepare the other messages
for i in reversed(range(len(keys) - 1)):
    f = Fernet(keys[i])
    new_message = [str(path_addresses[i + 1]), message]
    message = f.encrypt(str(new_message).encode()).decode()


# Connection to the first relay of the path and send it the onion
relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_socket.connect((Server_HOST, path_addresses[0]))
relay_socket.send(str(['send_to_next', message]).encode())
relay_socket.setblocking(0)
ready = select.select([relay_socket], [], [], 5)
if ready[0]:
    if(answer == "git"):
        responses = eval(relay_socket.recv(4096).decode())
        print("\n QUERY RESULT: \n the user of github %s has %s public(s) repository(s)\n" %
              (responses['login'], responses['public_repos']))
relay_socket.close()
