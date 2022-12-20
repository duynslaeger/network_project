import socket
from cryptography.fernet import Fernet
import numpy as np


HOST = '127.0.0.1'
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))  # this sends a request to the "server"
# Est ce que mettre le rcv dans le int() peut poser un soucis ? Apparemment non
my_adress = int(s.recv(1024).decode())

# message = input(
#     "Please paste the link of the website you would like to visit (https:// is required): \n")


# Request the list of the addresses to the gateway
s.send("adresses_request".encode())
nodes_ports = s.recv(4096)
nodes_ports = eval(nodes_ports.decode())


# Sélectionner aléatoirement "length" ports parmi la liste des relais/clients disponibles

length = len(nodes_ports) - 1  # -1 for not counting ourselves

rgen = np.random.default_rng()
rand_path_length = rgen.integers(low=1, high=length, size=1)[0]

path_addresses = []
used = [my_adress]
count = 0

while(count < rand_path_length):
    rand_index = rgen.integers(low=0, high=length - 1, size=1)[0]
    if(nodes_ports[rand_index] not in used):
        path_addresses.append(int(nodes_ports[rand_index]))
        used.append(int(nodes_ports[rand_index]))
        count += 1

print(path_addresses)

keys = []

for relay_port in path_addresses:
    relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    relay_socket.connect((HOST, relay_port))
    relay_socket.send('key_request'.encode())
    response = relay_socket.recv(1024).decode()
    keys.append(response)


rev_keys = reversed(keys)
print(keys)

message = 'https://www.ecosia.org/'
# QUESTION : est ce que les ports des relais auront toujours la même taille ?

# Here we prepare the last message. When the last relais will find the first part of the message as "last_node", it knows that it needs to open the browser
f = Fernet(keys[-1])
new_message = 'last_node' + message
message = f.encrypt(new_message.encode()).decode()
# Here we prepare the other messages
for i in reversed(range(len(keys) - 1)):
    f = Fernet(keys[i])
    new_message = str(path_addresses[i]) + message
    message = f.encrypt(new_message.encode()).decode()

# print(message)

# ----------- Uncomment the next lines for sending the encrypted message to the first relay -----------

# relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# relay_socket.connect((HOST, path_addresses[0]))
# relay_socket.send('send_to_next'.encode())
# relay_socket.send(message.encode())
