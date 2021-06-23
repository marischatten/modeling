import gurobipy as gp
import statistics as s
import statistics
import random

import matplotlib.pyplot as plt

from utils import utils as utils
import itertools
import numpy as np
import ortools as otlp  # somente LP
from enum import Enum
import uuid
import pandas as pds
from random import randrange

NO_EDGE = 9999999999

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


class Reallocation(Enum):
    REALLOCATION = 1
    NON_REALLOCATION = 0


# This class manages and handles the data of an instance of the problem.
class Data:
    requests = list()
    id_req = 0
    __id_event = 0
    __s = list()

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

    e_bs_adj = list()

    # fr \in R
    resources_file = list()
    size_file = list()
    # phi_node \in R
    phi_node = list()

    # bwf \in R
    throughput_min_file = list()

    # rt_i \in R
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

    # bwe_ij \in R
    throughput_expected_edge = None

    # bwdiff_fij \in R
    throughput_diff_edge = None

    # rr_i \in R
    current_resources_node = None

    # c_fij \in R
    weight_network = None
    weight_resources = None

    weight_network_dict = dict()
    weight_resources_dict = dict()

    connectivity_edges = None
    connectivity_edges_dict = dict()

    throughput_current_edge_dict = dict()
    throughput_expected_edge_dict = dict()
    throughput_diff_edge_dict = dict()
    resources_file_dict = dict()
    size_file_dict = dict()
    resources_node_dict = dict()
    current_resources_node_dict = dict()
    phi_node_dict = dict()
    throughput_min_file_dict = dict()
    gama_file_node_dict = dict()
    omega_user_node_dict = dict()
    e_bs_adj_dict = dict()
    psi_edge_dict = dict()
    rtt_edge_dict = dict()
    rtt_min_dict = dict()
    distance_ue_dict = dict()

    def __init__(self, mobility: object = Mobility.NON_MOBILE, mr=0, alpha=0, beta=0, num_bs=0, num_ue=0, num_file=0,
                 key_f=None, key_i=None, key_u=None,
                 e_bs_adj=None,
                 rf=None, sf=None, phi_node=None, bwf=None, rt_i=None, rtt_min=None, radius_mbs=0, radius_sbs=0,
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
        self.phi_node = phi_node
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
            self.phi_node_to_dictionary()
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
    def phi_node_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_bs)):
                tag_file = self.key_index_file[f]
                tag_user = self.key_index_bs[i]
                self.phi_node_dict[tag_file, tag_user] = self.phi_node[f][i]

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

    def throughput_expected_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.throughput_expected_edge_dict[tag_file, tag_orig, tag_dest] = \
                        self.throughput_expected_edge[f][i][j]

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

    def current_resources_node_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.current_resources_node_dict[tag] = self.current_resources_node[i]

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

    def weight_resources_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.weight_resources_dict[tag] = self.weight_resources[i]

    def connectivity_edges_to_dictionary(self):
        for c in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[c]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.connectivity_edges_dict[tag_file, tag_orig, tag_dest] = self.connectivity_edges[c][i][j]


# This class handles and calculates the variables and parameters.
class HandleData:
    paths = None
    old_path = None
    show_reallocation = None
    reallocation = None
    __data = Data()

    def __init__(self, data):
        self.__data = data

    def calc_vars(self, is_update=False):
        self.__calc_omega_user_node()
        if not is_update:
            self.__generate_rtt()
        self.__calc_expected_throughput_edge()
        self.__calc_current_throughput_edge()
        self.__calc_diff_throughput()
        self.__calc_psi_edge()
        self.__calc_current_resources_node()
        self.__calc_weight_network()
        self.__calc_weight_resources()
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

    def __calc_expected_throughput_edge(self):
        self.__data.throughput_expected_edge = [
            [[0.0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
             range(self.__data.num_nodes + self.__data.num_files)]
            for f
            in
            range(self.__data.num_files)]

        for f, tag_f in enumerate(self.__data.key_index_file):
            for i, tag_i in enumerate(self.__data.key_index_all):
                for j in range(len(self.__data.key_index_all)):
                    size_f = self.__data.size_file[f]
                    if self.__data.rtt_min is not None:
                        if self.__data.rtt_min[i][j] == 0:
                            if tag_f == tag_i:
                                self.__data.throughput_expected_edge[f][i][j] = NO_EDGE
                        else:
                            self.__data.throughput_expected_edge[f][i][j] = round(size_f // self.__data.rtt_min[i][j],
                                                                                  2)

        self.__data.throughput_expected_to_dictionary()

    def __calc_diff_throughput(self):
        self.__data.throughput_diff_edge = [
            [[0.0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
             range(self.__data.num_nodes + self.__data.num_files)]
            for f in
            range(self.__data.num_files)]

        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_with_ue)):
                for j in range(len(self.__data.key_index_with_ue)):
                    self.__data.throughput_diff_edge[f][i][j] = round(
                        self.__data.throughput_expected_edge[f][i][j] - self.__data.throughput_current_edge[f][i][j], 2)
        self.__data.throughput_diff_to_dictionary()

    def __calc_current_resources_node(self):
        self.__data.current_resources_node = [0 for i in range(self.__data.num_bs)]

        for i in range(len(self.__data.key_index_bs)):
            file = 0
            for f in range(len(self.__data.key_index_file)):
                if self.__data.gama_file_node[f][i] == 1 and self.__data.phi_node[f][i] != 0:
                    file += self.__data.gama_file_node[f][i] * self.__data.resources_file[f] * self.__data.phi_node[f][
                        i]
            self.__data.current_resources_node[i] = file
        self.__data.current_resources_node_to_dictionary()

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
                    thp_e = self.__data.throughput_expected_edge_dict[tag_f, tag_i, tag_j]

                    if (tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'SBS' and tag_j[:3] == 'SBS') or (
                            tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS'):
                        if self.__is_coverage_bs_to_bs(tag_i, tag_j):
                            self.__data.weight_network[f][i][j] = self.__weight_network(thp_c, thp_e)
                    if tag_i[:3] == 'SBS' and tag_j[:2] == 'UE':
                        if self.__is_coverage_bs_to_ue2(tag_j, tag_i):
                            self.__data.weight_network[f][i][j] = self.__weight_network(thp_c, thp_e)

                    if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                        if self.__is_caching(tag_i, tag_j) and (tag_f == tag_i):
                            self.__data.weight_network[f][i][j] = 0

        self.__data.weight_network_to_dictionary()

    def __weight_network(self, thp_c, thp_e):
        if thp_c == 0 and thp_e == 0:
            return NO_EDGE
        if thp_c == NO_EDGE and thp_e == NO_EDGE:
            return 0
        if (thp_c == thp_e) and (thp_c != 0) and (thp_e != 0):
            return 0
        return (thp_c / thp_e)

    def __calc_weight_resources(self):
        self.__data.weight_resources = [0.0 for i in range(self.__data.num_bs)]

        for i, tag_i in enumerate(self.__data.key_index_bs):
            rri = self.__data.current_resources_node_dict[tag_i]
            rti = self.__data.resources_node_dict[tag_i]
            self.__data.weight_resources[i] = self.__weight_resource(rri, rti)

        self.__data.weight_resources_to_dictionary()

    def __weight_resource(self, rri, rti):
        return (rri / rti)

    def __is_caching(self, file, bs):
        return self.__data.gama_file_node_dict[file, bs] == 1

    def __is_coverage_bs_to_bs(self, orig, dest):
        return self.__data.e_bs_adj_dict[orig, dest] == 1

    def __is_coverage_bs_to_ue(self, orig, dest):
        return self.__data.omega_user_node_dict[dest, orig] == 1

    def __is_coverage_bs_to_ue2(self, u, bs):
        return self.__data.omega_user_node_dict[u, bs] == 1

    # This method update data of the problem.
    def update_data(self, is_first=False):
        sense = -1
        if self.__data.mobility == Mobility.IS_MOBILE:
            sense = self.__update_ue_position()
        self.__update_rtt_min()
        self.__update_rtt(sense)
        if is_first or (self.show_reallocation == Reallocation.NON_REALLOCATION):
            self.__insert_phi_node()
        else:
            self.__update_phi_node()
        self.calc_vars(True)

    def __update_rtt_min(self):
        for i in range(len(self.__data.key_index_all)):
            for j in range(len(self.__data.key_index_all)):
                if self.__data.rtt_edge[i][j] <= self.__data.rtt_min[i][j]:
                    self.__data.rtt_min[i][j] = self.__data.rtt_edge[i][j]
        self.__data.rtt_min_to_dictionary()

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

    def __update_phi_node(self):
        # TO DO TypeError: 'NoneType' object is not iterable
        for op, np in zip(self.old_path, self.paths):
            if op != np:
                self.__data.phi_node[op[CONTENT]][op[STORE]] -= 1
                self.__data.phi_node[np[CONTENT]][np[STORE]] += 1
                if self.show_reallocation:
                    print("SHIFT.")
            else:
                if self.show_reallocation:
                    print("NON-SHIFT.")
        self.__data.phi_node_to_dictionary()

    def __insert_phi_node(self):
        for f, file in enumerate(self.__data.key_index_file):
            for j, bs in enumerate(self.__data.key_index_bs):
                for p in range(len(self.paths)):
                    # TO DO TypeError: 'NoneType' object is not iterable
                    # if  self.paths[p] not in self.old_path:
                    if file == self.paths[p][CONTENT] and bs == self.paths[p][STORE]:
                        self.__data.phi_node[f][j] += 1
        self.__data.phi_node_to_dictionary()

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


# This class execute the optimization model.
class OptimizeData:
    __data = Data()

    model = None
    x = None
    s = ""
    t = ""
    __path = list()
    __paths = list()

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

    # x_cij \in {0,1}
    def create_vars(self):
        self.x = self.model.addVars(self.s, self.__data.key_index_all, self.__data.key_index_all,
                                    vtype=gp.GRB.SEMICONT, name="flow")

    def __set_function_objective(self):
        self.model.setObjective((self.__data.alpha * (gp.quicksum(
            self.__data.weight_resources_dict[i] * self.x[c[KEY], c[SOURCE], i] * self.__data.req_dict[
                u[SINK], c[SOURCE]] for i in self.__data.key_index_bs for c in self.__data.requests for u in
            self.__data.requests)))
                                +
                                ((1 - self.__data.alpha) * (gp.quicksum(
                                    self.__data.weight_network_dict[c[SOURCE], i, j] * self.x[c[KEY], i, j] *
                                    self.__data.req_dict[u[SINK], c[SOURCE]]
                                    * self.__data.psi_edge_dict[c[SOURCE], i, j]
                                    * self.__data.connectivity_edges_dict[c[SOURCE], i, j] for j in
                                    self.__data.key_index_all for i in self.__data.key_index_all for c in
                                    self.__data.requests for u in self.__data.requests)))
                                , sense=gp.GRB.MINIMIZE)

    def __create_constraints(self):
        # limite de recursos do nó.
        self.__set_constraint_node_resources_capacity()

        # restrição para vazão esperada seja sempre a menor que a atual.
        self.__set_constraint_throughput()

        # restrições de equilibrio de fluxo em nós intermediarios.
        self.__set_constraint_flow_conservation()

        # restrições de equilibrio de fluxo no nó de origem.
        self.__set_constraint_flow_conservation_source()

        # restrições de equilibrio de fluxo no nó de destino.
        self.__set_constraint_flow_conservation_sink()

    def __set_constraint_node_resources_capacity(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_bs:
                self.model.addConstr(self.x[req[KEY], req[SOURCE], i] * self.__data.req_dict[req[SINK], req[SOURCE]] * (
                        self.__data.resources_node_dict[i] - (
                        self.__data.current_resources_node_dict[i] + self.__data.resources_file_dict[
                    req[SOURCE]])) >= 0)

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
                    self.x[req[KEY], i, j] * self.__data.req_dict[req[SINK], req[SOURCE]]
                    * self.__data.connectivity_edges_dict[req[SOURCE], i, j]
                    for j in
                    self.__data.key_index_all)
                                     - gp.quicksum(
                    self.x[req[KEY], j, i] * self.__data.req_dict[req[SINK], req[SOURCE]]
                    * self.__data.connectivity_edges_dict[req[SOURCE], j, i]
                    for j in
                    self.__data.key_index_all)
                                     == 0, 'c4')

    def __set_constraint_flow_conservation_source(self):
        for req in self.__data.requests:
            self.model.addConstr(gp.quicksum(
                self.x[req[KEY], req[SOURCE], i] * self.__data.req_dict[req[SINK], req[SOURCE]]
                * self.__data.connectivity_edges_dict[req[SOURCE], req[SOURCE], i]
                for i in
                self.__data.key_index_bs)
                                 - gp.quicksum(
                self.x[req[KEY], i, req[SOURCE]] * self.__data.req_dict[req[SINK], req[SOURCE]]
                * self.__data.connectivity_edges_dict[req[SOURCE], i, req[SOURCE]]
                for i in
                self.__data.key_index_bs)
                                 == self.__data.throughput_min_file_dict[req[SOURCE]], 'c5')

    def __set_constraint_flow_conservation_sink(self):
        for req in self.__data.requests:
            self.model.addConstr(gp.quicksum(
                self.x[req[KEY], req[SINK], i] * self.__data.req_dict[req[SINK], req[SOURCE]]
                * self.__data.connectivity_edges_dict[req[SOURCE], req[SINK], i]
                for i in
                self.__data.key_index_bs)
                                 - gp.quicksum(
                self.x[req[KEY], i, req[SINK]] * self.__data.req_dict[req[SINK], req[SOURCE]]
                * self.__data.connectivity_edges_dict[req[SOURCE], i, req[SINK]]
                for i in
                self.__data.key_index_bs)
                                 == - self.__data.throughput_min_file_dict[req[SOURCE]], 'c6')

    def execute(self, log):
        # self.model.reset()
        self.model.setParam("LogToConsole", log)
        self.model.optimize()

    def result(self):
        if self.model.status == gp.GRB.OPTIMAL:
            print(GREEN + "\nOPTIMAL SOLVE." + RESET)
            obj = self.model.getObjective()
            print(CYAN + "OBJECTIVE FUNCTION: " + RED + str(obj.getValue()) + RESET)
            print(BOLD + "DECISION VARIABLE:" + BOLD)
            for var in self.model.getVars():
                if var.X > 0:
                    print(var.VarName, round(var.X, 2))
        else:
            print(RED + "THE SOLVE IS INFEASIBLE.")

    def solution_path(self, show_path):
        self.__path.clear()
        self.__paths.clear()

        hops = list()
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X != 0:
                    hops.append(self.__get_solution(str(var.VarName)))

        for req in self.__data.requests:
            self.__make_path(hops, req[SOURCE], req[SINK])

        self.__split_paths()

        if show_path:
            for req in range(len(self.__paths)):
                print(REVERSE, "PATH: ", self.__paths[req], RESET)

        return self.__paths

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
            print(k, self.data.size_file_dict[k])
        print()

    def __log_resources_node_dict(self):
        print("TOTAL RESOURCES NODE.")
        for k in self.data.resources_node_dict.keys():
            print(k, self.data.resources_node_dict[k])
        print()

    def __log_phi_node(self):
        print("RESOURCES LOADED PER BASE STATION.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.phi_node[f][i], end=" ")
            print()
        print()

    def __log_phi_node_dict(self):
        print("RESOURCES LOADED PER BASE STATION.")
        for k in self.data.phi_node_dict.keys():
            print(k, self.data.phi_node_dict[k])
        print()

    def __log_throughput_min_dict(self):
        print("MINIMAL THROUGHPUT.")
        for k in self.data.throughput_min_file_dict.keys():
            print(k, self.data.throughput_min_file_dict[k])
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

    def __log_expected_throughput_edge(self):
        print("EXPECTED THROUGHPUT.")
        if self.data.throughput_expected_edge is not None:
            for f, filename in enumerate(self.data.key_index_file):
                print(filename.upper())
                for i in range(len(self.data.key_index_all)):
                    for j in range(len(self.data.key_index_all)):
                        if self.data.throughput_expected_edge[f][i][j] == NO_EDGE:
                            print('ထ', end=" ")
                        else:
                            print(self.data.throughput_expected_edge[f][i][j], end=" ")
                    print()
                print()
        print()

    def __log_expected_throughput_edge_dict(self):
        print("EXPECTED THROUGHPUT.")
        for k in self.data.throughput_expected_edge_dict.keys():
            print(k, self.data.throughput_expected_edge_dict[k])

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

    def __log_current_resources_node(self):
        print("CURRENT RESOURCES.")
        for i in range(len(self.data.key_index_bs)):
            print(self.data.current_resources_node[i])
        print()

    def __log_current_resources_node_dict(self):
        print("CURRENT RESOURCES NODE.")
        for k in self.data.current_resources_node_dict.keys():
            print(k, self.data.current_resources_node_dict[k])
        print()

    def __log_weight_resources(self):
        print("WEIGHT RESOURCES.")
        for i in range(len(self.data.key_index_bs)):
            print(str(self.data.weight_resources[i]).format(), end=" ")
        print()

    def __log_weight_resources_dict(self):
        print("WEIGHT RESOURCES.")
        for k in self.data.weight_resources_dict.keys():
            print(k, self.data.weight_resources_dict[k])
        print()

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
        # self.__log_phi_node()

        self.__log_resources_file_dict()
        self.__log_size_file_dict()
        self.__log_throughput_min_dict()

        self.__log_resources_node_dict()
        self.__log_phi_node_dict()

        self.__log_rtt_min()
        self.__log_rtt_edge()
        # self.__log_rtt_min_dict()
        # self.__log_rtt_edge_dict()
        self.__log_gama_file_node()
        self.__log_e_bs_adj_dict()

    def show_vars_matrix(self):
        print("VARS.\n")
        self.__log_omega_user_node()
        self.__log_expected_throughput_edge()
        self.__log_current_throughput_edge()
        self.__log_diff_throughput_edge()
        self.__log_current_resources_node()
        self.__log_psi_edge()
        self.__log_weight_resources()
        self.__log_weight_network()
        self.__log_connectivity_edges()

    def show_vars_dict(self):
        print("VARS.\n")
        self.__log_omega_user_node_dict()
        self.__log_expected_throughput_edge_dict()
        self.__log_current_throughput_edge_dict()
        self.__log_diff_throughput_edge_dict()
        self.__log_current_resources_node_dict()
        self.__log_psi_edge_dict()
        self.__log_weight_resources_dict()
        self.__log_weight_network_dict()
        self.__log_connectivity_edges_dict()


# This class store all result and plot a graphics.
class PlotData:
    __data = Data()
    set_path = None
    __delay = None
    __events_count = 0
    __req_count = 0

    def __init__(self, data):
        self.__data = data
        self.set_path = pds.DataFrame(columns=['Path', 'Source', 'Sink', 'Delay'])
        self.__delay = pds.DataFrame(columns=['Event', 'Delay'])

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
        with pds.ExcelWriter(path) as writer:
            self.__delay.to_excel(writer, sheet_name='Delay')
            self.set_path.to_excel(writer, sheet_name='Request')
