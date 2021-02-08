# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
from igraph import *
from modeling.optimize import *

from utils import utils as u
from simulation import request as r

alpha = 0
beta = 0
phi = 0
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

rtt_base = 0

avg_rtt = 0
sd_rtt = 0

previous_path = None

adj = None


def main():
    path = r'..\dataset\instance_1.json'  # args[0]
    dataset = u.get_data(path)
    convert_to_object(dataset)

    d = Data(alpha, beta, phi, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, resources_file,
             bandwidth_min_file, resources_node, file_user_request,rtt_base, avg_rtt, sd_rtt,
             )

    hd = HandleData(d)
    id = InfoData(d)
    od = OptimizeData(d, "Orchestrator")

    num_request = 10
    request = r.Request.generate_request(num_request, (num_bs + 1), (num_bs + num_ue), num_files)

    hd.calc_diff_bandwidth()
    hd.calc_bandwidth_current_edge()
    #hd.calc_actual_resources_node()
    hd.calc_weight_file_edge()
    d.resources_file_to_dictionary()
    # id.log_weight_dict()
    # id.log_total_bandwidth()
    # id.log_rtt_edge()
    # id.log_map_node_file()
    # id.log_weight_file_edge()
    # id.log_actual_resources_node()
    # id.log_bandwidth_actual_edge()
    # id.log_resources_file_dict()

    od.create_vars()
    od.set_function_objective()
    od.create_constraints()
    od.execute()
    #od.result()

    picture()
    print("SUCCESS!")


def picture():
    g = Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue
    for i, name in enumerate(key_nodes):
        g.add_vertex(name)

    for i, name_orig in enumerate(key_nodes):
        for j, name_dest in enumerate(key_nodes):
            if adj[i][j] == 1:
                g.add_edge(name_orig, name_dest)

    plot(g,vertex_label=key_nodes,vertex_color="white")


def convert_to_object(dataset):
    global alpha
    global beta
    global phi
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
    global rtt_base
    global avg_rtt
    global sd_rtt
    global map_node_file
    global previous_path
    global adj

    alpha = float(dataset["alpha"])
    beta = float(dataset["beta"])
    phi = float(dataset["phi"])
    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    resources_file = dataset["resources_file"]
    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    if num_bs is not None and num_ue is not None and num_files is not None:
        file_user_request = [[0 for u in range(num_bs + num_ue)] for f in range(num_files)]
        file_user_request = dataset["file_user_request"]

    if num_bs is not None and num_ue is not None:
        total_bandwidth_edge = [[0 for i in range(num_bs + num_ue)] for j in range(num_bs + num_ue)]
        total_bandwidth_edge = dataset["total_bandwidth_edge"]

    rtt_base = int(dataset["rtt_base"])
    avg_rtt = int(dataset["avg_rtt"])
    sd_rtt = int(dataset["sd_rtt"])

    previous_path = dataset["previous_path"]

    adj = dataset["adj"]


if __name__ == "__main__":
    main()
