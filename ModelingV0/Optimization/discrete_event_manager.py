# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
# pip install tqdm
# pip install scipy
# pip install seaborn
# pip install openpyxl


import time
import tqdm
import seaborn as sns

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
from ortools.graph import pywrapgraph

import igraph as ig
from modeling.optimize import *
import matplotlib.pyplot as plt

from utils import utils as u
from simulation import request as r

mobility_rate = 10

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
size_file = list()
phi = list()
throughput_min_file = list()

resources_node = list()

rtt_min = list()

distance_ue = list()
distance_bs = list

gama = list()
radius_mbs = 0
radius_sbs = 0

data = None

show_log = 0
show_results = True
show_path = False
show_var = False
show_par = False
plot_distribution = False
plot_data = False
show_all_paths = False
type = Type.SINGLE
mobility = Mobility.IS_MOBILE
model = Model.ONLINE

path_dataset = r'..\dataset\instance_3.json'

save_data = False
path_output = r'..\output\data\instance_3.xlsx'
plot_graph = True
path_graph = r'..\output\graph\instance_3.png'

# random and distribution.
avg_qtd_bulk = 2
num_events = 2
num_alpha = 0.56

# single.
s = np.array(['F2'])
t = np.array(['UE3'])


def main():
    #########################################################################################################################
    path_config = r''
    if path_config != '':
        config = u.get_data(path_config)
        load_config(config)
    #########################################################################################################################
    start_time = time.time()
    dataset = u.get_data(path_dataset)
    load_dataset(dataset)
    print(CYAN, "READ FILE TIME --- %s seconds ---" % (time.time() - start_time), RESET)

    start_time = time.time()
    global data
    data = make_data()
    calc_vars()
    print(CYAN, "LOADING DATA TIME --- %s seconds ---" % (time.time() - start_time), RESET)

    start_time = time.time()
    discrete_events(type, source=s, sink=t, avg_qtd_bulk=avg_qtd_bulk, num_events=num_events,
                    num_alpha=num_alpha)
    print(CYAN, "FULL TIME --- %s seconds ---" % (time.time() - start_time), RESET)

    if plot_graph:
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
    #handler.update_data()
    #allocated_request(pd, path, source, sink)
    if show_all_paths:
        pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    # pd.plot()
    data.clear_requests()


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
            allocated_request(pd, path, event)

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
        # for req in range(qtd_req):
        #   source = sources[req]
        #   sink = sinks[req]

        # source = [source]
        # sink = [sink]

        #for s,t in zip(sources,sinks):
        #if is_unique(pd, s, t):
        path = create_model(sources, sinks, event)
        handler.path = path

        if path is not None:
            start_time = time.time()
            handler.update_data()
            print(CYAN, "UPDATE TIME --- %s seconds ---" % (time.time() - start_time), RESET)
            allocated_request(pd, path, sources, sinks, event, 1)
        # update_model(pd, handler, sources, sinks)
        init = qtd_req

    # data.clear_requests()

    #if show_all_paths:
     #   pd.show_paths()
    if save_data:
        pd.save_data(path_output)
    if plot_data:
        pd.plot()


def is_unique(pd, source, sink):
    for i, row in pd.set_path.iterrows():
        if source == row['Source'] and sink == row['Sink']:
            return False
    return True


def update_model(pd, handler, last_source, last_sink):
    for i, row in pd.set_path.iterrows():
        if last_source == row['Source'] and last_sink == row['Sink']:
            pass
        else:
            path = create_model(row['Source'], row['Sink'], True)
            handler.path = path
            if path != row['Path']:  # verificar se essa condição é adequada, como usar o diff?
                print("SHIFT.")
                handler.old_path = row['Path']
                handler.update_data(True)
                reallocated_request(pd, path, i)
            else:
                print("NON-SHIFT.")


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

    for event in range(num_events):
        sources = r.Request.generate_sources_random(qtd_bulk, num_events)
        sinks = r.Request.generate_sinks_random(qtd_bulk, num_events)
        for req in tqdm.tqdm(range(qtd_bulk)):
            source = np.array(sources[req])
            sink = np.array(sinks[req])
            path = create_model(source, sink)
            handler.path = path
            handler.update_data()
            allocated_request(pd, path, event)

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
    plt.hist(distribution, bins=np.arange(1, num_files + 1), density=True)
    # plt.hist(distribution[distribution < 10], 10, density=True)
    # x = np.arange(1., 10.)
    # y = x ** (-alpha) / special.zetac(alpha)
    # plt.yscale('log')
    plt.title('Zipf')
    plt.xlabel('rank')
    plt.ylabel('frequency')
    # plt.plot(x, y / max(y), linewidth=2, color='r')
    plt.show()


def make_data():
    return Data(mobility, mobility_rate, alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs,
                key_index_ue, e_bs_adj,
                resources_file, size_file, phi,
                throughput_min_file, resources_node, rtt_min, radius_mbs, radius_sbs,
                gama, distance_ue, distance_bs
                )


def create_model(source, sink, event=1, reoptimize=False):
    if show_par:
        show_parameters()
    if show_var:
        show_vars()
    return run_model(source, sink, reoptimize, event)


def run_model(source, sink, reoptimize, event):
    start_time = time.time()
    od = OptimizeData(data=data, sources=source, sinks=sink)
    od.model = gp.Model("Orchestrator")
    od.create_vars()
    # od.set_function_objective()
    # od.set_function_objective1()
    od.set_function_objective2()
    # od.create_constraints()
    od.create_constraints2()
    od.execute(show_log)
    if show_results:
        print(GREEN, "\nContent:", source, " to User:", sink)
        od.result()
    if reoptimize:
        print(CYAN, "REOPTIMIZE TIME --- %s seconds ---" % (time.time() - start_time), RESET)
    else:
        print(RED, "EVENTO: ", event, RESET)
        print(CYAN, "\nOPTIMIZE TIME --- %s seconds ---" % (time.time() - start_time), RESET)
    if od.model.status == gp.GRB.OPTIMAL:
        path = od.solution_path(show_path)
    else:
        path = None
    return path


def reallocated_request(pd, path, req):
    pd.update_path(path, req)


def allocated_request(pd, path, source, sink, req=1, event=1):
    pd.insert_path(path, source, sink, event, req)


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
    color_dict = {"F": "#4682B4", "M": "#3CB371", "S": "#F0E68C", "U": "#A52A2A"}

    g = ig.Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue + key_index_file
    for i, name in enumerate(key_nodes):
        g.add_vertices(name)

    for i, name_orig in enumerate(key_nodes):
        for j, name_dest in enumerate(key_nodes):
            if data.weight_dict is not None:
                if data.weight_file_edge[0][i][j] < NO_EDGE:
                    g.add_edge(name_orig, name_dest)

    g.vs["color"] = [color_dict[node[0:1]] for node in g.vs["name"]]
    ig.plot(g, vertex_label=key_nodes, target=path_graph, edge_color="#808080", vertex_size=10, edge_arrow_size=0.7,
            bbox=(1000, 1000), )


def load_dataset(dataset: object):
    global mobility_rate, alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, e_bs_adj, resources_file, size_file, phi, throughput_min_file, resources_node, rtt_min, gama, distance_ue, distance_bs, radius_mbs, radius_sbs, avg_rtt, sd_rtt

    mobility_rate = dataset["mobility_rate"]

    alpha = dataset['alpha']
    beta = dataset["beta"]

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    e_bs_adj = dataset["e_bs_adj"]

    resources_file = dataset["resources_file"]
    size_file = dataset["size_file"]

    if num_bs is not None and num_files is not None:
        phi = [[0 for i in range(num_bs)] for f in range(num_files)]
        phi = dataset["phi"]

    throughput_min_file = dataset["throughput_min_file"]

    resources_node = dataset["resources_node"]

    rtt_min = dataset["rtt_min"]

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


def load_config(config: object):
    show_log = config["show_log"]
    show_results = config["show_results"]
    show_path = config["show_path"]
    show_var = config["show_var"]
    show_par = config["show_par"]
    plot_distribution = config["plot_distribution"]
    plot_data = config["plot_data"]
    show_all_paths = config["show_all_paths"]
    type = config["type"]
    mobility = config["mobility"]
    path_dataset = config["path_dataset"]
    save_data = config["save_data"]
    path_output = config["path_output"]
    plot_graph = config["plot_graph"]
    path_graph = config["path_graph"]

    # random and distribution.
    avg_qtd_bulk = config["avg_qtd_bulk"]
    num_events = config["num_events"]
    num_alpha = config["num_alpha"]

    # single.
    source = config["source"]
    sink = config["sink"]


if __name__ == "__main__":
    main()
