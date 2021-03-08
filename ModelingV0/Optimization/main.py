# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
from igraph import *
from modeling.optimize import *

from utils import utils as u
from simulation import request as r

alpha = 0
phi = 0

num_bs = 0
num_ue = 0
num_files = 0

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

resources_file = list()
map_user_file = list()
bandwidth_min_file = list()

resources_node = list()

rtt_base = list()

loc_BS_node = list()
loc_UE_node = list()

gama = list()
distance = 0

avg_rtt = 0
sd_rtt = 0


def main():
    path = r'..\dataset\instance_1.json'  # args[0]
    dataset = u.get_data(path)
    convert_to_object(dataset)

    num_request = 10
    request = r.Request.generate_request(num_request, (num_bs + 1), (num_bs + num_ue), num_files)

    #for i in range(num_request):
    #req = request[i]
    req = 0
    d = Data(alpha, phi, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue,
                 resources_file,map_user_file,
                 bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt,loc_UE_node,loc_BS_node,gama,req
                 )

    hd = HandleData(d)
    id = InfoData(d)
    od = OptimizeData(d, "Orchestrator")

    hd.calc_omega_user_node()
    hd.calc_expected_bandwidth_edge()
    hd.calc_current_bandwidth_edge()
    hd.calc_diff_bandwidth()
    hd.calc_actual_resources_node()
    hd.calc_weight_file_edge()

    d.resources_file_to_dictionary()

    #Parameters
    print("PARAMETERS.\n")
    id.log_map_user_file()

    id.log_resources_file_dict()
    id.log_bandwidth_min_dict()

    id.log_resources_node_dict()
    #id.log_map_user_file_dict()

    id.log_rtt_base()
    id.log_rtt_edge()

    id.log_gama_file_node()

    #Vars
    print("VARS.\n")
    id.log_omega_user_node()
    id.log_expected_bandwidth_edge()
    id.log_current_bandwidth_edge()
    id.log_diff_bandwidth_edge()
    #id.log_actual_resources_node()
    id.log_actual_resources_node_dict()

    #id.log_weight_dict()
    id.log_weight_file_edge()

    od.create_vars()
    od.set_function_objective()
    od.create_constraints()
    od.execute()
    od.result()

    # picture()
    print("SUCCESS!")


def picture():
    g = Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue
    for i, name in enumerate(key_nodes):
        g.add_vertex(name)

    for i, name_orig in enumerate(key_nodes):
        for j, name_dest in enumerate(key_nodes):
            #if adj[i][j] == 1:
                g.add_edge(name_orig, name_dest)

    plot(g, vertex_label=key_nodes, vertex_color="white")


def convert_to_object(dataset):
    global alpha
    global phi
    global num_bs
    global num_ue
    global num_files
    global key_index_file
    global key_index_bs
    global key_index_ue
    global resources_file
    global map_user_file
    global bandwidth_min_file
    global resources_node
    global rtt_base
    global loc_BS_node
    global loc_UE_node
    global gama
    global distance
    global avg_rtt
    global sd_rtt

    alpha = dataset["alpha"]
    phi = float(dataset["phi"])

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    resources_file = dataset["resources_file"]

    if num_bs is not None and num_ue is not None:
        map_user_file = [[0 for i in range(num_ue)] for f in range(num_files)]
        map_user_file = dataset["map_user_file"]

    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    rtt_base = dataset["rtt_base"]

    if num_bs is not None:
        loc_BS_node = [[0 for j in range(3)]for i in range(num_bs)]
        loc_BS_node = dataset['loc_BS_node']

    loc_UE_node = [[0 for j in range(3)] for u in range(num_ue)]
    loc_UE_node = dataset['loc_UE_node']

    if num_bs is not None and num_ue is not None and num_files is not None:
        gama = [[0 for i in range(num_bs+num_ue)] for f in range(num_files)]
        gama = dataset["gama"]

    distance = int(dataset["distance"])

    avg_rtt = int(dataset["avg_rtt"])
    sd_rtt = int(dataset["sd_rtt"])


if __name__ == "__main__":
    main()
