import os
from random import randrange

import numpy as np
import utils.utils as u


path_locations = ''
num_events = 0
key_index_bs = list()
key_index_ue = list()
mobility_rate = 0

locations = list()


def main():
    global locations
    if os.name == 'nt':
        path_config = r'..\config\config_generator_locations.json'
    else:
        path_config = r'../config/config_generator_locations.json'
    data = u.get_data(path_config)
    load_configs(data)
    create_locations()
    write_locations(path_locations)
    print("Success generating localization!")


def create_locations():
    global locations
    locations = [[[0 for i in range(len(key_index_bs))] for j in range(len(key_index_ue))] for e in range(num_events)]
    for e in range(num_events):
        for u in range(len(key_index_ue)):
            for i in range(len(key_index_bs)):
                dis = randrange(-mobility_rate, mobility_rate+1)
                locations[e][u][i] = int(dis)


def load_configs(config: object):
    global path_locations, num_events, key_index_bs, key_index_ue, mobility_rate
    path_locations = config["path_locations"]
    num_events = config["num_events"]
    mobility_rate = config["mobility_rate"]
    key_index_bs = config["key_index_bs"]
    key_index_ue = config["key_index_ue"]


def write_locations(path):
    data = {
        "locations": locations,
    }
    u.write_data(path, data)


if __name__ == "__main__":
    main()
