###Create Gurobi license in:
https://www.gurobi.com/downloads/free-academic-license/

###Active Gurobi license in command/terminal prompt:
````shell
command: grbgetkey "pastelicense"
````
###Install dependencies:
````shell
command: ./intaller.sh
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