#!/bin/bash

n=$1
python gateway.py &
sleep 0.1 #to ensure that the server is launched before the relays
for (( i=1 ; i<=$n ; i++ )); 
do
    python relay.py &
done

