# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
#pip install tqdm
#pip install scipy
#pip install seaborn

import numpy as np
import time
import tqdm
import  seaborn as sns

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
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

    #random
    avg_bulk = 5
    num_events = 100

    num_alpha = 0.8

    #single
    source = np.array(['F5'])
    sink = np.array(['UE11'])

    #todos para todos
    sources = np.array(['F1'])
    sinks = np.array(['UE1'])

    start_time = time.time()
    #all(sources, sinks)
    single(source,sink)
    #bulk_distribuition_poisson(avg_bulk,num_events)
    #random_request(num_blocks,num_requests,sources,sinks)
    print(CYAN,"--- %s seconds ---" % (time.time() - start_time))

    # min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # pywraplp.Solver('teste', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)

def bulk_distribuition_poisson(avg_size_bulk,num_events):
    show = False
    bulks = r.Request.generate_bulk_poisson(avg_size_bulk, num_events)
    #r.Request.generate_bulk_zip(avg_size_bulk,num_events,bulks,num_events)
    print(bulks)
    sns.displot(bulks)
    plt.xlim([0,25])
    plt.xlabel('k')
    plt.ylabel('P(X=k)')
    plt.legend()
    plt.show()

    for event in tqdm.tqdm(range(num_events)): #EVENTS IN TIMELINE
        qtd_req = bulks[event]
        sources = r.Request.generate_sources_random(qtd_req,key_index_file)
        sinks = r.Request.generate_sinks_random(qtd_req, key_index_ue)
        for req in range(qtd_req):
            source = sources[req]
            sink = sinks[req]
            #if req == sources[-1] and req == sinks[-1]:
            show = True

            source = [source]
            sink = [sink]
            #print(GREEN,"\nOrigem:", source, "| Destino:", sink)
            data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                                resources_file, phi, bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt, loc_UE_node,
                                loc_BS_node, gama, omega, source, sink
                                )
            calc_vars(data)
            # show_parameters(data)
            # show_vars(data)
            #run_model(data, show)


def bulk_poisson_req_zipf(num_alpha,avg_size_bulk,num_events):
    show = False
    bulks = r.Request.generate_bulk_poisson(avg_size_bulk, num_events)
    for event in tqdm.tqdm(range(num_events)): #EVENTS IN TIMELINE
        qtd_req = bulks[event]
        sources = r.Request.generate_sources_random(qtd_req,key_index_file)
        sinks = r.Request.generate_sinks_random(qtd_req, key_index_ue)
        for req in range(qtd_req):
            source = sources[req]
            sink = sinks[req]
            #if req == sources[-1] and req == sinks[-1]:
            show = True

            source = [source]
            sink = [sink]
            #print(GREEN,"\nOrigem:", source, "| Destino:", sink)
            data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                                resources_file, phi, bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt, loc_UE_node,
                                loc_BS_node, gama, omega, source, sink
                                )
            calc_vars(data)
            # show_parameters(data)
            # show_vars(data)
            run_model(data, show)


def all(sources,sinks):
    show = False
    for s in tqdm.tqdm(sources):
        for t in sinks:
            source = np.array([s])
            sink = np.array([t])
            if s == sources[-1] and t == sinks[-1]:
                show = True
            #print(GREEN,"\nOrigem:", source, "| Destino:", sink)
            data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                        resources_file, phi, bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt, loc_UE_node,
                        loc_BS_node, gama, omega, source, sink
                        )
            calc_vars(data)
            #show_parameters(data)
            #show_vars(data)
            #run_model(data, show)


def random_request(num_blocks,num_requests,sources,sinks):
    show = False
    for num_blocks in range(num_blocks):
        #r.Request.generate_request_random(num_requests, key_index_file, key_index_ue, sources, sinks)
        for req in tqdm.tqdm(range(num_requests)):
            source = np.array(sources[req])
            sink = np.array(sinks[req])
            if req == sources[-1] and req == sinks[-1]:
                show = True
            print(GREEN,"\nOrigem:", source, "| Destino:", sink)
            data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                            resources_file, phi,
                            bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt, loc_UE_node,
                            loc_BS_node,
                            gama, omega,
                            source, sink
                            )
            calc_vars(data)
            # show_parameters(data)
            # show_vars(data)
            run_model(data, show)


def single(source,sink):
    show = True
    print(GREEN,"\nOrigem:", source, "| Destino:", sink)
    print("single",type(source),type(sink))
    data = Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, x_bs_adj,
                resources_file, phi,
                bandwidth_min_file, resources_node, rtt_base, distance, avg_rtt, sd_rtt, loc_UE_node,
                loc_BS_node,
                gama, omega,
                source, sink
                )
    calc_vars(data)
    #show_parameters(data)
    show_vars(data)
    run_model(data, show)


def run_model(data, show):
    od = OptimizeData(data, "Orchestrator")
    od.create_vars()
    od.set_function_objective()
    od.create_constraints()
    od.execute()
    if show:
        od.result()


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
    # id.log_omega_user_node()
    #id.log_expected_bandwidth_edge()
    #id.log_current_bandwidth_edge()
    # id.log_diff_bandwidth_edge()
    # id.log_current_resources_node()
    #id.log_weight_file_edge()

    # dict
    # id.log_omega_user_node_dict()
    id.log_expected_bandwidth_edge_dict()
    id.log_current_bandwidth_edge_dict()
    # id.log_diff_bandwidth_edge_dict()
    # id.log_current_resources_node_dict()
    #id.log_weight_dict()


def picture(data):
    g = Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue + key_index_file
    for i, name in enumerate(key_nodes):
        g.add_vertex(name)

    for f, filename in enumerate(key_index_file):
        for i, name_orig in enumerate(key_nodes):
            for j, name_dest in enumerate(key_nodes):
                if data.weight_dict[filename, name_orig, name_dest] <= 9999:
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
        loc_BS_node = [[0 for j in range(3)] for i in range(num_bs)]
        loc_BS_node = dataset['loc_BS_node']
    if num_ue is not None:
        loc_UE_node = [[0 for j in range(3)] for u in range(num_ue)]
        loc_UE_node = dataset['loc_UE_node']

    if num_bs is not None and num_ue is not None and num_files is not None:
        gama = [[0 for i in range(num_bs + num_ue)] for f in range(num_files)]
        gama = dataset["gama"]

    if num_bs is not None and num_ue is not None:
        omega = [[0.0 for i in range(num_bs)] for j in range(num_ue)]
        omega = dataset["omega"]

    distance = int(dataset["distance"])

    avg_rtt = int(dataset["avg_rtt"])
    sd_rtt = int(dataset["sd_rtt"])


if __name__ == "__main__":
    main()
