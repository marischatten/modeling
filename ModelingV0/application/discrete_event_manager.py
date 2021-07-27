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
import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

# import ortools.linear_solver.pywraplp as otlp
# from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
# from ortools.graph import pywrapgraph

import igraph as ig
import utils.utils as u
import simulation.request as rr
from optimization.optimize import *

lst_time = list()

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
show_results = False
show_path = False
show_var = False
show_par = False
plot_distribution = False
plot_data = False
type = Type.ZIPF
mobility = Mobility.IS_MOBILE
show_reallocation = False

path_dataset = ''

save_data = False
path_output = ''
plot_graph = False
plot_graph_mobility = False
path_graph = ''
enable_ceil_nodes_capacity = False
path_time = ''
# random and distribution.
avg_qtd_bulk = 2
num_events = 2
num_alpha = 0.56

# single.
s_single = np.array(['F1'])
t_single = np.array(['UE3'])


def application():
    if os.name == 'nt':
        path_config = r'..\config\config_model.json'
    else:
        path_config = r'../config/config_model.json'

    if path_config != '':
        config = u.get_data(path_config)
        load_config(config)

    start_time_1 = time.time()
    dataset = u.get_data(path_dataset)
    load_dataset(dataset)
    print(CYAN, "READ INSTANCE FILE TIME --- %s seconds ---" % round((time.time() - start_time_1), 4), RESET)

    start_time_2 = time.time()
    global data
    data = make_data()
    calc_vars()
    print(CYAN, "LOADING DATA TIME --- %s seconds ---" % round((time.time() - start_time_2), 4), RESET)

    start_time_3 = time.time()
    discrete_events()
    full_time = time.time() - start_time_3
    lst_time.append(full_time)
    print(CYAN, "FULL TIME --- %s seconds ---" % round(full_time, 4), RESET)

    if plot_graph:
        data.set_graph_adj_matrix()
        picture(path_graph)

    write_optimization_time()
    # min_cost_flow = pywrapgraph.SimpleMinCostFlow()
    # pywraplp.Solver('test', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)


def discrete_events():
    if type == Type.SINGLE:
        single()
    if type == Type.ZIPF:
        bulk_poisson_req_zipf()


def single():
    pd = PlotData(data)
    handler = HandleData(data)
    insert_reqs(s_single, t_single)
    path = create_model(s_single, t_single)
    handler.paths = path
    # handler.update_data()
    # allocated_request(pd, path, source, sink)
    if save_data:
        pd.save_data(path_output)
    # pd.plot()
    # data.clear_requests()


def bulk_poisson_req_zipf():
    pd = PlotData(data)
    handler = HandleData(data)
    paths = None
    hosts = None
    admission = 0
    init = 0
    all_sources, all_sinks, bulks = create_requests()
    for event in tqdm.tqdm(range(num_events)):  # EVENTS IN TIMELINE
        qtd_req = bulks[event]
        sources, sinks = get_req(all_sources.copy(), all_sinks.copy(), init, qtd_req)
        insert_reqs(sources, sinks)

        for req in range(qtd_req):
            data.clear_hops()
            data.clear_hops_with_id()

            source = sources[req]
            sink = sinks[req]

            source = [source]
            sink = [sink]

            paths, hosts = create_model(source, sink, event)
            handler.paths = paths
            handler.hosts = hosts
            if paths is not None:
                handler.reallocation(show_reallocation, event+1)
            else:
                drop_reqs(source, sink)
                data.drop_requests()
            if (paths is not None) and save_data:
                admission = len(paths)
                process_datas(pd, paths, hosts, event + 1)

        if event != (num_events-1):
            start_time_4 = time.time()
            handler.update_data()
            print(CYAN, "UPDATE DATA TIME --- %s seconds ---" % round((time.time() - start_time_4), 4), RESET)

        if plot_graph_mobility:
            data.set_graph_adj_matrix()
            picture(path_graph+"_{0}".format(event+1))
        init = qtd_req
    pd.calc_rate_admission_requests(admission, sum(bulks))

    if save_data:
        start_time_save = time.time()
        pd.save_data(path_output)
        print(CYAN, "SAVE DATA TIME --- %s seconds ---" % round((time.time() - start_time_save), 4), RESET)
    if plot_data:
        pass


def create_requests():
    sources = list()
    sinks = list()
    init = 0
    bulks = rr.Request.generate_bulk_poisson(avg_qtd_bulk, num_events)
    zipf = rr.Request.generate_sources_zip(num_alpha, sum(bulks), key_index_file)
    bulks = remove_bulk_empty(bulks.copy())
    for r in range(sum(bulks)):
        s = zipf[init]
        t = rr.Request.generate_sink_random(key_index_ue)
        if (len(sources) != 0) and (len(sinks) != 0):
            for i in range(len(sources)):
                while (sources[i] == s) and (sinks[i] == t):
                    print("Removed Replicated Request.")
                    t = rr.Request.generate_sink_random(key_index_ue)
            sources.append(s)
            sinks.append(t)
        else:
            sources.append(s)
            sinks.append(t)
        init += 1
    if plot_distribution:
        plot_poisson(bulks)
        plot_zipf(zipf)
    return (sources, sinks, bulks)


def process_datas(pd, paths, hosts, event):
    start_time_process = time.time()
    pd.insert_req(paths, hosts, event)
    pd.calc_server_use(paths, event)
    pd.calc_scattering(event)  # Get a lasts hops of event for scattering. Because a request can change the path.
    pd.calc_load_link(event)
    pd.calc_reallocation()
    print(CYAN, "PROCESS DATA TIME --- %s seconds ---" % round((time.time() - start_time_process), 4), RESET)


def remove_bulk_empty(bulks):
    for b in range(len(bulks)):
        if bulks[b] == 0:
            bulks[b] = 1
    return bulks


def insert_reqs(sources, sinks):
    global data
    for t, s in zip(sinks, sources):
        data.req_dict[t, s] = 1


def drop_reqs(source, sink):
    global data
    data.req_dict[sink[0],source[0]] = 0


def get_req(sources, sinks, qtd_previous, qtd):
    if qtd_previous == 0:
        return sources[:qtd], sinks[:qtd],
    else:
        return sources[qtd_previous:qtd_previous + qtd], sinks[qtd_previous:qtd_previous + qtd]


def plot_poisson(distribution):
    sns.displot(distribution)
    plt.xlim([0, 25])
    plt.xlabel('k')
    plt.ylabel('P(X=k)')
    plt.show()


def plot_zipf(distribution):
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
                size_file,
                throughput_min_file, resources_file, resources_node, rtt_min, radius_mbs, radius_sbs,
                gama, distance_ue, distance_bs
                )


def create_model(source, sink, event=0):
    if show_par:
        show_parameters()
    if show_var:
        show_vars()
    return run_model(source, sink, event)


def run_model(source, sink, event):
    global lst_time
    start_time_5 = time.time()
    od = OptimizeData(data=data, sources=source, sinks=sink)
    od.model = gp.Model("Orchestrator")
    od.run_model(show_log, enable_ceil_nodes_capacity)
    end_time_5 = time.time()
    paths = None
    hosts = None

    if show_results:
        print(RED, "##########################################", RESET)
        print(GREEN, "Content:", source, " to User:", sink)
        od.result()

    print(RED, "EVENT: ", event + 1, RESET)
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
    id.show_vars_matrix()
    # id.show_vars_dict()


def picture(path):
    path_with_ext = path + ".png"
    color_dict = {"F": "#4682B4", "M": "#3CB371", "S": "#F0E68C", "U": "#A52A2A"}

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
    global mobility_rate, alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, e_bs_adj, resources_file, size_file, throughput_min_file, resources_node, rtt_min, gama, distance_ue, distance_bs, radius_mbs, radius_sbs

    mobility_rate = dataset["mobility_rate"]
    alpha = dataset['alpha']
    beta = dataset['beta']

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_files = int(dataset["num_files"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    e_bs_adj = dataset["e_bs_adj"]

    size_file = dataset["size_file"]
    throughput_min_file = dataset["throughput_min_file"]
    resources_file = dataset["resources_file"]

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


def load_type_enum(t):
    global type
    if str(t).upper() == str('SINGLE'):
        type = type.SINGLE
    if str(t).upper() == 'ZIPF':
        type = type.ZIPF


def load_is_mobile_enum(mob):
    global mobility
    if mob.upper() == 'IS_MOBILE':
        mobility = mobility.IS_MOBILE
    if mob.upper() == 'NON_MOBILE':
        mobility = mobility.NON_MOBILE


def load_config(config: object):
    global show_log, show_results, show_path, show_var, show_par, plot_distribution, plot_data, show_reallocation, path_dataset, save_data, path_output, plot_graph, plot_graph_mobility, path_graph, enable_ceil_nodes_capacity, path_time, avg_qtd_bulk, num_events, num_alpha, s_single, t_single
    show_log = config["show_log"]
    show_results = config["show_results"]
    show_path = config["show_path"]
    show_var = config["show_var"]

    show_par = config["show_par"]
    plot_distribution = config["plot_distribution"]
    plot_data = config["plot_data"]
    load_type_enum(config["type"])
    load_is_mobile_enum(config["mobility"])
    path_dataset = config["path_dataset"]
    save_data = config["save_data"]
    path_output = config["path_output"]
    plot_graph = config["plot_graph"]
    plot_graph_mobility = config["plot_graph_mobility"]
    path_graph = config["path_graph"]
    show_reallocation = config["show_reallocation"]
    enable_ceil_nodes_capacity = config["enable_ceil_nodes_capacity"]
    path_time = config["path_time"]
    # random and distribution.
    avg_qtd_bulk = config["avg_qtd_bulk"]
    num_events = config["num_events"]
    num_alpha = config["num_alpha"]
    # single.
    s_single = config["source"]
    t_single = config["sink"]

    if os.name != 'nt':
        path_dataset = path_dataset.replace('\\', '/')
        path_output = path_output.replace('\\', '/')
        path_graph = path_graph.replace('\\', '/')
        path_time = path_graph.replace('\\', '/')

    print(CYAN, "LOADED CONFIGURATION.", RESET)


def write_optimization_time():
    with open(path_time, 'w') as f:
        for i in lst_time:
            f.write("%s\n" % i)


if __name__ == "__main__":
    application()
