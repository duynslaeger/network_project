import socket

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
# client.connect((target, port))
client.connect(('127.0.0.1', 1233))
response = client.recv(2048)
l_s = 'l'
while True:
    l_s = input(response.decode())
    if l_s == 'l' or l_s == 's':
        break

client.send(str.encode(l_s))

# Input UserName
response = client.recv(2048)
name = input(response.decode())
client.send(str.encode(name))


# Input Password
response = client.recv(2048)
password = input(response.decode())
client.send(str.encode(password))

''' Response : Status of Connection :
	1 : Registeration successful 
	2 : Connection Successful
	3 : Login Failed
'''
# Receive response
response = client.recv(2048)
response = response.decode()

if response == 'Connection Successful':
    #_________________________TO_DO___________________________________#
    #                                                                 #
    #      remplacer avec le code qui permet de communiquer ainsi     #
    #                                                                 #
    #_________________________TO_DO___________________________________#
    print('Connection Successful')
    print('You have to choose a request')
    print('tape m for message, tape etc')
    while True:
        client.send(bytes(input(""), 'utf-8'))
elif response == 'Login Failed':
    print('Login failed and you are disconnected')
    print('you have to run again client and have to connect ')
    client.close()
elif response == 'Saved Failed':
    print('Saveing Failed and you are disconnected')
    #a change pour pouvoir se save directement
    print('you have to run again client if you want to save')
    client.close()
else:
    #Si on tape
    print('save and disconnected you have to run again client to connect')
    client.close()