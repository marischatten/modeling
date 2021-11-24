#!/bin/bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.9
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
sudo apt-get install -y python-typing
sudo pip install tqdm --upgrade
sudo pip install seaborn --upgrade
sudo pip install python-igraph --upgrade
sudo pip install cairocffi --upgrade
sudo pip install openpyxl --upgrade
sudo python3.9 -m pip install --upgrade Pillow
sudo pip install gurobipy
echo "Dependencies Installed."

