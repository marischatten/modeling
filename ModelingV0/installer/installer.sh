#!/bin/bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
echo "Dependencies Installed."

