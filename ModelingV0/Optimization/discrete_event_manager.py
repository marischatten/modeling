# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
# pip install tqdm
# pip install scipy
# pip install seaborn
#pip install openpyxl


import time
import tqdm
import seaborn as sns
from scipy import special

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
from ortools.graph import pywrapgraph

import igraph as ig
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

e_bs_adj = list()

resources_file = list()
phi = list()
bandwidth_min_file = list()

resources_node = list()

rtt_base = list()

distance_ue = list()
distance_bs = list

gama = list()
radius_mbs = 0
radius_sbs = 0

data = None

show_log = 0
show_results = False
show_path = False
show_var = False
show_par = False
plot_distribution = False
save_data = False
show_all_paths = False
type = Type.ZIPF
path_output = '..\output\instance_2.xlsx'

def main():
    #########################################################################################################################
    path = r'..\dataset\instance_2.json'  # args[0]

    # random and distribution.
    avg_qtd_bulk = 2
    num_events = 10
    num_alpha = 0.56

    # single.
    source = np.array(['F1'])
    sink = np.array(['UE3'])

    #########################################################################################################################

    dataset = u.get_data(path)
    convert_to_object(dataset)

    global data
    data = make_data()
    calc_vars()
    start_time = time.time()
    discrete_events(type, source=source, sink=sink, avg_qtd_bulk=avg_qtd_bulk, num_events=num_events,
                    num_alpha=num_alpha)
    print(CYAN, "FULL TIME --- %s seconds ---" % (time.time() - start_time), RESET)

    picture()
    # min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # pywraplp.Solver('test', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)


def discrete_events(type, source=None, sink=None, avg_qtd_bulk=0, num_events=0, num_alpha=0.0):
    if type == Type.SINGLE:
        single(source, sink)
    if type == Type.POISSON:
        bulk_distribution_poisson(avg_qtd_bulk, num_events)
    if type == Type.ZIPF:
        bulk_poisson_req_zipf(num_alpha, avg_qtd_bulk, num_events)
    if type == Type.ALLTOALL:
        all_to_all()
    if type == Type.RANDOM:
        random_request(avg_qtd_bulk, num_events)


def single(source, sink):
    pd = PlotData(data)
    handler = HandleData(data)

    path = create_model(source, sink)
    handler.path = path
    handler.update_data()
    allocated_request(pd, path)
    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    #pd.plot()


def bulk_distribution_poisson(avg_size_bulk, num_events):
    pd = PlotData(data)
    handler = HandleData(data)

    bulks = r.Request.generate_bulk_poisson(avg_size_bulk, num_events)

    if plot_distribution:
        plot_poisson(bulks)

    for event in tqdm.tqdm(range(num_events)):  # EVENTS IN TIMELINE
        qtd_req = bulks[event]
        sources = r.Request.generate_sources_random(qtd_req, key_index_file)
        sinks = r.Request.generate_sinks_random(qtd_req, key_index_ue)
        for req in range(qtd_req):
            source = sources[req]
            sink = sinks[req]

            source = [source]
            sink = [sink]
            path = create_model(source, sink)
            handler.path = path
            handler.update_data()
            allocated_request(pd, path)

    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    # pd.plot()


def bulk_poisson_req_zipf(num_alpha, avg_size_bulk, num_events):
    pd = PlotData(data)
    handler = HandleData(data)
    init = 0
    bulks = r.Request.generate_bulk_poisson(avg_size_bulk, num_events)
    zipf = r.Request.generate_sources_zip(num_alpha, sum_requests(bulks), key_index_file)

    if plot_distribution:
        plot_poisson(bulks)
        plot_zipf(zipf, num_alpha)

    for event in tqdm.tqdm(range(num_events)):  # EVENTS IN TIMELINE
        qtd_req = bulks[event]
        sources = get_req(zipf, init, qtd_req)
        sinks = r.Request.generate_sinks_random(qtd_req, key_index_ue)
        for req in range(qtd_req):
            source = sources[req]
            sink = sinks[req]

            source = [source]
            sink = [sink]
            path = create_model(source, sink)
            handler.path = path
            handler.update_data()
            allocated_request(pd, path)
        init = qtd_req
    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    #pd.plot()


def get_req(zipf, qtd_previous, qtd):
    if qtd_previous == 0:
        return zipf[:qtd]
    else:
        return zipf[qtd_previous:qtd_previous + qtd]


def all_to_all():
    pd = PlotData(data)
    handler = HandleData(data)

    for s in tqdm.tqdm(key_index_file):
        for t in key_index_ue:
            source = np.array([s])
            sink = np.array([t])
            path = create_model(source, sink)
            handler.path = path
            handler.update_data()
            allocated_request(pd, path)

    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    # pd.plot()


def random_request(qtd_bulk, num_events):
    pd = PlotData(data)
    handler = HandleData(data)

    for num_blocks in range(num_events):
        sources = r.Request.generate_sources_random(qtd_bulk, num_events)
        sinks = r.Request.generate_sinks_random(qtd_bulk, num_events)
        for req in tqdm.tqdm(range(qtd_bulk)):
            source = np.array(sources[req])
            sink = np.array(sinks[req])
            path = create_model(source, sink)
            handler.path = path
            handler.update_data()
            allocated_request(pd, path)

    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    # pd.plot()


def sum_requests(bulks):
    all_req = 0
    for i in range(len(bulks)):
        all_req += bulks[i]
    return all_req


def plot_poisson(distribution):
    sns.displot(distribution)
    plt.xlim([0, 25])
    plt.xlabel('k')
    plt.ylabel('P(X=k)')
    plt.show()


def plot_zipf(distribution, alpha):
    plt.hist(distribution, bins=np.arange(1, num_files + 1),density=True)
    #plt.hist(distribution[distribution < 10], 10, density=True)
    #x = np.arange(1., 10.)
    #y = x ** (-alpha) / special.zetac(alpha)
    #plt.yscale('log')
    plt.title('Zipf')
    plt.xlabel('rank')
    plt.ylabel('frequency')
    #plt.plot(x, y / max(y), linewidth=2, color='r')
    plt.show()


def make_data():
    return Data(alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, e_bs_adj,
                resources_file, phi,
                bandwidth_min_file, resources_node, rtt_base, radius_mbs, radius_sbs,
                gama, distance_ue, distance_bs
                )


def create_model(source, sink):
    if show_par:
        show_parameters()
    if show_var:
        show_vars()
    return run_model(source, sink)


def run_model(source, sink):
    od = OptimizeData(data=data, source=source, sink=sink)
    od.model = gp.Model("Orchestrator")
    od.create_vars()
    od.set_function_objective()
    od.create_constraints()
    od.execute(show_log)
    if show_results:
        print(GREEN, "\nContent:", source, " to User:", sink)
        od.result()
    return od.solution_path(show_path)


def allocated_request(pd, path) -> object:
    pd.insert_path(path)
    return pd


def calc_vars():
    hd = HandleData(data)
    hd.calc_vars()


def show_parameters():
    ld = LogData(data)
    ld.show_parameters()


def show_vars():
    id = LogData(data)
    id.show_vars_matrix()
    # id.show_vars_dict()


def picture():
    g = ig.Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue + key_index_file
    for i, name in enumerate(key_nodes):
        g.add_vertex(name)

    for f, filename in enumerate(key_index_file):
        for i, name_orig in enumerate(key_nodes):
            for j, name_dest in enumerate(key_nodes):
                if data.weight_dict is not None:
                    if data.weight_dict[filename, name_orig, name_dest] <= 9999:
                        g.add_edge(name_orig, name_dest)

    # print(g.get_adjacency())
    # ig.plot(g, layout="kk", vertex_label=range(g.vcount()))
    # g.save('..\output\instance_1.pdf')


def convert_to_object(dataset: object):
    global alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, e_bs_adj, resources_file, phi, bandwidth_min_file, resources_node, rtt_base, gama, distance_ue, distance_bs, radius_mbs, radius_sbs, avg_rtt, sd_rtt

    alpha = dataset['alpha']
    beta = float(dataset["beta"])

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    e_bs_adj = dataset["e_bs_adj"]

    resources_file = dataset["resources_file"]

    if num_bs is not None and num_files is not None:
        phi = [[0 for i in range(num_bs)] for f in range(num_files)]
        phi = dataset["phi"]

    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    rtt_base = dataset["rtt_base"]

    if num_bs is not None and num_ue is not None and num_files is not None:
        gama = [[0 for i in range(num_bs + num_ue)] for f in range(num_files)]
        gama = dataset["gama"]

    if num_bs is not None and num_ue is not None:
        distance_ue = [[0.0 for i in range(num_bs)] for u in range(num_ue)]
        distance_ue = dataset["distance_ue"]

    if num_bs is not None:
        distance_bs = [[0.0 for i in range(num_bs)] for u in range(num_bs)]
        distance_bs = dataset["distance_bs"]

    radius_mbs = int(dataset["radius_mbs"])
    radius_sbs = int(dataset["radius_sbs"])


if __name__ == "__main__":
    main()
