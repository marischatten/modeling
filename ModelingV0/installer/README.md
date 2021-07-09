###Install dependencies:
````shell
command: chmod +x installer.sh
````
````shell
command: ./installer.sh
````
### Download Gurobi Optimizer in :
https://www.gurobi.com/downloads/gurobi-optimizer-eula/

###Create Gurobi license in:
https://www.gurobi.com/downloads/free-academic-license/

###Active Gurobi license in command/terminal prompt:
````shell
command: grbgetkey "pastelicense"
````

###Execute the Model:
````shell
command: python3 discrete_event_manager.py
````
###Execute the Instance Generator:
````shell
command: python3 generate_new_instance.py
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