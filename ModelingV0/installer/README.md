###Install dependencies:
````shell
command: cd modeling/ModelingV0/installer/
command: chmod +x installer.sh
command: ./installer.sh
````
### Download Gurobi Optimizer in :
https://www.gurobi.com/downloads/gurobi-software/

###Install  Gurobi:
https://www.gurobi.com/documentation/9.1/remoteservices/linux_installation.html

###Create Gurobi license in:
https://www.gurobi.com/downloads/free-academic-license/

###Active Gurobi license in command/terminal prompt:
````shell
command: grbgetkey "pastelicense"
````

###Execute the Model:
````shell
command: cd modeling/ModelingV0/optimization/
command: python3.9 discrete_event_manager.py
````
###Execute the Instance Generator:
````shell
command: cd modeling/ModelingV0/generator/
command: python3.9 generate_new_instance.py
````

Model configuration is in config/config_model.json

Instance generator is in config/generator.json

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
````
>RuntimeError: This package is deprecated. See the deprecation notice above.
````shell
command: sudo apt-get install python-igraph
````