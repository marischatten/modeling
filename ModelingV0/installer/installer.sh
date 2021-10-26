#!/bin/bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.9
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt
sudo apt-get install -y python-typing
pip install tqdm --upgrade
pip install seaborn --upgrade
pip install python-igraph --upgrade
pip install cairocffi --upgrade
pip install openpyxl --upgrade
sudo python3.9 -m pip install --upgrade Pillow
echo "Dependencies Installed."

