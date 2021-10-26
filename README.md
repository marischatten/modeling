#### This is an optimal model of cooperative caching policies network-aware to join placement caching problem and mult-hops requests routing problem for the heterogeneous cellular networks. The objective is to decrease delay and increase cache hit. There are constraints of storage and Quality Service requirements defined by SLA(Service Level Agreement).

### Install dependencies:
````shell
command: cd optimization/ModelingV0/installer/
command: chmod +x installer.sh
command: ./installer.sh
````
### Download Gurobi Optimizer in :

https://www.gurobi.com/downloads/gurobi-software/

ou

````shell
command: wget https://packages.gurobi.com/9.1/gurobi9.1.2_linux64.tar.gz
````

### Install  Gurobi:

https://www.gurobi.com/documentation/9.1/remoteservices/linux_installation.html
````shell
command: tar xvfz gurobi_server9.1.2_linux64.tar.gz
command: cd gurbi912/linux64/src/build
command: make
command: mv libgurobi_c++.a ../../lib
command: cd /home/linux
command: sudo nano .bashrc
````
Insert in file:
export GUROBI_HOME="/home/linux/gurobi912/linux64"
export PATH="${GUROBI_HOME}/bin:${PATH}"
export LD_LIBRARY_PATH = "${LD_LIBRARY_PATH}:${GUROBI_HOME}/lib"

Warning! /home/linux = pwd
````shell
command: pwd
````

### Create Gurobi license in:

https://www.gurobi.com/downloads/free-academic-license/

### Active Gurobi license in command/terminal prompt:
````shell
command: grbgetkey "pastelicense"
````

### Execute the Model:
Model configuration is in config/config_model.json
````shell
command: cd optimization/ModelingV0/config/
command: python3.9 ../application discrete_event_manager.py
````

### Execute the Instance Generator:
Instance generator is in config/config_generator_instance.json
````shell
command: cd optimization/ModelingV0/config/
command: python3.9 ../application/generate_new_instance.py
````

### Execute the Locations Generator:
Instance generator is in config/config_generator_locations.json
````shell
command: cd optimization/ModelingV0/config/
command: python3.9 ../application/generate_locations.py
````

### Execute the Requests Generator:
Instance generator is in config/config_generator_request.json
````shell
command: cd optimization/ModelingV0/config/
command: python3.9 ../application/generate_requests.py
````

### Install Make
````shell
command: sudo apt install build-essential
````

### Debug and Build
````shell
command: sudo snap install pycharm-professional --classic
````

### Update requirements file
````shell
command: pip3 list --format=freeze > requirements.txt
````

###Install Virtual Environment
````shell
command: sudo apt install python3.9-venv
command: python3.9 -m venv <Dir>
````

###Set python version default
````shell
command: which python3
command: sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
````

###Errors
>ImportError: cannot import name '_imaging' from 'PIL'
````shell
command: python3.9 -m pip install --upgrade Pillow
````
>NoModule
````shell
command: sudo apt-get install tqdm
command: sudo apt-get install seaborn
command: sudo apt-get install -y python-typing
command: pip install tqdm --upgrade
command: pip install seaborn --upgrade
command: pip install python-igraph --upgrade
command: pip install cairocffi --upgrade
command: pip install openpyxl --upgrade
command: pip install gurobipy or python3 -m pip install gurobipy
````
>RuntimeError: This package is deprecated. See the deprecation notice above.
````shell
command: sudo apt-get install python-igraph
````