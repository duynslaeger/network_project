import socket
import time
from cryptography.fernet import Fernet
import numpy as np
import select


Server_HOST = '127.0.0.1'
Server_PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((Server_HOST, Server_PORT))  # connect to the gateway
my_adress = int(s.recv(1024).decode())

print("\nHello ! Welcome to our TOR network.\n \nIn this network, you have the choice between opening a web page, exctracting informations about a github user or authenticate to our server.\n")

answer = input("What would you like to do ? [web/git/server/quit] : ")

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
    message = "response=requests.get('https://api.github.com/users/" + \
        str(user) + "').json()"
elif(answer == "server"):
    message = "serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nserv.connect(('127.0.0.1', 1233))\nresponse=serv.recv(4096).decode()"
    print("\n")
    pass

# Request the list of the addresses to the gateway
s.send("adresses_request".encode())
nodes_ports = s.recv(4096)
nodes_ports = eval(nodes_ports.decode())
print("The total number of relays is : ", nodes_ports)

length = len(nodes_ports)
rgen = np.random.default_rng()
# now we choose the length of the path randomly
if(len(nodes_ports) == 1):
    rand_path_length = 1
else:
    rand_path_length = rgen.integers(low=1, high=length, size=1)[0]

path_addresses = []
used = [my_adress]
count = 0

while(count < rand_path_length):
    if(length == 1):
        rand_index = 0
    else:
        rand_index = rgen.integers(low=0, high=length - 1, size=1)[0]
    if(nodes_ports[rand_index] not in used):
        path_addresses.append(int(nodes_ports[rand_index]))
        used.append(int(nodes_ports[rand_index]))
        count += 1

print("The path is : ", path_addresses)

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

f = Fernet(keys[-1])
def encrypt_message(message):
    global f
    new_message = ['last_node', message]
    message = f.encrypt(str(new_message).encode()).decode()

    # Here we prepare the other messages
    for i in reversed(range(len(keys) - 1)):
        f = Fernet(keys[i])
        new_message = [str(path_addresses[i + 1]), message]
        message = f.encrypt(str(new_message).encode()).decode()
    return message



relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_socket.connect((Server_HOST, path_addresses[0]))
relay_socket.send(str(['send_to_next', encrypt_message(message)]).encode())

if(answer == "git"):
    responses = eval(relay_socket.recv(4096).decode())
    print("\n QUERY RESULT: \n the user of github %s has %s public(s) repository(s)\n" %
            (responses['login'], responses['public_repos']))
if(answer == "web"):
    print("\n QUERY RESULT: \n the web page was opened successfully \n")
if(answer == "server"):
    while True:
        response = relay_socket.recv(4096).decode()
        if(response == "end"):
            break
        else:
            print(response)
            message = "serv.send(b'"+input()+"')\nresponse=serv.recv(4096).decode()"
            relay_socket.send(str(['send_to_next', encrypt_message(message)]).encode())
relay_socket.close()
