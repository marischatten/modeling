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

import os
import warnings

import tqdm

# import ortools.linear_solver.pywraplp as otlp
# from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
# from ortools.graph import pywrapgraph

import igraph as ig
from utils.utils import *
import simulation.request as r
from optimization.optimize import *

lst_time = list()
max_events = 0
mobility_rate = 10
location_fixed = False
path_location = ''
locations = None

alpha = 0
beta = 0
num_bs = 0
num_ue = 0
num_files = 0
num_mbs = 0
num_sbs = 0

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

e_bs_adj = list()

size_file = list()
buffer_file = list()
throughput_min_file = list()

resources_node = list()

rtt_edge = list()
rtt_min_cloud_mbs = 0
rtt_min_mbs_mbs = 0
rtt_min_sbs_mbs = 0
rtt_min_sbs_ue = 0
rtt_min_cloud_ue = 0

distance_ue = list()
distance_bs = list

gama = list()
radius_mbs = 0
radius_sbs = 0

data = None
key =None

show_log = 0
show_results = False
show_path = False
show_var = False
show_par = False
plot_distribution = False
type = Type.ZIPF
approach = Approach.NETWORK_AWARE
mobility = False
show_reallocation = False
requests_fixed = True
path_requests = ''
path_dataset = ''

save_data = False
path_output = ''
plot_graph = False
plot_graph_mobility = False
path_graph = ''
enable_ceil_nodes_capacity = False
deallocate_request = False
path_time = ''
# random and distribution.
fixed = False
avg_qtd_bulk = 2
num_events = 2
num_alpha = 0.56
bandwidth_maximum = 0

# single.
s_single = np.array(['F1'])
t_single = np.array(['UE3'])


def application():
    if os.name == 'nt':
        path_config = r'..\config\config_model.json'
    else:
        path_config = r'../config/config_model.json'

    if path_config != '':
        config = get_data(path_config)
        load_config(config)

    start_time_1 = time.time()
    dataset = get_data(path_dataset)
    load_dataset(dataset)
    print(CYAN, "READ INSTANCE FILE TIME --- %s seconds ---" % round((time.time() - start_time_1), 4), RESET)

    start_time_2 = time.time()
    global data
    if location_fixed:
        load_location_fixed()
    data = make_data()
    calc_vars()
    print(CYAN, "LOADING DATA TIME --- %s seconds ---" % round((time.time() - start_time_2), 4), RESET)

    if plot_graph:
        data.set_graph_adj_matrix()
        picture(path_graph)

    start_time_3 = time.time()
    discrete_events()
    full_time = time.time() - start_time_3
    lst_time.append(full_time)
    print(CYAN, "FULL TIME --- %s seconds ---" % round(full_time, 4), RESET)

    write_optimization_time()
    # min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # pywraplp.Solver('test', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)


def discrete_events():
    if type == Type.SINGLE:
        single()
    if type == Type.ZIPF:
        poisson_zipf()


def single():
    pd = PlotData(data)
    handler = HandleData(data)
    path = create_model(s_single, t_single)
    handler.paths = path
    if save_data:
        pd.save_data(path_output)


def poisson_zipf():
    pd = PlotData(data)
    handler = HandleData(data)
    paths = None
    hosts = None
    admission = 0
    init = 0
    req_total = 0
    lst_time.append('times')

    if requests_fixed:
        dataset = get_data(path_requests)
        requests, bulks = load_requests(dataset)
    else:
        requests, bulks = r.Request.create_requests(avg_qtd_bulk, num_events, num_alpha, key_index_file, key_index_ue, num_files, plot_distribution, fixed)

    data.create_exponential_scale_rtt(sum(bulks))

    for event in tqdm.tqdm(range(num_events)):  # EVENTS IN TIMELINE

        if plot_graph_mobility:
            data.set_graph_adj_matrix()
            picture(path_graph+"_{0}".format(event+1))

        pd.rtt_to_dataframe(event+1)

        qtd_req = bulks[event]
        for req in range(qtd_req):
            req_total += 1
            data.clear_hops()
            data.clear_hops_with_id()

            source = [requests[init][0]]
            sink = [requests[init][1]]

            paths, hosts = create_model(source, sink, event)

            if paths is not None:
                handler.paths = paths
                handler.hosts = hosts
                handler.reallocation(show_reallocation, event + 1)
                pd.set_request(paths.copy(), hosts.copy())

                handler.insert_counter_requests(source, sink, key)
                admission += 1
            else:
                data.drop_requests(source, sink, key)
            init += 1

            pd.set_hops(data.hops.copy(), data.hops_with_id.copy())

        process_datas(pd, event + 1)

        if deallocate_request:
            handler.update_counter()
        if event != (num_events-1):
            start_time_4 = time.time()
            handler.update_data(event,location_fixed)
            print(CYAN, "UPDATE DATA TIME --- %s seconds ---" % round((time.time() - start_time_4), 4), RESET)

    if save_data:
        pd.calc_rate_admission_requests(admission, req_total)
        pd.set_distribution(bulks, requests)
        start_time_save = time.time()
        pd.save_data(path_output)
        print(CYAN, "SAVE DATA TIME --- %s seconds ---" % round((time.time() - start_time_save), 4), RESET)


def process_datas(pd, event):
    event_null = True
    start_time_process = time.time()
    if ((len(pd.set_paths) != 0) or (len(pd.set_hosts) != 0)) and save_data:
        event_null = False
        for r, h in zip(pd.set_paths, pd.set_hosts):
            pd.insert_req(r, h, event)
        last_req = pd.set_paths[len(pd.set_paths)-1]
        last_host = pd.set_hosts[len(pd.set_hosts)-1]
        pd.calc_server_use(event,event_null,last_req,last_host)
        pd.calc_delay_by_request(event, event_null,last_req)
        pd.calc_cache_vs_cloud(event,event_null,last_host)
    else:
        pd.calc_server_use(event, event_null)
        pd.calc_delay_by_request(event, event_null)
        pd.calc_cache_vs_cloud(event, event_null)

    pd.calc_server_use_by_type(event,event_null)
    pd.calc_scattering(event, event_null)
    pd.calc_load_link(event, event_null)
    pd.calc_reallocation(event, event_null)
    pd.set_paths.clear()
    pd.set_hosts.clear()
    print(CYAN, "PROCESS DATA TIME --- %s seconds ---" % round((time.time() - start_time_process), 4), RESET)


def load_location_fixed():
    global locations
    dataset = get_data(path_location)
    locations = dataset["locations"]


def make_data():
    return Data(mobility, mobility_rate, alpha, beta, num_bs, num_ue, num_files, num_mbs,num_sbs, key_index_file, key_index_bs,
                key_index_ue, e_bs_adj,
                size_file,buffer_file,
                throughput_min_file, resources_node, rtt_edge, radius_mbs, radius_sbs,
                gama, distance_ue, distance_bs, max_events, locations, rtt_min_cloud_mbs, rtt_min_mbs_mbs, rtt_min_sbs_mbs,  rtt_min_sbs_ue, rtt_min_cloud_ue, approach, bandwidth_maximum
                )


def create_model(source, sink, event=0):
    if show_par:
        show_parameters()
    if show_var:
        show_vars()
    return run_model(source, sink, event)


def run_model(source, sink, event):
    global lst_time, key
    start_time_5 = time.time()
    od = OptimizeData(data=data, sources=source, sinks=sink)
    od.model = gp.Model("Orchestrator")

    if approach == approach.NETWORK_AWARE:
        key = od.run_model_network_aware(show_log, enable_ceil_nodes_capacity)
    if approach == approach.NO_COOPERATION:
        key = od.run_model_no_cooperation(show_log, enable_ceil_nodes_capacity)
    if approach == approach.ONE_HOP:
        key = od.run_model_one_hop(show_log, enable_ceil_nodes_capacity)
    if approach == approach.MULTI_HOP:
        key = od.run_model_multi_hop(show_log, enable_ceil_nodes_capacity)
    if approach == approach.BANDWIDTH_MAX:
        key = od.run_model_bandwidth_max(show_log, enable_ceil_nodes_capacity)

    end_time_5 = time.time()
    paths = None
    hosts = None

    if show_results:
        print(RED, "##########################################", RESET)
    print(RED, "EVENT: ", event + 1, RESET)
    if show_results:
        print(GREEN, "Content:", source, " to User:", sink)
        od.result()
    time_optimize = round((end_time_5 - start_time_5), 4)
    lst_time.append(time_optimize)
    print(CYAN, "OPTIMIZE TIME --- %s seconds ---" % time_optimize, RESET)

    if od.model.status == gp.GRB.OPTIMAL:
        start_time_make_path = time.time()
        paths, hosts = od.solutions(show_path)
        print(CYAN, "MAKE PATHS TIME --- %s seconds ---" % round(time.time() - start_time_make_path, 4), RESET)
    return (paths, hosts)


def calc_vars():
    hd = HandleData(data)
    hd.calc_vars()


def show_parameters():
    ld = LogData(data)
    ld.show_parameters()


def show_vars():
    id = LogData(data)
    id.show_vars_dict()
    id.show_vars_matrix()


def picture(path):
    path_with_ext = path + ".png"

    color_dict = {"F": "#4682B4", "M": "#3CB371", "S": "#F0E68C", "U": "#A52A2A"}
    color_dict_cloud = {"MBS0": "#4B0082"}
    g = ig.Graph(directed=1)
    g.is_weighted()
    key_nodes = key_index_bs + key_index_ue + key_index_file
    for i, name in enumerate(key_nodes):
        g.add_vertices(name)

    for i, name_orig in enumerate(key_nodes):
        for j, name_dest in enumerate(key_nodes):
            if data.graph_adj_matrix[i][j] != NO_EDGE:
                g.add_edge(name_orig, name_dest)

    g.vs["color"] = [color_dict[node[0:1]] for node in g.vs["name"]]
    ig.plot(g, vertex_label=key_nodes, target=path_with_ext, edge_color="#808080", vertex_size=10, edge_arrow_size=0.7,
            bbox=(1000, 1000), )



def load_dataset(dataset: object):
    global mobility_rate, alpha, beta, num_bs, num_ue, num_files, num_mbs, num_sbs, key_index_file, key_index_bs, key_index_ue, e_bs_adj, size_file, buffer_file, throughput_min_file, resources_node, rtt_edge, gama, distance_ue, distance_bs, radius_mbs, radius_sbs, rtt_min_cloud_mbs, rtt_min_mbs_mbs, rtt_min_sbs_mbs, rtt_min_sbs_ue, rtt_min_cloud_ue

    mobility_rate = dataset["mobility_rate"]
    alpha = dataset['alpha']
    beta = dataset['beta']

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])
    num_mbs = int(dataset["num_mbs"])
    num_sbs = int(dataset["num_sbs"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    e_bs_adj = dataset["e_bs_adj"]

    size_file = dataset["size_file"]
    buffer_file = dataset["buffer_file"]
    throughput_min_file = dataset["throughput_min_file"]

    resources_node = dataset["resources_node"]

    rtt_edge = dataset["rtt_edge"]
    rtt_min_cloud_mbs = dataset["rtt_min_cloud_mbs"]
    rtt_min_mbs_mbs =  dataset["rtt_min_mbs_mbs"]
    rtt_min_sbs_mbs = dataset["rtt_min_sbs_mbs"]
    rtt_min_sbs_ue = dataset["rtt_min_sbs_ue"]
    rtt_min_cloud_ue = dataset["rtt_min_cloud_ue"]

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


def load_type_enum(t):
    global type
    if str(t).upper() == str('SINGLE'):
        type = type.SINGLE
    if str(t).upper() == 'ZIPF':
        type = type.ZIPF


def load_approach_enum(a):
    global approach
    if str(a).upper() == str('NETWORK_AWARE'):
        approach = approach.NETWORK_AWARE
    if str(a).upper() == str('NO_COOPERATION'):
        approach = approach.NO_COOPERATION
    if str(a).upper() == str('ONE_HOP'):
        approach = approach.ONE_HOP
    if str(a).upper() == str('MULTI_HOP'):
        approach = approach.MULTI_HOP
    if str(a).upper() == str('BANDWIDTH_MAX'):
        approach = approach.BANDWIDTH_MAX


def load_config(config: object):
    global show_log, show_results, show_path, show_var, show_par, plot_distribution, show_reallocation, mobility, path_dataset, save_data, path_output, plot_graph, plot_graph_mobility, path_graph, enable_ceil_nodes_capacity, path_time, requests_fixed, path_requests, fixed, avg_qtd_bulk, num_events, num_alpha, s_single, t_single, max_events, location_fixed, path_location, deallocate_request, bandwidth_maximum
    show_log = config["show_log"]
    show_results = config["show_results"]
    show_path = config["show_path"]
    show_var = config["show_var"]

    show_par = config["show_par"]
    plot_distribution = config["plot_distribution"]
    load_type_enum(config["type"])
    load_approach_enum(config["approach"])
    mobility = config["mobility"]
    location_fixed = config["location_fixed"]
    path_location = config["path_location"]
    path_dataset = config["path_dataset"]
    save_data = config["save_data"]
    path_output = config["path_output"]
    plot_graph = config["plot_graph"]
    plot_graph_mobility = config["plot_graph_mobility"]
    path_graph = config["path_graph"]
    show_reallocation = config["show_reallocation"]
    enable_ceil_nodes_capacity = config["enable_ceil_nodes_capacity"]
    path_time = config["path_time"]
    requests_fixed = config["requests_fixed"]
    path_requests = config["path_requests"]
    deallocate_request = config["deallocate_request"]
    # random and distribution.
    fixed = config["fixed"]
    avg_qtd_bulk = config["avg_qtd_bulk"]
    num_events = config["num_events"]
    num_alpha = config["num_alpha"]
    max_events = config["max_events"]
    bandwidth_maximum = config["bandwidth_maximum"]

    # single.
    s_single = config["source"]
    t_single = config["sink"]

    if os.name != 'nt':
        path_dataset = path_dataset.replace('\\', '/')
        path_output = path_output.replace('\\', '/')
        path_graph = path_graph.replace('\\', '/')
        path_time = path_time.replace('\\', '/')
        path_requests = path_requests.replace('\\', '/')
        path_location = path_location.replace('\\', '/')

    print(CYAN, "LOADED CONFIGURATION.", RESET)


def load_requests(dataset):
    return (dataset["requests"], dataset["bulks"])


def write_optimization_time():
    with open(path_time, 'w') as f:
        for i in lst_time:
            f.write("%s\n" % i)


if __name__ == "__main__":
    application()
