###Install dependencies:
````shell
command: chmod +x installer.sh
````
````shell
command: ./installer.sh
````
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
