# Communication Network Project : TOR Network

## Instruction to launch the network (run the code) and close it

To launch the TOR network, go to your directory where this project's files are and run the following command : 

	'''sh
	$ bash launch_network.sh n
	'''

with "n" the number of relays you want in the network.

Then, to launch a client : 

	'''sh
	$ python client_TOR.py
	'''

After launching the client, instructions will be given to you. Follow them to make your request to the network.

If you want to launch an additionnal relay after the TOR network has been created, just do :

	'''sh
	$ python relay.py
	'''


To close the TOR network and kill all relays and clients :

 	'''sh
	$ killall python
	'''

The **killall** command required the **psmisc** package. If you don't have it, you can install it with : 

 	'''sh
	$ sudo apt-get install psmisc
	'''

***Warning*** : the **killall python** command will kill every python processes running on your computer. Use it conscienciously. 