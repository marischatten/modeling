# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
import numpy as np

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  #https://developers.google.com/optimization/introduction/python
from ortools.graph import pywrapgraph

from igraph import *
from modeling.optimize import *
import matplotlib.pyplot as plt

from utils import utils as u
from simulation import request as r

alpha = 0
beta = 0

num_bs = 0
num_ue = 0
num_files = 0

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

x_bs_adj = list()

resources_file = list()
phi = list()
bandwidth_min_file = list()

resources_node = list()

rtt_base = list()

loc_BS_node = list()
loc_UE_node = list()

gama = list()
omega = list()
distance = 0

avg_rtt = 0
sd_rtt = 0


def main():
    path = r'..\dataset\instance_2.json'  # args[0]
    dataset = u.get_data(path)
    convert_to_object(dataset)

    num_request = 10
    request = r.Request.generate_request(num_request, (num_bs + 1), (num_bs + num_ue), num_files)

    #for i in range(num_request):
    #req = request[i]
    source = np.array(['F1'])
    sink = np.array(['UE9'])
    #sources = np.array(['F1', 'F2', 'F3','F4', 'F5', 'F6','F7', 'F8', 'F9','F10'])
    #sinks = np.array(['UE1', 'UE2', 'UE3','UE4', 'UE5', 'UE6','UE7', 'UE8', 'UE9','UE10', 'UE11'])
    #source = ""
    #sink = ""
    #for s in sources:
    #    for t in sinks:
    #        source = s
    #        sink = t
    #        print(source)
    #        print(sink)
    data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                         resources_file,phi,
                         bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt,loc_UE_node,loc_BS_node,gama,omega,
                            source,sink
                         )

    calc_vars(data)
    #show_parameters(data)
    #show_vars(data)
    run_model(data,"Orchestrator")

    #picture(data)

    #min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    #pywraplp.Solver('teste', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)


def run_model(data,name):
    od = OptimizeData(data,name)
    od.run_model()


def calc_vars(data):
    hd = HandleData(data)
    hd.calc_vars()


def show_parameters(data):
    id = InfoData(data)

    print("PARAMETERS.\n")
    id.log_phi()

    id.log_resources_file_dict()
    id.log_bandwidth_min_dict()

    id.log_resources_node_dict()
    id.log_phi_dict()

    id.log_rtt_base()
    id.log_rtt_edge()

    id.log_gama_file_node()
    id.log_x_bs_adj_dict()

def show_vars(data):
    id = InfoData(data)

    print("VARS.\n")
    #id.log_omega_user_node()
    #id.log_expected_bandwidth_edge()
    #id.log_current_bandwidth_edge()
    #id.log_diff_bandwidth_edge()
    #id.log_current_resources_node()
    #id.log_weight_file_edge()

    # dict
    #id.log_omega_user_node_dict()
    # id.log_expected_bandwidth_edge_dict()
    # id.log_current_bandwidth_edge_dict()
    # id.log_diff_bandwidth_edge_dict()
    #id.log_current_resources_node_dict()
    id.log_weight_dict()


def picture(data):
    g = Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue + key_index_file
    for i, name in enumerate(key_nodes):
        g.add_vertex(name)

    for f,filename in enumerate(key_index_file):
        for i, name_orig in enumerate(key_nodes):
            for j, name_dest in enumerate(key_nodes):
                if data.weight_dict[filename,name_orig,name_dest] <= 9999:
                    g.add_edge(name_orig, name_dest)

    plot(g, vertex_label=key_nodes, vertex_color="white")


def convert_to_object(dataset):
    global alpha
    global beta
    global num_bs
    global num_ue
    global num_files
    global key_index_file
    global key_index_bs
    global key_index_ue
    global x_bs_adj
    global resources_file
    global phi
    global bandwidth_min_file
    global resources_node
    global rtt_base
    global loc_BS_node
    global loc_UE_node
    global gama
    global omega
    global distance
    global avg_rtt
    global sd_rtt

    alpha = dataset["alpha"]
    beta = float(dataset["beta"])

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    x_bs_adj = dataset["x_bs_adj"]

    resources_file = dataset["resources_file"]

    if num_bs is not None and num_files is not None:
        phi = [[0 for i in range(num_bs)] for f in range(num_files)]
        phi = dataset["phi"]

    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    rtt_base = dataset["rtt_base"]

    if num_bs is not None:
        loc_BS_node = [[0 for j in range(3)]for i in range(num_bs)]
        loc_BS_node = dataset['loc_BS_node']
    if num_ue is not None:
        loc_UE_node = [[0 for j in range(3)] for u in range(num_ue)]
        loc_UE_node = dataset['loc_UE_node']

    if num_bs is not None and num_ue is not None and num_files is not None:
        gama = [[0 for i in range(num_bs+num_ue)] for f in range(num_files)]
        gama = dataset["gama"]

    if num_bs is not None and num_ue is not None:
        omega = [[0.0 for i in range(num_bs)] for j in range(num_ue)]
        omega = dataset["omega"]

    distance = int(dataset["distance"])

    avg_rtt = int(dataset["avg_rtt"])
    sd_rtt = int(dataset["sd_rtt"])


if __name__ == "__main__":
    main()
