import gurobipy as gp
import matplotlib.pyplot as plt
import numpy as np
# import ortools as otlp  # somente LP
from enum import Enum
import pandas as pds


NO_EDGE = 9999999999
DELTA = 0.0001
EPSILON = 0.9999
TAG_COORD = 0
X_COORD = 1
Y_COORD = 2

CURRENT_NODE = 0
NEXT_HOP = 1

CONTENT = 0
STORE = 1

INCREASE = 1
DECREASE = 0

MOBILITY_RATE = 10

ID_REQ = 0
SOURCE = 1
SINK = 2
KEY = 3

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


# This class changes the type of trials.
class Type(Enum):
    SINGLE = 1
    ZIPF = 2
    ALLTOALL = 3


class Mobility(Enum):
    IS_MOBILE = 1
    NON_MOBILE = 0


class Model(Enum):
    ONLINE = 1
    OFFLINE = 0


# This class manages and handles the data of an instance of the problem.
class Data:
    requests = list()
    id_req = 0
    __id_event = 0
    __s = list()

    graph_adj_matrix = None
    req = list()
    req_dict = dict()

    mobility = Mobility
    mobility_rate = 0
    # Input
    alpha = 0
    beta = 0

    # Parameters
    num_bs = 0
    num_ue = 0
    num_nodes = 0
    num_files = 0

    # f \in F
    key_index_file = list()
    # i \in BS
    key_index_bs = list()
    # u \in UE
    key_index_ue = list()

    # V = BU \cup UE
    key_index_with_file = list()
    key_index_with_ue = list()
    key_index_all = list()

    # ij \in E
    e_bs_adj = list()

    # cr_k \in N
    resources_file = list()
    # cs_k \in N
    size_file = list()

    # thp \in N
    throughput_min_file = list()

    # bsr_i \in R
    resources_node = list()

    rtt_min = 0

    # rtt_ij \in R
    rtt_edge = None

    # D \in R
    radius_mbs = 0
    radius_sbs = 0
    distance_ue = list()
    distance_bs = list()

    # gama \in {0,1}
    gama_file_node = list()

    # psi \in {0,1}
    psi_edge = list()

    # Vars

    # omega
    omega_user_node = None

    # bwc_ij \in R
    throughput_current_edge = None

    # bwdiff_fij \in R
    throughput_diff_edge = None

    # rr_i \in R
    current_resources_node = None

    # c_fij \in R
    weight_network = None

    weight_network_dict = dict()

    connectivity_edges = None
    connectivity_edges_dict = dict()

    throughput_current_edge_dict = dict()
    throughput_diff_edge_dict = dict()
    resources_file_dict = dict()
    size_file_dict = dict()
    resources_node_dict = dict()
    current_resources_node_dict = dict()
    throughput_min_file_dict = dict()
    gama_file_node_dict = dict()
    omega_user_node_dict = dict()
    e_bs_adj_dict = dict()
    psi_edge_dict = dict()
    rtt_edge_dict = dict()
    rtt_min_dict = dict()
    distance_ue_dict = dict()

    def __init__(self, mobility: object = Mobility.NON_MOBILE, mr=0,
                 alpha=0, beta=0, num_bs=0, num_ue=0, num_file=0,
                 key_f=None, key_i=None, key_u=None,
                 e_bs_adj=None,rf=None,
                 sf=None, bwf=None, rt_i=None, rtt_min=None, radius_mbs=0, radius_sbs=0,
                 gama_file_node=None, dis_ue=None, dis_bs=None):

        self.mobility = mobility
        self.mobility_rate = mr
        self.alpha = alpha
        self.beta = beta

        self.num_bs = num_bs
        self.num_ue = num_ue
        if num_bs != 0 and num_ue != 0:
            self.num_nodes = num_bs + num_ue
        self.num_files = num_file

        if key_f is not None and key_i is not None and key_u is not None:
            self.key_index_file = key_f
            self.key_index_bs = key_i
            self.key_index_ue = key_u
            self.key_index_with_file = key_i + key_f
            self.key_index_with_ue = key_i + key_u
            self.key_index_all = key_i + key_u + key_f

        self.e_bs_adj = e_bs_adj

        self.resources_file = rf
        self.size_file = sf
        self.throughput_min_file = bwf
        self.resources_node = rt_i

        self.rtt_min = rtt_min
        self.radius_mbs = radius_mbs
        self.radius_sbs = radius_sbs
        self.distance_ue = dis_ue
        self.distance_bs = dis_bs

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.req = [[0 for f in range(self.num_files)] for u in range(self.num_ue)]
            self.gama_file_node = gama_file_node

            self.__resources_file_to_dictionary()
            self.__size_file_to_dictionary()
            self.__resources_node_to_dictionary()
            self.__throughput_min_file_to_dictionary()
            self.__gama_file_node_to_dictionary()
            self.__e_bs_adj_to_dictionary()
            self.rtt_min_to_dictionary()
            self.distance_ue_to_dictionary()

    def clear_requests(self):
        self.requests.clear()
        self.id_req = 0

    def insert_requests(self, sources, sinks):
        self.__id_event += 1
        new_source = list()
        for r in range(len(sources)):
            self.id_req += 1
            key = str(self.id_req).rjust(8, '0') + '_' + str(sources[r])
            tuple = (self.id_req, sources[r], sinks[r], key)
            new_source.append(key)
            self.requests.append(tuple)

        self.__s += new_source
        return self.__s

    # PARAMETERS TO DICTIONARY
    def __resources_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.resources_file_dict[tag] = self.resources_file[f]

    def __size_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.size_file_dict[tag] = self.size_file[f]

    def __throughput_min_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.throughput_min_file_dict[tag] = self.throughput_min_file[f]

    def __resources_node_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.resources_node_dict[tag] = self.resources_node[i]

    def __gama_file_node_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_bs)):
                tag_file = self.key_index_file[f]
                tag_bs = self.key_index_bs[i]
                self.gama_file_node_dict[tag_file, tag_bs] = self.gama_file_node[f][i]

    def __e_bs_adj_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            for j in range(len(self.key_index_bs)):
                tag_orig = self.key_index_bs[i]
                tag_dest = self.key_index_bs[j]
                self.e_bs_adj_dict[tag_orig, tag_dest] = self.e_bs_adj[i][j]

    def rtt_edge_to_dictionary(self):
        for i in range(len(self.key_index_with_ue)):
            for j in range(len(self.key_index_with_ue)):
                tag_orig = self.key_index_with_ue[i]
                tag_dest = self.key_index_with_ue[j]
                self.rtt_edge_dict[tag_orig, tag_dest] = self.rtt_edge[i][j]

    def rtt_min_to_dictionary(self):
        for i in range(len(self.key_index_with_ue)):
            for j in range(len(self.key_index_with_ue)):
                tag_orig = self.key_index_with_ue[i]
                tag_dest = self.key_index_with_ue[j]
                self.rtt_min_dict[tag_orig, tag_dest] = self.rtt_min[i][j]

    def distance_ue_to_dictionary(self):
        for u in range(len(self.key_index_ue)):
            for i in range(len(self.key_index_bs)):
                tag_ue = self.key_index_ue[u]
                tag_bs = self.key_index_bs[i]
                self.distance_ue_dict[tag_ue, tag_bs] = self.distance_ue[u][i]

    # VARS TO DICTIONARY
    def omega_user_node_to_dictionary(self):
        for u in range(len(self.key_index_ue)):
            for i in range(len(self.key_index_bs)):
                tag_ue = self.key_index_ue[u]
                tag_bs = self.key_index_bs[i]
                self.omega_user_node_dict[tag_ue, tag_bs] = self.omega_user_node[u][i]

    def throughput_current_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.throughput_current_edge_dict[tag_file, tag_orig, tag_dest] = \
                        self.throughput_current_edge[f][i][
                            j]

    def throughput_diff_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_with_ue)):
                for j in range(len(self.key_index_with_ue)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_with_ue[i]
                    tag_dest = self.key_index_with_ue[j]
                    self.throughput_diff_edge_dict[tag_file, tag_orig, tag_dest] = self.throughput_diff_edge[f][i][j]

    def psi_edge_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.psi_edge_dict[tag_file, tag_orig, tag_dest] = self.psi_edge[f][i][j]

    def weight_network_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.weight_network_dict[tag_file, tag_orig, tag_dest] = self.weight_network[f][i][j]

    def connectivity_edges_to_dictionary(self):
        for c in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[c]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.connectivity_edges_dict[tag_file, tag_orig, tag_dest] = self.connectivity_edges[c][i][j]

    def set_graph_adj_matrix(self):
        self.graph_adj_matrix= [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in
                                       range(self.num_nodes + self.num_files)]

        for c in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    if (self.weight_network[c][i][j] != NO_EDGE) and (self.graph_adj_matrix[i][j] == NO_EDGE):
                        self.graph_adj_matrix[i][j] = self.weight_network[c][i][j]


# This class handles and calculates the variables and parameters.
class HandleData:
    hosts = None
    paths = None
    __old_hosts = None
    __old_paths = None
    __data = Data()

    def __init__(self, data):
        self.__data = data

    def calc_vars(self, is_update=False):
        self.__calc_omega_user_node()
        if not is_update:
            self.__generate_rtt()
        self.__calc_current_throughput_edge()
        self.__calc_diff_throughput()
        self.__calc_psi_edge()

        self.__calc_weight_network()
        self.__calc_connectivity_edges()

    def __calc_connectivity_edges(self):
        self.__data.connectivity_edges = [[[0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
                                           range(self.__data.num_nodes + self.__data.num_files)] for
                                          f in range(self.__data.num_files)]
        for c in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_all)):
                for j in range(len(self.__data.key_index_all)):
                    if self.__data.weight_network[c][i][j] != NO_EDGE:
                        self.__data.connectivity_edges[c][i][j] = 1
        self.__data.connectivity_edges_to_dictionary()

    def __calc_omega_user_node(self):
        self.__data.omega_user_node = [[0 for i in range(self.__data.num_bs)] for u in range(self.__data.num_ue)]

        for u in range(len(self.__data.key_index_ue)):
            for i, tag_i in enumerate(self.__data.key_index_bs):
                if tag_i[:3] == 'MBS':
                    # if self.__data.distance_ue[u][i] <= self.__data.radius_mbs: UE não tem cobertura de MBS.
                    self.__data.omega_user_node[u][i] = 0
                else:
                    if self.__data.distance_ue[u][i] <= self.__data.radius_sbs:
                        self.__data.omega_user_node[u][i] = 1

        self.__data.omega_user_node_to_dictionary()

    def __generate_rtt(self):
        self.__data.rtt_edge = [[NO_EDGE for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
                                range(self.__data.num_nodes + self.__data.num_files)]

        for i, tag_i in enumerate(self.__data.key_index_all):
            for j, tag_j in enumerate(self.__data.key_index_all):
                if i != j:
                    if (tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (
                            tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS') or (
                            tag_i[:3] == 'SBS' and tag_j[:3] == 'SBS'):
                        if self.__is_coverage_bs_to_bs(tag_i, tag_j):
                            self.__data.rtt_edge[i][j] = self.__data.rtt_min[i][j]
                            self.__data.rtt_edge[j][i] = self.__data.rtt_min[j][i]
                        else:
                            self.__data.rtt_edge[i][j] = NO_EDGE
                            self.__data.rtt_edge[j][i] = NO_EDGE
                    if (tag_i[:3] == 'SBS' and tag_j[:2] == 'UE'):
                        if self.__is_coverage_bs_to_ue(tag_i, tag_j):
                            self.__data.rtt_edge[i][j] = self.__calc_rtt_bs_to_ue_increase(tag_i, tag_j,
                                                                                           self.__data.rtt_min[i][j])
                    if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                        if self.__is_caching(tag_i, tag_j):
                            self.__data.rtt_edge[i][j] = 0
                else:
                    self.__data.rtt_edge[i][j] = NO_EDGE
                    self.__data.rtt_edge[j][i] = NO_EDGE

        self.__data.rtt_edge_to_dictionary()

    def __calc_rtt_bs_to_ue_increase(self, bs, ue, rtt_previous):
        rtt = 0
        if self.__data.omega_user_node_dict[ue, bs] == 1:
            rtt = rtt_previous * 1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs)
        else:
            rtt = NO_EDGE
        return rtt

    def __calc_rtt_bs_to_ue_decrease(self, bs, ue, rtt_previous):
        rtt = 0
        if self.__data.omega_user_node_dict[ue, bs] == 1:
            rtt = rtt_previous / 1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs)
        else:
            rtt = NO_EDGE
        return rtt

    def __calc_current_throughput_edge(self):
        self.__data.throughput_current_edge = [
            [[0.0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
             range(self.__data.num_nodes + self.__data.num_files)]
            for f
            in
            range(self.__data.num_files)]

        for f, tag_f in enumerate(self.__data.key_index_file):
            for i, tag_i in enumerate(self.__data.key_index_all):
                for j in range(len(self.__data.key_index_all)):
                    size_f = self.__data.size_file[f]
                    if self.__data.rtt_edge is not None:
                        if self.__data.rtt_edge[i][j] == 0:
                            if tag_f == tag_i:
                                self.__data.throughput_current_edge[f][i][j] = NO_EDGE
                        else:
                            self.__data.throughput_current_edge[f][i][j] = round(size_f // self.__data.rtt_edge[i][j],
                                                                                 2)

        self.__data.throughput_current_to_dictionary()

    def __calc_diff_throughput(self):
        self.__data.throughput_diff_edge = [
            [[0.0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
             range(self.__data.num_nodes + self.__data.num_files)]
            for f in
            range(self.__data.num_files)]

        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_with_ue)):
                for j in range(len(self.__data.key_index_with_ue)):
                    if self.__data.throughput_current_edge[f][i][j] == NO_EDGE:
                        self.__data.throughput_diff_edge[f][i][j] = 0.0
                    if self.__data.throughput_current_edge[f][i][j] == 0:
                        self.__data.throughput_diff_edge[f][i][j] = 0.0
                    else:
                        self.__data.throughput_diff_edge[f][i][j] = round(
                            self.__data.throughput_current_edge[f][i][j] - self.__data.throughput_min_file[f], 2)
        self.__data.throughput_diff_to_dictionary()

    def __calc_psi_edge(self):
        self.__data.psi_edge = [
            [[0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
             range(self.__data.num_nodes + self.__data.num_files)]
            for f in
            range(self.__data.num_files)]

        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_all)):
                for j in range(len(self.__data.key_index_all)):
                    if self.__data.throughput_diff_edge[f][i][j] >= self.__data.beta:
                        self.__data.psi_edge[f][i][j] = 1
        self.__data.psi_edge_to_dictionary()

    def __calc_weight_network(self):
        self.__data.weight_network = [[[NO_EDGE for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
                                       range(self.__data.num_nodes + self.__data.num_files)] for
                                      f in range(self.__data.num_files)]
        for f, tag_f in enumerate(self.__data.key_index_file):
            for i, tag_i in enumerate(self.__data.key_index_all):
                for j, tag_j in enumerate(self.__data.key_index_all):
                    thp_c = self.__data.throughput_current_edge_dict[tag_f, tag_i, tag_j]
                    thp_min = self.__data.throughput_min_file_dict[tag_f]

                    if (tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'SBS' and tag_j[:3] == 'SBS') or (
                            tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS'):
                        if self.__is_coverage_bs_to_bs(tag_i, tag_j):
                            self.__data.weight_network[f][i][j] = self.__weight_network(thp_c, thp_min)
                    if tag_i[:3] == 'SBS' and tag_j[:2] == 'UE':
                        if self.__is_coverage_bs_to_ue2(tag_j, tag_i):
                            self.__data.weight_network[f][i][j] = self.__weight_network(thp_c, thp_min)

                    if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                        if self.__is_caching(tag_i, tag_j) and (tag_f == tag_i):
                            self.__data.weight_network[f][i][j] = 0

        self.__data.weight_network_to_dictionary()

    def __weight_network(self, thp_c, thp_min):
        if thp_c == 0:
            return NO_EDGE
        if thp_c == NO_EDGE:
            return 1
        return (thp_c / thp_min)

    def __is_caching(self, file, bs):
        return self.__data.gama_file_node_dict[file, bs] == 1

    def __is_coverage_bs_to_bs(self, orig, dest):
        return self.__data.e_bs_adj_dict[orig, dest] == 1

    def __is_coverage_bs_to_ue(self, orig, dest):
        return self.__data.omega_user_node_dict[dest, orig] == 1

    def __is_coverage_bs_to_ue2(self, u, bs):
        return self.__data.omega_user_node_dict[u, bs] == 1

    # This follow method update data of the problem.
    def update_data(self):
        self.__old_hosts = self.hosts
        self.__old_paths = self.paths
        sense = -1
        if self.__data.mobility == Mobility.IS_MOBILE:
            sense = self.__update_ue_position()

        self.__update_rtt(sense)
        self.calc_vars(True)

    def __update_rtt(self, sense):
        for i, tag_i in enumerate(self.__data.key_index_all):
            for j, tag_j in enumerate(self.__data.key_index_all):
                if self.__data.rtt_edge[i][j] != NO_EDGE:
                    if (tag_i[:3] == 'SBS' and tag_j[:2] == 'UE'):
                        if sense == INCREASE:
                            self.__data.rtt_edge[i][j] = self.__calc_rtt_bs_to_ue_increase(tag_i, tag_j,
                                                                                           self.__data.rtt_edge[i][j])
                        if sense == DECREASE:
                            self.__data.rtt_edge[i][j] = self.__calc_rtt_bs_to_ue_decrease(tag_i, tag_j,
                                                                                           self.__data.rtt_edge[i][j])
        self.__data.rtt_edge_to_dictionary()

    def __update_ue_position(self):
        sense = -1
        for u in range(len(self.__data.key_index_ue)):
            for i in range(len(self.__data.key_index_bs)):
                new_dis = np.random.normal(-self.__data.mobility_rate, self.__data.mobility_rate, 1)
                if new_dis > self.__data.distance_ue[u][i]:
                    sense = INCREASE
                else:
                    sense = DECREASE
                self.__data.distance_ue[u][i] += new_dis
        return sense

    def show_reallocation(self):
        for op, np in zip(self.__old_paths, self.paths[:len(self.__old_paths)]):
            if op != np:
                print("SHIFT PATH [{0}]".format(self.paths.index(np)))
            else:
                print("NON-SHIFT PATH [{0}]".format(self.paths.index(np)))

        for oh, nh in zip(self.__old_hosts, self.hosts[:len(self.__old_hosts)]):
            if oh != nh:
                print("SHIFT HOST.")
            else:
                print("NON-SHIFT.")


# This class execute the application model.
class OptimizeData:
    __data = Data()
    __path = list()
    __paths = list()
    __hosts = list()

    model = None
    x = gp.Var
    y = gp.Var

    def __init__(self, data, sources, sinks):
        self.__data = data
        self.s = sources
        self.t = sinks
        self.s = self.__data.insert_requests(sources, sinks)

    def run_model(self, show_log):
        self.model.reset()
        self.create_vars()
        self.__set_function_objective()
        self.__create_constraints()
        self.execute(show_log)

    def create_vars(self):
        self.__create_var_flow()
        self.__create_var_host()

    # x_ijk \in R+
    def __create_var_flow(self):
        self.x = self.model.addVars(self.s, self.__data.key_index_all, self.__data.key_index_all,
                                    vtype=gp.GRB.SEMICONT, name="flow")

    # y_ik \in R+
    def __create_var_host(self):
        self.y = self.model.addVars(self.s, self.__data.key_index_bs,
                                    vtype=gp.GRB.SEMICONT, name="host")

    def __set_function_objective(self):
        self.model.setObjective((self.__data.alpha * (gp.quicksum((self.__data.resources_file_dict[c[SOURCE]] * self.__data.req_dict[u[SINK], c[SOURCE]] *(self.y[c[KEY],i]))/((self.__data.resources_node_dict[i] * self.__data.gama_file_node_dict[c[SOURCE], i]) + DELTA)
                                for i in self.__data.key_index_bs for c in self.__data.requests for u in self.__data.requests)))
                                +
                                ((1 - self.__data.alpha) * (gp.quicksum(
                                    self.__data.weight_network_dict[c[SOURCE], i, j] * self.x[c[KEY], i, j]
                                    * self.__data.req_dict[u[SINK], c[SOURCE]]
                                    * self.__data.psi_edge_dict[c[SOURCE], i, j]
                                    * self.__data.connectivity_edges_dict[c[SOURCE], i, j] for j in
                                    self.__data.key_index_all for i in self.__data.key_index_all for c in
                                    self.__data.requests for u in self.__data.requests)))
                                , sense=gp.GRB.MINIMIZE)

    def __create_constraints(self):
        # This constraint set y value.
        self.__set_constraint_y_value()

        # This constraint limit the use  of node resources.
        self.__set_constraint_node_resources_capacity()

        # This constraint ensures that the throughput current being the most than the throughput minimum of content.
        self.__set_constraint_throughput()

        # This constraint ensures the equilibrium of flow between nodes intermediary in the network.
        self.__set_constraint_flow_conservation()

        # This constraint ensures the equilibrium of flow in the source nodes in the network.
        self.__set_constraint_flow_conservation_source()

        # This constraint ensures the equilibrium of flow in the destiny(sink) nodes in the network.
        self.__set_constraint_flow_conservation_sink()

    def __set_constraint_y_value(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_bs:
                self.model.addConstr(self.y[req[KEY], i] <= (self.x[req[KEY], req[SOURCE], i] / self.__data.size_file_dict[req[SOURCE]]) + EPSILON)
                self.model.addConstr(self.y[req[KEY], i] >= (self.x[req[KEY], req[SOURCE], i] / self.__data.size_file_dict[req[SOURCE]]))

    def __set_constraint_node_resources_capacity(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_bs:
                self.model.addConstr(self.__data.resources_node_dict[i] >= gp.quicksum( self.__data.resources_file_dict[req[SOURCE]] * self.y[req[KEY],i] for i in self.__data.key_index_bs))

    def __set_constraint_throughput(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_all:
                for j in self.__data.key_index_all:
                    self.model.addConstr(((self.x[req[KEY], i, j] * self.__data.req_dict[req[SINK], req[SOURCE]]) * (
                            self.__data.throughput_current_edge_dict[req[SOURCE], i, j] -
                            self.__data.throughput_min_file_dict[req[SOURCE]]))
                                         * self.__data.connectivity_edges_dict[req[SOURCE], i, j]
                                         >= 0)

    def __set_constraint_flow_conservation(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_bs:
                self.model.addConstr(gp.quicksum(
                    self.x[req[KEY], i, j]
                    * self.__data.req_dict[req[SINK], req[SOURCE]]
                    * self.__data.connectivity_edges_dict[req[SOURCE], i, j]
                    for j in
                    self.__data.key_index_all)
                                     - gp.quicksum(
                    self.x[req[KEY], j, i]
                    * self.__data.req_dict[req[SINK], req[SOURCE]]
                    * self.__data.connectivity_edges_dict[req[SOURCE], j, i]
                    for j in
                    self.__data.key_index_all)
                                     == 0, 'c4')

    def __set_constraint_flow_conservation_source(self):
        for req in self.__data.requests:
            self.model.addConstr(
                    (self.__data.throughput_min_file_dict[req[SOURCE]]) == (
                                             gp.quicksum(
                                                 self.x[req[KEY], req[SOURCE], i]
                                                 * self.__data.connectivity_edges_dict[req[SOURCE], req[SOURCE], i]
                                                 for i in self.__data.key_index_bs
                                             )
                                             - gp.quicksum(
                                         self.x[req[KEY], i, req[SOURCE]]
                                         * self.__data.connectivity_edges_dict[req[SOURCE], i, req[SOURCE]]
                                         for i in self.__data.key_index_bs
                                     ))
                                     , 'c5')

    def __set_constraint_flow_conservation_sink(self):
        for req in self.__data.requests:
            self.model.addConstr(
                (- self.__data.throughput_min_file_dict[req[SOURCE]]) == (
                                         gp.quicksum(
                                             self.x[req[KEY], req[SINK], i]
                                             * self.__data.connectivity_edges_dict[req[SOURCE], req[SINK], i]
                                             for i in self.__data.key_index_bs
                                         )
                                         - gp.quicksum(
                                     self.x[req[KEY], i, req[SINK]]
                                     * self.__data.connectivity_edges_dict[req[SOURCE], i, req[SINK]]
                                     for i in self.__data.key_index_bs
                                 ))
                                 , 'c6')

    def execute(self, log):
        self.model.setParam("LogToConsole", log)
        self.model.optimize()

    def result(self):
        if self.model.status == gp.GRB.OPTIMAL:
            print(GREEN, "OPTIMAL SOLVE.", RESET)
            obj = self.model.getObjective()
            print(CYAN, "OBJECTIVE FUNCTION: ", RED, str(obj.getValue()), RESET)
            print(BOLD, "DECISION VARIABLE:", BOLD)
            for var in self.model.getVars():
                if var.X > 0:
                    print(var.VarName, round(var.X, 2))
        else:
            print(RED, "THE SOLVE IS INFEASIBLE.")

    def solutions(self, show_path):
        self.__solution_path()
        self.__solution_host()
        if self.__paths is None:
            return (None, None)
        if show_path:
            for req in range(len(self.__paths)):
                print(REVERSE, " {0} - PATH: {1} | HOST: {2}".format(req,self.__paths[req],self.__hosts[req]), RESET)
        return (self.__paths, self.__hosts)

    def __solution_host(self):
        self.__hosts.clear()
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X != 0 and var.VarName[:4] == "host":
                    self.__hosts.append(str(var.VarName).split(',')[1][:-1])

    def __solution_path(self):
        self.__path.clear()
        self.__paths.clear()
        hops = list()
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X != 0 and var.VarName[:4] == "flow":
                    hops.append(self.__get_solution(str(var.VarName)))
        for req in self.__data.requests:
            self.__make_path(hops, req[SOURCE], req[SINK])
        self.__split_paths()

    def __split_paths(self):
        init = 0
        for u, tag_u in enumerate(self.__path):
            if tag_u[:2] == "UE":
                self.__paths.append(self.__path[init:u + 1])
                init = u + 1

    def __get_solution(self, hop):
        next_hop = list()
        hop = hop[5:]
        hop = hop[:-1]
        aux = hop.split(',')
        next_hop.append(aux[1])
        next_hop.append(aux[2])
        return next_hop

    def __make_path(self, hops, source, sink):
        self.__next_hop(hops, source)
        self.__path.append(sink)

    def __next_hop(self, hops, node):
        for i in range(len(hops)):
            if node in hops[i][CURRENT_NODE]:
                self.__path.append(hops[i][CURRENT_NODE])
                return self.__next_hop(hops, hops[i][NEXT_HOP])

    def create_model_in_ortools(self):
        pass


# This class show data in parameters and vars.
class LogData:
    data = Data()

    def __init__(self, data):
        self.data = data

    # PARAMETERS
    def __log_rtt_edge(self):
        print("EDGE RTT.")
        for i in range(len(self.data.key_index_all)):
            for j in range(len(self.data.key_index_all)):
                if self.data.rtt_edge[i][j] == NO_EDGE:
                    print('ထ', end=" ")
                else:
                    print(self.data.rtt_edge[i][j], end=" ")
            print()
        print()

    def __log_rtt_edge_dict(self):
        print("EDGE RTT.")
        for k in self.data.rtt_edge_dict.keys():
            print(k, self.data.rtt_edge_dict[k])
        print()

    def __log_resources_file_dict(self):
        print("RESOURCES FILE.")
        for k in self.data.resources_file_dict.keys():
            print(k, self.data.resources_file_dict[k])
        print()

    def __log_size_file_dict(self):
        print("SIZE FILE.")
        for k in self.data.size_file_dict.keys():
            print(k, self.data.size_file_dict[k], "MB")
        print()

    def __log_resources_node_dict(self):
        print("TOTAL RESOURCES NODE.")
        for k in self.data.resources_node_dict.keys():
            print(k, self.data.resources_node_dict[k])
        print()

    def __log_throughput_min_dict(self):
        print("MINIMAL THROUGHPUT.")
        for k in self.data.throughput_min_file_dict.keys():
            print(k, self.data.throughput_min_file_dict[k], "MB")
        print()

    def __log_rtt_min(self):
        print("MINIMUM RTT.")
        for i in range(len(self.data.key_index_all)):
            for j in range(len(self.data.key_index_all)):
                if self.data.rtt_min[i][j] == NO_EDGE:
                    print('ထ', end=" ")
                else:
                    print(self.data.rtt_min[i][j], end=" ")
            print()
        print()

    def __log_rtt_min_dict(self):
        print("MINIMUM RTT.")
        for k in self.data.rtt_min_dict.keys():
            print(k, self.data.rtt_min_dict[k])
        print()

    def __log_gama_file_node(self):
        print("FILE CACHING PER BASE STATION(GAMA).")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.gama_file_node[f][i], end=" ")
            print()
        print()

    def __log_e_bs_adj(self):
        print("COVERAGE BETWEEN BASE STATIONS(E).")
        for i in range(len(self.data.key_index_bs)):
            for j in range(len(self.data.key_index_bs)):
                print(self.data.e_bs_adj[i][j], end=" ")
            print()
        print()

    def __log_e_bs_adj_dict(self):
        print("COVERAGE BETWEEN BASE STATIONS(E).")
        for k in self.data.e_bs_adj_dict.keys():
            print(k, self.data.e_bs_adj_dict[k])
        print()

    # VARS

    def __log_omega_user_node(self):
        print("USER COVERAGE PER BASE STATION(OMEGA).")
        for u in range(len(self.data.key_index_ue)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.omega_user_node[u][i], end=" ")
            print()
        print()

    def __log_omega_user_node_dict(self):
        print("USER COVERAGE PER BASE STATION(OMEGA).")
        for k in self.data.omega_user_node_dict.keys():
            print(k, self.data.omega_user_node_dict[k])

    def __log_current_throughput_edge(self):
        print("CURRENT THROUGHPUT.")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    if self.data.throughput_current_edge[f][i][j] == NO_EDGE:
                        print('ထ', end=" ")
                    else:
                        print(self.data.throughput_current_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def __log_current_throughput_edge_dict(self):
        print("CURRENT THROUGHPUT.")
        for k in self.data.throughput_current_edge_dict.keys():
            print(k, self.data.throughput_current_edge_dict[k])

    def __log_diff_throughput_edge(self):
        print("DIFFERENCE THROUGHPUT")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.throughput_diff_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def __log_diff_throughput_edge_dict(self):
        print("DIFFERENCE THROUGHPUT")
        for k in self.data.throughput_diff_edge_dict.keys():
            print(k, self.data.throughput_diff_edge_dict[k])

    def __log_psi_edge(self):
        print("DIFFERENCE INSIDE BOUND BETA (beta).")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.psi_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def __log_psi_edge_dict(self):
        print("DIFFERENCE INSIDE BOUND BETA (beta).")
        for k in self.data.psi_edge_dict.keys():
            print(k, self.data.psi_edge_dict[k])

    def __log_weight_network(self):
        print("WEIGHT NETWORK.")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    if self.data.weight_network[f][i][j] == NO_EDGE:
                        print('ထ', end=" ")
                    else:
                        print(str(self.data.weight_network[f][i][j]).format(), end=" ")
                print()
            print()
        print()

    def __log_weight_network_dict(self):
        print("WEIGHT NETWORK.")
        for k in self.data.weight_network_dict.keys():
            print(k, self.data.weight_network_dict[k])
        print()

    def __log_connectivity_edges(self):
        print("CONNECTIVITY EDGES.")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(str(self.data.connectivity_edges[f][i][j]).format(), end=" ")
                print()
            print()
        print()

    def __log_connectivity_edges_dict(self):
        print("CONNECTIVITY EDGES.")
        for k in self.data.connectivity_edges_dict.keys():
            print(k, self.data.connectivity_edges_dict[k])
        print()

    def show_parameters(self):
        print("PARAMETERS.\n")
        self.__log_resources_file_dict()
        self.__log_size_file_dict()
        self.__log_throughput_min_dict()

        self.__log_resources_node_dict()

        self.__log_rtt_min()
        self.__log_rtt_edge()
        # self.__log_rtt_min_dict()
        # self.__log_rtt_edge_dict()
        self.__log_gama_file_node()
        self.__log_e_bs_adj_dict()

    def show_vars_matrix(self):
        print("VARS.\n")
        self.__log_omega_user_node()
        self.__log_current_throughput_edge()
        self.__log_diff_throughput_edge()
        self.__log_psi_edge()
        self.__log_weight_network()
        self.__log_connectivity_edges()

    def show_vars_dict(self):
        print("VARS.\n")
        self.__log_omega_user_node_dict()
        self.__log_current_throughput_edge_dict()
        self.__log_diff_throughput_edge_dict()
        self.__log_psi_edge_dict()
        self.__log_weight_network_dict()
        self.__log_connectivity_edges_dict()


# This class store all result and plot a graphics.
class PlotData:
    __data = Data()
    set_path = None
    __delay = None
    __events_count = 0
    __req_count = 0

    __paths = None
    all_requests = 0
    admission_requests = 0
    __rate_admission_requests = 0

    def __init__(self, data):
        self.__data = data
        self.set_path = pds.DataFrame(columns=['Path', 'Source', 'Sink', 'Delay'])
        self.__delay = pds.DataFrame(columns=['Event', 'Delay'])
        self.__paths = pds.DataFrame(columns=['Event', 'Request', 'Source', 'Sink', 'Path', 'Host'])

    def insert_req(self,paths,hosts,event):
        self.__events_count = event
        for r in range(len(paths)):
            self.__paths = self.__paths.append({'Event': event, 'Request': r ,'Source': paths[r][:1], 'Sink': paths[r][-1:], 'Path': paths[r],'Host': hosts[r]}, ignore_index=True)

    def calc_rate_admission_requests(self, admission_requests, all_requests):
        self.admission_requests = admission_requests
        self.all_requests = all_requests
        self.__rate_admission_requests = admission_requests / all_requests

    def insert_path(self, path, source, sink, event, req):
        self.__events_count = event
        self.__req_count = req
        self.set_path = self.set_path.append(
            {'Path': path.copy(), 'Source': source, 'Sink': sink, 'Delay': self.__sum_rtt(path)},
            ignore_index=True)
        self.__insert_delay(path)

    def update_path(self, path, req):
        self.set_path._set_value(req, 'Path', path.copy())
        self.__update_delay()

    def __sum_rtt(self, path):
        rtt = 0
        for i, j in zip(path[1:], path[2:]):
            if self.__data.rtt_edge_dict[i, j] >= NO_EDGE:
                continue
            rtt += self.__data.rtt_edge_dict[i, j]
        return rtt

    def show_paths(self):
        print("SET PATH.")
        print(self.set_path)
        print(self.__delay)

    def __insert_delay(self, path, ):
        self.__delay = self.__delay.append(
            {'Id': self.set_path.shape[0] - 1, 'Event': self.__events_count, 'Delay': self.__sum_rtt(path)},
            ignore_index=True)

    def __update_delay(self):
        for i, row in self.set_path.iterrows():
            self.__delay = self.__delay.append(
                {'Id': i, 'Event': self.__events_count, 'Delay': self.__sum_rtt(row['Path'])}, ignore_index=True)
            self.set_path._set_value(i, 'Delay', self.__sum_rtt(row['Path']))

    def plot(self):
        plt.title('Average delay per time')
        plt.ylabel('Average delay')
        plt.xlabel('Time')
        plt.plot(self.__average_delay_per_requisitions())
        plt.show()

    def __average_delay_per_requisitions(self):
        avg_delay_event = list()
        for event in range(self.__events_count):
            select_event = self.__delay.loc[self.__delay['Event'] == event]
            avg_delay_event.append(self.__calc_avg(select_event))
        return avg_delay_event

    def __calc_avg(self, select_event):
        all_delay_event = list()
        for i, row in select_event.iterrows():
            all_delay_event.append(row['Delay'])
        return np.mean(all_delay_event)

    def save_data(self, path):
        dt_rate_admission = pds.DataFrame({'Rate Admission':[self.__rate_admission_requests],'Admission Requests':[self.admission_requests],'All Requests':[self.all_requests]})
        with pds.ExcelWriter(path) as writer:
            # self.__delay.to_excel(writer, sheet_name='Delay')
            # self.set_path.to_excel(writer, sheet_name='Request')
            self.__paths.to_excel(writer,sheet_name='Requests')
            dt_rate_admission.to_excel(writer,sheet_name='Rate Admission')