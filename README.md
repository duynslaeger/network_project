# Communication Network Project : TOR Network

## Instruction to install the packages required for running the network

To install the packages required for running the network, run the following command : 
```sh
$ pip install -r requirements.txt
```
Or, if you are using python3 :
```sh
$ pip3 install -r requirements.txt
```

## Instruction to launch the network (run the code) and close it

- To launch the TOR network, go to your directory where this project's files are and run the following command : 
	```sh
	$ bash launch_network.sh n
	```
with "n" the number of relays you want in the network. 
***Note*** : this bash script can only be executed in linux or in macOS. If you are on windows or any other OS, you might have to run every script separately by doing : 
	```sh
	$ python server.py
	```
for running the server, and
	```sh
	$ python relay.py
	```
for running a relay (execute it n times in n terminals if you want n relays)


- To launch a client : 

	```sh
	$ python client_TOR.py
	```
After launching the client, instructions will be given to you. Follow them to make your request to the network. You can either conncet to a web page typing "web", receive informations about the number of public git repositories of a git user byt typing "git" or login/sign up to a server by typing "server". **Attention** : specific conditions need to be required for login/sign up on the server. Please see next section. 

- If you want to connect and login in a server (Challenge-Response based Authentication) : 
	The launcher_network.sh has to be launched with **nor more than 2** relays for doing this. If we have more than two relays, we have a problem that we discuss more in details in the report. Once the network_launcher is launched, run the server_auth.py script : 
	```sh
	$ python server_auth.py
	```
	And then run the client_TOR.py and type "server". 

- If you want to launch an additionnal relay after the TOR network has been created, just do :
	```sh
	$ python relay.py
	```

- To close the TOR network and kill all relays and clients :
 	```sh
	$ killall python
	```

The **killall** command required the **psmisc** package. If you don't have it, you can install it with : 
 	```sh
	$ sudo apt-get install psmisc
	```

***Warning*** : the ```killall python``` command will kill every python processes running on your computer. Use it conscienciously. 


