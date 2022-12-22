import socket
import time
from cryptography.fernet import Fernet
import numpy as np
import select
import ast


class TORClient:
    """A TOR client class that can connect to a TOR network and send messages through it.

    Attributes:
        client (socket): A socket object used for connecting to the TOR network.
        my_address (int): The address of the client within the TOR network.
    """
    def __init__(self, host, port):
        """Initialize the TORClient object with a connection to the TOR network.

        Args:
            host (str): The hostname or IP address of the machine hosting the TOR network.
            port (int): The port number of the machine hosting the TOR network.
        """
        # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.my_address = None

    def login_or_register(self):
        """Log in or register with the TOR network.

               Returns:
                   str: A message indicating the result of the login or registration attempt.
               """
        # receive a message from the server
        response = self.client.recv(2048)
        l_s = 'l'
        while True:
            l_s = input(response.decode())
            if l_s == 'l' or l_s == 's':
                break

        # send a message to the server
        self.client.send(str.encode(l_s))

        # receive a message from the server
        response = self.client.recv(2048)
        name = input(response.decode())

        # send a message to the server
        self.client.send(str.encode(name))

        # receive a message from the server
        response = self.client.recv(2048)
        password = input(response.decode())

        # send a message to the server
        self.client.send(str.encode(password))

        # receive a message from the server
        response = self.client.recv(2048)
        response = response.decode()
        return response


def get_path_and_keys(self):
    """Retrieve a path and keys for sending a message through the TOR network.

    Returns:
        tuple: A tuple containing the following:
            list: A list of integers representing the addresses of the relays in the path.
            list: A list of bytes objects representing the keys for encrypting the message at each relay.
    """
    # receive my address from the server
    self.my_address = int(self.client.recv(1024).decode())

    # request the list of addresses from the server
    self.client.send("adresses_request".encode())
    nodes_ports = self.client.recv(4096)

    # parse the list of addresses
    nodes_ports = ast.literal_eval(nodes_ports.decode())
    print("The total number of relays is : ", nodes_ports)
    # choose a random subset of the addresses to form the path
    length = len(nodes_ports)
    rgen = np.random.default_rng()
    if length == 1:
        rand_path_length = 1
    else:
        rand_path_length = rgen.integers(low=1, high=length, size=1)[0]
    path_addresses = []
    used = [self.my_address]
    count = 0
    while count < rand_path_length:
        rand_index = rgen.integers(low=0, high=length - 1, size=1)[0]
        if nodes_ports[rand_index] not in used:
            path_addresses.append(int(nodes_ports[rand_index]))
            used.append(int(nodes_ports[rand_index]))
            count += 1

            # generate a random sequence of keys
            keys = []

            for relay_port in path_addresses:
                relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    relay_socket.connect(("127.0.0.1", relay_port))
                    relay_socket.send(str(['key_request']).encode())
                    relay_socket.setblocking(0)  # indicate that the socket is non-blocking
                    ready = select.select([relay_socket], [], [], 5)
                    if ready[0]:
                        response = relay_socket.recv(1024).decode()
                        keys.append(response)
                except ConnectionRefusedError:
                    print("Connection to relay at port {} failed".format(relay_port))

            return path_addresses, keys


def send_message_through_tor(path_addresses, keys, message):
    """Send a message through the TOR network.

    Args:
        path_addresses (list): A list of integers representing the addresses of the relays in the path.
        keys (list): A list of bytes objects representing the keys for encrypting the message at each relay.
        message (str): The message to be sent through the TOR network.

    Returns:
        str: The message received by the final relay in the path.
    """
    # Encrypt the message using the keys
    f = Fernet(keys[-1])
    new_message = ['last_node', message]
    message = f.encrypt(str(new_message).encode()).decode()

    for i in reversed(range(len(keys) - 1)):
        f = Fernet(keys[i])
        new_message = [str(path_addresses[i + 1]), message]
        message = f.encrypt(str(new_message).encode()).decode()

    # Connect to the first node in the path and send the message
    relay_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    relay_socket.connect(("127.0.0.1", path_addresses[0]))
    relay_socket.send(str(["send_to_next", message]).encode())

    # Wait for a response from the final destination
    relay_socket.setblocking(0)
    ready = select.select([relay_socket], [], [], 5)
    if ready[0]:
        responses = eval(relay_socket.recv(4096).decode())
    else:
        responses = None
    relay_socket.close()

    return responses


def main():
    # create a TORClient instance and establish a connection with the server
    client = TORClient("127.0.0.1", 1233)

    # log in or register as a new user
    response = client.login_or_register()
    if response == 'Connection Successful':

        # the message to send through the TOR network
        message = "requests.get('https://api.github.com/users/Dlawlet').json()"

        # get the path and keys
        path, keys = get_path_and_keys(client)
        print("The path is : ", path)
        responses = send_message_through_tor(path, keys, message)
        print("\n QUERY RESULT: \n the user of github %s has %s public(s) repository(s)\n" % (
            responses['login'], responses['public_repos']))

    elif response == 'Login Failed':
        print('Login failed and you are disconnected')
        print('you have to run again client and have to connect ')

    elif response == 'Saving Failed':
        print('Saveing Failed and you are disconnected')
        # a change pour pouvoir se save directement
        print('you have to run again client if you want to save')

    else:
        # Si on tape
        print('save and disconnected you have to run again client to connect')


if __name__ == '__main__':
    main()


def main():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    # connection to hostname on the port.
    client.connect((host, 1233))

    # receive data from the server
    response = client.recv(1024).decode()
    print(response)

    # send a message to the server
    message = input("Enter your message: ")
    client.send(message.encode())

    # receive data from the server
    response = client.recv(1024).decode()
    print(response)
