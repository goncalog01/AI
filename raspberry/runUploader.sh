#!/bin/bash

sleep 60

while ! lsusb | grep -q "Playstation"
do
    sleep 15
done

sudo motion -n &
motionPID=$!

sleep 5

watch -n 15 python /home/grupo7/imageUploader.py &
clientPID=$!

while lsusb | grep -q "Playstation"
do
    sleep 10
done

sudo kill "$motionPID"
sudo kill "$clientPID"

shutdown now