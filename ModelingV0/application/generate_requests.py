import os

import utils.utils as u
from simulation.request import *

path_requests = ''
avg_qtd_bulk = 0
num_events = 0
num_alpha = 0
key_index_file = None
key_index_ue = None
num_files = 0
plot_distribution = False
fixed = False
requests = None
bulks = None


def main():
    global requests, bulks
    if os.name == 'nt':
        path_config = r'..\config\config_generator_request.json'
    else:
        path_config = r'../config/config_generator_request.json'
    data = u.get_data(path_config)
    load_configs(data)
    requests, bulks = Request.create_requests(avg_qtd_bulk, num_events, num_alpha, key_index_file, key_index_ue,
                                              num_files, plot_distribution, fixed)
    write_requests(path_requests)
    print("Success generating requests!")


def load_configs(config: object):
    global path_requests, avg_qtd_bulk, num_events, num_alpha, key_index_file, key_index_ue, num_files, plot_distribution, fixed
    path_requests = config["path_requests"]
    avg_qtd_bulk = config["avg_qtd_bulk"]
    num_events = config["num_events"]
    num_alpha = config["num_alpha"]
    key_index_file = config["key_index_file"]
    key_index_ue = config["key_index_ue"]
    num_files = config["num_files"]
    plot_distribution = config["plot_distribution"]
    fixed = config["fixed"]


def write_requests(path):
    data = {
        "requests": requests,
        "bulks": bulks.tolist()
    }
    u.write_data(path, data)


if __name__ == "__main__":
    main()
