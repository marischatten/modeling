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
key =None

show_log = 0
show_results = False
show_path = False
show_var = False
show_par = False
plot_distribution = False
type = Type.ZIPF
mobility = Mobility.IS_MOBILE
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

    if requests_fixed:
        #dataset = get_data(path_requests)
        #requests, bulks = load_requests(dataset)
        requests = [['F11', 'UE136'], ['F100', 'UE88'], ['F19', 'UE124'], ['F89', 'UE63'], ['F40', 'UE144'], ['F97', 'UE86'], ['F27', 'UE56'], ['F28', 'UE160'], ['F1', 'UE168'], ['F37', 'UE27'], ['F93', 'UE136'], ['F26', 'UE124'], ['F98', 'UE50'], ['F34', 'UE153'], ['F96', 'UE168'], ['F2', 'UE9'], ['F13', 'UE180'], ['F2', 'UE2'], ['F24', 'UE130'], ['F5', 'UE25'], ['F15', 'UE127'], ['F21', 'UE16'], ['F100', 'UE22'], ['F44', 'UE131'], ['F3', 'UE177'], ['F63', 'UE164'], ['F28', 'UE11'], ['F33', 'UE161'], ['F1', 'UE13'], ['F2', 'UE100'], ['F35', 'UE147'], ['F79', 'UE8'], ['F43', 'UE29'], ['F2', 'UE173'], ['F9', 'UE178'], ['F97', 'UE44'], ['F24', 'UE49'], ['F41', 'UE187'], ['F59', 'UE114'], ['F13', 'UE37'], ['F15', 'UE59'], ['F28', 'UE69'], ['F62', 'UE118'], ['F90', 'UE159'], ['F9', 'UE11'], ['F63', 'UE10'], ['F1', 'UE50'], ['F100', 'UE166'], ['F23', 'UE143'], ['F99', 'UE111'], ['F89', 'UE42'], ['F3', 'UE103'], ['F66', 'UE147'], ['F12', 'UE98'], ['F6', 'UE53'], ['F55', 'UE134'], ['F54', 'UE143'], ['F44', 'UE194'], ['F29', 'UE143'], ['F14', 'UE71'], ['F72', 'UE118'], ['F89', 'UE197'], ['F1', 'UE58'], ['F2', 'UE193'], ['F95', 'UE108'], ['F41', 'UE194'], ['F4', 'UE184'], ['F5', 'UE188'], ['F49', 'UE54'], ['F24', 'UE110'], ['F78', 'UE47'], ['F1', 'UE44'], ['F18', 'UE152'], ['F26', 'UE18'], ['F16', 'UE114'], ['F39', 'UE100'], ['F33', 'UE12'], ['F12', 'UE137'], ['F1', 'UE120'], ['F11', 'UE20'], ['F24', 'UE190'], ['F44', 'UE160'], ['F31', 'UE73'], ['F1', 'UE28'], ['F82', 'UE19'], ['F7', 'UE155'], ['F82', 'UE119'], ['F5', 'UE14'], ['F94', 'UE170'], ['F49', 'UE60'], ['F11', 'UE19'], ['F14', 'UE183'], ['F58', 'UE138'], ['F52', 'UE58'], ['F81', 'UE167'], ['F67', 'UE36'], ['F19', 'UE173'], ['F20', 'UE20'], ['F51', 'UE124'], ['F11', 'UE23'], ['F31', 'UE22'], ['F46', 'UE47'], ['F34', 'UE13'], ['F87', 'UE68'], ['F45', 'UE189'], ['F78', 'UE154'], ['F21', 'UE102'], ['F92', 'UE1'], ['F2', 'UE149'], ['F57', 'UE20'], ['F55', 'UE1'], ['F51', 'UE2'], ['F7', 'UE56'], ['F62', 'UE23'], ['F28', 'UE182'], ['F24', 'UE195'], ['F13', 'UE69'], ['F93', 'UE127'], ['F76', 'UE109'], ['F94', 'UE25'], ['F100', 'UE192'], ['F8', 'UE130'], ['F49', 'UE191'], ['F64', 'UE9'], ['F23', 'UE160'], ['F98', 'UE43'], ['F47', 'UE1'], ['F4', 'UE52'], ['F17', 'UE163'], ['F64', 'UE129'], ['F37', 'UE154'], ['F34', 'UE173'], ['F14', 'UE182'], ['F37', 'UE54'], ['F18', 'UE128'], ['F5', 'UE103'], ['F40', 'UE119'], ['F6', 'UE67'], ['F44', 'UE123'], ['F15', 'UE40'], ['F9', 'UE8'], ['F5', 'UE177'], ['F38', 'UE13'], ['F33', 'UE156'], ['F44', 'UE122'], ['F2', 'UE199'], ['F13', 'UE76'], ['F95', 'UE123'], ['F11', 'UE42'], ['F13', 'UE194'], ['F45', 'UE146'], ['F25', 'UE76'], ['F3', 'UE149'], ['F16', 'UE151'], ['F18', 'UE22'], ['F1', 'UE154'], ['F56', 'UE160'], ['F94', 'UE100'], ['F35', 'UE36'], ['F7', 'UE176'], ['F69', 'UE6'], ['F36', 'UE125'], ['F27', 'UE84'], ['F86', 'UE17'], ['F44', 'UE3'], ['F41', 'UE139'], ['F3', 'UE102'], ['F12', 'UE44'], ['F6', 'UE47'], ['F9', 'UE33'], ['F1', 'UE150'], ['F7', 'UE185'], ['F85', 'UE104'], ['F9', 'UE150'], ['F1', 'UE42'], ['F40', 'UE198'], ['F52', 'UE46'], ['F3', 'UE113'], ['F84', 'UE31'], ['F43', 'UE141'], ['F86', 'UE191'], ['F56', 'UE43'], ['F8', 'UE36'], ['F95', 'UE95'], ['F58', 'UE2'], ['F48', 'UE169'], ['F1', 'UE121'], ['F49', 'UE159'], ['F63', 'UE172'], ['F66', 'UE78'], ['F1', 'UE129'], ['F26', 'UE115'], ['F89', 'UE136'], ['F20', 'UE86'], ['F49', 'UE72'], ['F55', 'UE3'], ['F3', 'UE152'], ['F17', 'UE69'], ['F1', 'UE43'], ['F4', 'UE17'], ['F91', 'UE5'], ['F5', 'UE22'], ['F17', 'UE148'], ['F75', 'UE78'], ['F32', 'UE79'], ['F20', 'UE74'], ['F47', 'UE121'], ['F22', 'UE29'], ['F2', 'UE114'], ['F51', 'UE80'], ['F7', 'UE88'], ['F77', 'UE3'], ['F85', 'UE85'], ['F1', 'UE52'], ['F59', 'UE118'], ['F31', 'UE158'], ['F84', 'UE122'], ['F97', 'UE180'], ['F33', 'UE74'], ['F42', 'UE137'], ['F56', 'UE133'], ['F10', 'UE133'], ['F85', 'UE14'], ['F44', 'UE38'], ['F42', 'UE166'], ['F6', 'UE34'], ['F62', 'UE163'], ['F20', 'UE91'], ['F84', 'UE77'], ['F39', 'UE159'], ['F32', 'UE109'], ['F1', 'UE70'], ['F17', 'UE185'], ['F15', 'UE179'], ['F2', 'UE155'], ['F81', 'UE77'], ['F17', 'UE152'], ['F15', 'UE14'], ['F28', 'UE126'], ['F1', 'UE181'], ['F34', 'UE129'], ['F69', 'UE186'], ['F1', 'UE164'], ['F1', 'UE26'], ['F56', 'UE109'], ['F38', 'UE187'], ['F3', 'UE176'], ['F36', 'UE117'], ['F12', 'UE52'], ['F5', 'UE88'], ['F2', 'UE169'], ['F21', 'UE77'], ['F34', 'UE185'], ['F37', 'UE35'], ['F47', 'UE181'], ['F55', 'UE150'], ['F33', 'UE89'], ['F4', 'UE86'], ['F79', 'UE89'], ['F37', 'UE168'], ['F37', 'UE195'], ['F5', 'UE125'], ['F40', 'UE51'], ['F14', 'UE66'], ['F46', 'UE98'], ['F18', 'UE195'], ['F5', 'UE136'], ['F44', 'UE77'], ['F1', 'UE45'], ['F64', 'UE5'], ['F86', 'UE127'], ['F59', 'UE112'], ['F12', 'UE196'], ['F10', 'UE83'], ['F49', 'UE58'], ['F38', 'UE148'], ['F13', 'UE34'], ['F4', 'UE159'], ['F64', 'UE53'], ['F1', 'UE22'], ['F7', 'UE91'], ['F1', 'UE33'], ['F61', 'UE136'], ['F40', 'UE110'], ['F29', 'UE179'], ['F1', 'UE39'], ['F24', 'UE141'], ['F83', 'UE30'], ['F8', 'UE148'], ['F77', 'UE58'], ['F25', 'UE10'], ['F57', 'UE168'], ['F57', 'UE31'], ['F23', 'UE51'], ['F87', 'UE30'], ['F2', 'UE38'], ['F10', 'UE175'], ['F90', 'UE27'], ['F11', 'UE26'], ['F3', 'UE76'], ['F56', 'UE131'], ['F36', 'UE112'], ['F12', 'UE48'], ['F60', 'UE63'], ['F6', 'UE110'], ['F16', 'UE32'], ['F76', 'UE2'], ['F3', 'UE137'], ['F3', 'UE93'], ['F5', 'UE165'], ['F78', 'UE20'], ['F13', 'UE74'], ['F12', 'UE80'], ['F27', 'UE79'], ['F2', 'UE154'], ['F30', 'UE63'], ['F4', 'UE193'], ['F12', 'UE54'], ['F39', 'UE55'], ['F45', 'UE33'], ['F58', 'UE60'], ['F20', 'UE47'], ['F92', 'UE112'], ['F8', 'UE38'], ['F33', 'UE165'], ['F63', 'UE101'], ['F30', 'UE9'], ['F11', 'UE121'], ['F25', 'UE3'], ['F78', 'UE8'], ['F11', 'UE55'], ['F24', 'UE155'], ['F6', 'UE50'], ['F8', 'UE72'], ['F40', 'UE42'], ['F14', 'UE107'], ['F52', 'UE88'], ['F1', 'UE2'], ['F26', 'UE25'], ['F29', 'UE162'], ['F50', 'UE33'], ['F44', 'UE67'], ['F1', 'UE158'], ['F98', 'UE136'], ['F15', 'UE61'], ['F49', 'UE51'], ['F4', 'UE132'], ['F56', 'UE31'], ['F67', 'UE66'], ['F2', 'UE197'], ['F6', 'UE105'], ['F8', 'UE172'], ['F8', 'UE104'], ['F31', 'UE97'], ['F25', 'UE155'], ['F26', 'UE12'], ['F38', 'UE197'], ['F51', 'UE199'], ['F37', 'UE38'], ['F26', 'UE81'], ['F85', 'UE137'], ['F43', 'UE165'], ['F83', 'UE132'], ['F5', 'UE46'], ['F44', 'UE108'], ['F31', 'UE114'], ['F2', 'UE147'], ['F70', 'UE198'], ['F84', 'UE103'], ['F43', 'UE82'], ['F86', 'UE89'], ['F53', 'UE30'], ['F3', 'UE41'], ['F55', 'UE72'], ['F64', 'UE120'], ['F5', 'UE158'], ['F46', 'UE84'], ['F67', 'UE83'], ['F19', 'UE146'], ['F20', 'UE160'], ['F10', 'UE157'], ['F9', 'UE32'], ['F15', 'UE107'], ['F32', 'UE82'], ['F3', 'UE42'], ['F1', 'UE190'], ['F64', 'UE105'], ['F1', 'UE156'], ['F29', 'UE98'], ['F16', 'UE190'], ['F6', 'UE146'], ['F66', 'UE15'], ['F91', 'UE24'], ['F8', 'UE100'], ['F6', 'UE84'], ['F2', 'UE195'], ['F57', 'UE154'], ['F57', 'UE34'], ['F57', 'UE165'], ['F62', 'UE90'], ['F83', 'UE153'], ['F20', 'UE177'], ['F58', 'UE165'], ['F52', 'UE172'], ['F55', 'UE40'], ['F26', 'UE189'], ['F18', 'UE156'], ['F4', 'UE99'], ['F45', 'UE66'], ['F2', 'UE55'], ['F14', 'UE157'], ['F1', 'UE35'], ['F4', 'UE185'], ['F66', 'UE53'], ['F35', 'UE180'], ['F4', 'UE115'], ['F20', 'UE163'], ['F37', 'UE173'], ['F1', 'UE34'], ['F3', 'UE5'], ['F80', 'UE170'], ['F49', 'UE47'], ['F1', 'UE107'], ['F57', 'UE189'], ['F18', 'UE80'], ['F44', 'UE60'], ['F21', 'UE133'], ['F16', 'UE155'], ['F82', 'UE1'], ['F42', 'UE172'], ['F12', 'UE122'], ['F45', 'UE85'], ['F10', 'UE44'], ['F1', 'UE1'], ['F53', 'UE78'], ['F45', 'UE135'], ['F46', 'UE165'], ['F79', 'UE43'], ['F3', 'UE83'], ['F36', 'UE70'], ['F21', 'UE104'], ['F75', 'UE157'], ['F65', 'UE129'], ['F6', 'UE69'], ['F2', 'UE78'], ['F8', 'UE13'], ['F10', 'UE162'], ['F69', 'UE8'], ['F56', 'UE147'], ['F30', 'UE51'], ['F98', 'UE78'], ['F75', 'UE92'], ['F44', 'UE157'], ['F16', 'UE88'], ['F85', 'UE102'], ['F22', 'UE135'], ['F91', 'UE154'], ['F1', 'UE92'], ['F15', 'UE123'], ['F26', 'UE142'], ['F41', 'UE30'], ['F20', 'UE129'], ['F88', 'UE41'], ['F6', 'UE22'], ['F83', 'UE43'], ['F22', 'UE152'], ['F57', 'UE50'], ['F3', 'UE156'], ['F89', 'UE88'], ['F21', 'UE8'], ['F80', 'UE11'], ['F8', 'UE122'], ['F7', 'UE139'], ['F9', 'UE137'], ['F9', 'UE186'], ['F37', 'UE112'], ['F23', 'UE180'], ['F6', 'UE33'], ['F1', 'UE97'], ['F98', 'UE157'], ['F20', 'UE49'], ['F14', 'UE121'], ['F5', 'UE9'], ['F7', 'UE33'], ['F9', 'UE19'], ['F54', 'UE164'], ['F54', 'UE121'], ['F39', 'UE6'], ['F3', 'UE84'], ['F30', 'UE25'], ['F64', 'UE158'], ['F44', 'UE116'], ['F1', 'UE59'], ['F78', 'UE183'], ['F43', 'UE117'], ['F36', 'UE146'], ['F66', 'UE24'], ['F7', 'UE172'], ['F23', 'UE118'], ['F1', 'UE68'], ['F54', 'UE118'], ['F46', 'UE3'], ['F34', 'UE56'], ['F48', 'UE136'], ['F77', 'UE36'], ['F60', 'UE73'], ['F96', 'UE2'], ['F14', 'UE63'], ['F1', 'UE67']]
        bulks = [7, 7, 10, 5, 11, 5, 4, 6, 3, 6, 10, 8, 7, 4, 5, 3, 4, 5, 5, 1, 6, 4, 4, 4, 6, 7, 5, 5, 7, 8, 7, 4, 6, 6, 2, 7, 8, 3, 4, 8, 5, 7, 1, 5, 7, 3, 6, 3, 6, 6, 4, 7, 5, 7, 2, 7, 5, 5, 6, 7, 4, 2, 3, 5, 5, 2, 7, 2, 3, 5, 4, 4, 5, 5, 3, 2, 1, 6, 7, 4, 3, 4, 3, 9, 8, 1, 11, 3, 5, 6, 9, 4, 4, 2, 10, 1, 3, 1, 9, 3]
    else:
        requests, bulks = r.Request.create_requests(avg_qtd_bulk, num_events, num_alpha, key_index_file, key_index_ue, num_files, plot_distribution, fixed)

    for event in tqdm.tqdm(range(num_events)):  # EVENTS IN TIMELINE
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
                pd.set_hops(data.hops.copy(), data.hops_with_id.copy())
                handler.insert_counter_requests(source, sink, key)
                admission += 1
            else:
                data.drop_requests(source, sink, key)
            init += 1
        if deallocate_request:
            handler.update_counter()
        if event != (num_events-1):
            start_time_4 = time.time()
            handler.update_data(event,location_fixed)
            print(CYAN, "UPDATE DATA TIME --- %s seconds ---" % round((time.time() - start_time_4), 4), RESET)

        if plot_graph_mobility:
            data.set_graph_adj_matrix()
            picture(path_graph+"_{0}".format(event+1))

        process_datas(pd, event + 1)

    if save_data:
        pd.calc_rate_admission_requests(admission, req_total)
        pd.set_distribution(bulks, requests)
        start_time_save = time.time()
        pd.save_data(path_output)
        print(CYAN, "SAVE DATA TIME --- %s seconds ---" % round((time.time() - start_time_save), 4), RESET)


def process_datas(pd, event):
    event_null = True
    start_time_process = time.time()
    if ((len(pd.set_requests) != 0) or (len(pd.set_hosts) != 0)) and save_data:
        event_null = False
        for r, h in zip(pd.set_requests, pd.set_hosts):
            pd.insert_req(r, h, event)
        last_req = pd.set_requests[len(pd.set_requests)-1]
        last_host = pd.set_requests[len(pd.set_hosts)-1]
        pd.calc_server_use(event,event_null,last_req,last_host)
    else:
        pd.calc_server_use(event,event_null)

    pd.calc_scattering(event, event_null)
    pd.calc_load_link(event, event_null)
    pd.calc_reallocation(event, event_null)
    pd.set_requests.clear()
    pd.set_hosts.clear()
    print(CYAN, "PROCESS DATA TIME --- %s seconds ---" % round((time.time() - start_time_process), 4), RESET)


def load_location_fixed():
    global locations
    dataset = get_data(path_location)
    locations = dataset["locations"]


def make_data():
    return Data(mobility, mobility_rate, alpha, beta, num_bs, num_ue, num_files, key_index_file, key_index_bs,
                key_index_ue, e_bs_adj,
                size_file,
                throughput_min_file, resources_file, resources_node, rtt_min, radius_mbs, radius_sbs,
                gama, distance_ue, distance_bs, max_events, locations
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
    key = od.run_model(show_log, enable_ceil_nodes_capacity)
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
    global show_log, show_results, show_path, show_var, show_par, plot_distribution, show_reallocation, path_dataset, save_data, path_output, plot_graph, plot_graph_mobility, path_graph, enable_ceil_nodes_capacity, path_time, requests_fixed, path_requests, fixed, avg_qtd_bulk, num_events, num_alpha, s_single, t_single, max_events, location_fixed, path_location, deallocate_request
    show_log = config["show_log"]
    show_results = config["show_results"]
    show_path = config["show_path"]
    show_var = config["show_var"]

    show_par = config["show_par"]
    plot_distribution = config["plot_distribution"]
    load_type_enum(config["type"])
    load_is_mobile_enum(config["mobility"])
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
