# python -m pip install -i https://pypi.gurobi.com gurobipy
from modeling.optimize import Data
from modeling.optimize import HandleData
from modeling.optimize import InfoData
from modeling.optimize import OptimizeData
from utils import utils as u
from simulation import request as r


alpha = 0

num_bs = 0
num_ue = 0
num_files = 0

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

size_file = list()
resources_file = list()
bandwidth_min_file = list()

resources_node = list()

file_user_request = None

total_bandwidth_edge = None

avg_rtt = 0
sd_rtt = 0

map_node_file = None


def main():
    path = r'..\dataset\instance_1.json'  # args[0]
    dataset = u.get_data(path)
    convert_to_object(dataset)

    d = Data(alpha, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, size_file, resources_file,
             bandwidth_min_file, resources_node, file_user_request, total_bandwidth_edge, avg_rtt, sd_rtt, map_node_file)

    hd = HandleData(d)
    id = InfoData(d)
    od = OptimizeData(d)

    num_request = 10
    request = r.Request.generate_request(num_request, (num_bs+1), (num_bs + num_ue), num_files)

    id.log_weight_file_edge()
    hd.calc_bandwidth_actual_edge()
    hd.calc_actual_resources_node()
    hd.calc_weight_file_edge()

    id.log_total_bandwidth()
    id.log_rtt_edge()
    id.log_map_node_file()
    id.log_weight_file_edge()
    id.log_actual_resources_node()
    id.log_bandwidth_actual_edge()

    print("SUCESS!")


def convert_to_object(dataset):

    global alpha
    global num_bs
    global num_ue
    global num_files
    global key_index_file
    global key_index_bs
    global key_index_ue
    global size_file
    global resources_file
    global bandwidth_min_file
    global resources_node
    global file_user_request
    global total_bandwidth_edge
    global avg_rtt
    global sd_rtt
    global map_node_file

    alpha = float(dataset["alpha"])

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    size_file = dataset["size_file"]
    resources_file = dataset["resources_file"]
    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    if num_bs is not None and num_ue is not None and num_files is not None:
        file_user_request =  [[0 for u in range(num_bs+num_ue)] for f in range(num_files)]
        file_user_request = dataset["file_user_request"]

    if num_bs is not None and num_ue is not None:
        total_bandwidth_edge = [[0 for i in range(num_bs+num_ue)] for j in range(num_bs+num_ue)]
        total_bandwidth_edge = dataset["total_bandwidth_edge"]

    avg_rtt = int(dataset["avg_rtt"])
    sd_rtt = int(dataset["sd_rtt"])

    map_node_file = dataset["map_node_file"]


if __name__ == "__main__":
    main()
