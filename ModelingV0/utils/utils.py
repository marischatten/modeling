import json

def get_data(filename) -> object:
    with open(filename, "r", encoding='utf8') as f:
        return json.load(f)

# def write_data(filename):
#   with open(filename,"w",encoding='utf8') as f:
