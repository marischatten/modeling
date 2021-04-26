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

NO_EDGE = 99999

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
    POISSON = 2
    ZIPF = 3
    ALLTOALL = 4
    RANDOM = 5


class Mobility(Enum):
    IS_MOBILE = 1
    NON_MOBILE = 0


class Model(Enum):
    ONLINE = 1
    OFFLINE = 0


# This class manages and handles the data of an instance of the problem.
class Data:

    sources = list()
    sinks = list()

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
    weight_file_edge = None

    weight_dict = dict()
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

    def __init__(self, mobility: object = Mobility.NON_MOBILE, mr=0, alpha=0, beta=0, num_bs=0, num_ue=0, num_file=0, key_f=None, key_i=None, key_u=None,
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
            self.throughput_current_edge = [
                [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in
                 range(self.num_nodes + self.num_files)]
                for f
                in
                range(self.num_files)]
            self.current_resources_node = [0 for i in range(self.num_nodes)]

            self.throughput_expected_edge = [
                [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in
                 range(self.num_nodes + self.num_files)]
                for f
                in
                range(self.num_files)]

            self.throughput_diff_edge = [
                [[0.0 for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f in
                range(self.num_files)]

            self.weight_file_edge = [
                [[0.0 for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f in
                range(self.num_files)]

            self.psi_edge = [
                [[0 for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f in
                range(self.num_files)]

            self.omega_user_node = [[0 for i in range(self.num_bs)] for u in range(self.num_ue)]

            self.gama_file_node = gama_file_node

            self.weight_to_dictionary()
            self.__resources_file_to_dictionary()
            self.__size_file_to_dictionary()
            self.__resources_node_to_dictionary()
            self.phi_node_to_dictionary()
            self.__throughput_min_file_to_dictionary()
            self.__gama_file_node_to_dictionary()
            self.__e_bs_adj_to_dictionary()
            self.rtt_min_to_dictionary()
            self.distance_ue_to_dictionary()

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
                    self.throughput_current_edge_dict[tag_file, tag_orig, tag_dest] = self.throughput_current_edge[f][i][
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

    def weight_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.weight_dict[tag_file, tag_orig, tag_dest] = self.weight_file_edge[f][i][j]

    def psi_edge_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.psi_edge_dict[tag_file, tag_orig, tag_dest] = self.psi_edge[f][i][j]


# This class handles and calculates the variables and parameters.
class HandleData:
    path = None

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
        self.__calc_weight_file_edge()

    def __calc_omega_user_node(self):

        for u in range(len(self.__data.key_index_ue)):
            for i,tag_i in enumerate(self.__data.key_index_bs):
                if tag_i[:3] == 'MBS':
                    # if self.__data.distance_ue[u][i] <= self.__data.radius_mbs: UE não tem cobertura de MBS.
                    self.__data.omega_user_node[u][i] = 0
                else:
                    if self.__data.distance_ue[u][i] <= self.__data.radius_sbs:
                        self.__data.omega_user_node[u][i] = 1

        self.__data.omega_user_node_to_dictionary()

    def __generate_rtt(self):
        self.__data.rtt_edge = [[0.0 for i in range(self.__data.num_nodes)] for j in range(self.__data.num_nodes)]
        for i in range(len(self.__data.key_index_with_ue)):
            for j in range(len(self.__data.key_index_with_ue)):
                if i == j:
                    self.__data.rtt_edge[i][j] = NO_EDGE

        self.__generate_rtt_bs_to_bs()
        self.__generate_rtt_bs_to_ue()
        self.__data.rtt_edge_to_dictionary()

    def __generate_rtt_bs_to_bs(self):
        for i, tag_i in enumerate(self.__data.key_index_bs):
            for j, tag_j in enumerate(self.__data.key_index_bs):
                if self.__data.e_bs_adj[i][j] == 1:
                    self.__data.rtt_edge[i][j] = self.__data.rtt_min[i][j]
                else:
                    self.__data.rtt_edge[i][j] = NO_EDGE

    def __generate_rtt_bs_to_ue(self):
        for i, tag_i in enumerate(self.__data.key_index_with_ue):
            for j, tag_j in enumerate(self.__data.key_index_with_ue):
                if self.__data.rtt_edge[i][j] == 0.0 and self.__data.rtt_edge[i][j] != NO_EDGE:
                    rtt = self.__calc_rtt_bs_to_ue(tag_i, i, tag_j, j, self.__data.rtt_min[i][j])
                    self.__data.rtt_edge[i][j] = self.__data.rtt_edge[j][i] = round(rtt, 2)

    def __calc_rtt_bs_to_ue(self, tag_i, i, tag_j, j, rtt_min):
        rtt = 0
        if self.__data.rtt_edge[i][j] == 0.0 and self.__data.rtt_edge[i][j] != NO_EDGE:
            if tag_i[:2] != tag_j[:2]:
                if tag_i[:2] == 'UE':
                    ue = tag_i
                    bs = tag_j
                    if self.__data.omega_user_node_dict[ue, bs] == 1:
                        rtt = rtt_min * (1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs))
                    else:
                        rtt = NO_EDGE
                if tag_j[:2] == 'UE':
                    ue = tag_j
                    bs = tag_i
                    if self.__data.omega_user_node_dict[ue, bs] == 1:
                        rtt = rtt_min * (1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs))
                    else:
                        rtt = NO_EDGE
            else:
                rtt = NO_EDGE
        return rtt

    def __calc_current_throughput_edge(self):
        rtt_ij = 0
        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_with_ue)):
                for j in range(len(self.__data.key_index_with_ue)):
                    size_f = self.__data.size_file[f]
                    if self.__data.rtt_edge is not None:
                        rtt_ij = self.__data.rtt_edge[i][j]
                    if rtt_ij != NO_EDGE:
                        self.__data.throughput_current_edge[f][i][j] = round(size_f // rtt_ij, 2)
                    else:
                        self.__data.throughput_current_edge[f][i][j] = NO_EDGE

        self.__data.throughput_current_to_dictionary()

    def __calc_expected_throughput_edge(self):
        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_with_ue)):
                for j in range(len(self.__data.key_index_with_ue)):
                    size_f = self.__data.size_file[f]
                    if self.__data.rtt_min[i][j] != NO_EDGE:
                        self.__data.throughput_expected_edge[f][i][j] = round(size_f // self.__data.rtt_min[i][j], 2)
                    else:
                        self.__data.throughput_expected_edge[f][i][j] = NO_EDGE
        self.__data.throughput_expected_to_dictionary()

    def __calc_diff_throughput(self):
        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_with_ue)):
                for j in range(len(self.__data.key_index_with_ue)):
                    self.__data.throughput_diff_edge[f][i][j] = round(
                        self.__data.throughput_expected_edge[f][i][j] - self.__data.throughput_current_edge[f][i][j], 2)
        self.__data.throughput_diff_to_dictionary()

    def __calc_current_resources_node(self):
        for i in range(len(self.__data.key_index_bs)):
            file = 0
            for f in range(len(self.__data.key_index_file)):
                if self.__data.gama_file_node[f][i] == 1 and self.__data.phi_node[f][i] != 0:
                    file += self.__data.gama_file_node[f][i] * self.__data.resources_file[f] * self.__data.phi_node[f][
                        i]
            self.__data.current_resources_node[i] = file
        self.__data.current_resources_node_to_dictionary()

    def __calc_weight_file_edge(self):
        global NO_EDGE
        for f, filename in enumerate(self.__data.key_index_file):
            for i, orig_name in enumerate(self.__data.key_index_all):
                for j, dest_name in enumerate(self.__data.key_index_all):
                    if i == j:  # Origem e destino não podem ser iguais.
                        self.__data.weight_file_edge[f][i][j] = NO_EDGE
                    elif self.__is_ue(orig_name) or self.__is_content(orig_name):  # UE ou F
                        if self.__is_ue(orig_name):  # Não existe aresta saindo de UE.
                            self.__data.weight_file_edge[f][i][j] = NO_EDGE
                        elif self.__is_content_to_bs(
                                dest_name):  # O custo de F para BS é sempre 0. Se o Gama entre BS e F são iguais a 1.
                            if self.__is_caching(orig_name, dest_name):  # #BS não armazena F.
                                self.__data.weight_file_edge[f][i][j] = 0.0
                            else:  # BS armazena F.
                                self.__data.weight_file_edge[f][i][j] = NO_EDGE
                        else:  # F para UE.
                            self.__data.weight_file_edge[f][i][j] = NO_EDGE  # Não existe aresta entre F e UE.
                    else:  # BS
                        if self.__is_bs_to_content(dest_name):  # Não existe aresta com origem em BS para F.
                            self.__data.weight_file_edge[f][i][j] = NO_EDGE
                        else:  # BS para UE
                            if self.__is_coverage(orig_name,
                                                  dest_name):  # Existe aresta de origem em BS para o destino UE ou origem em BS para o destino BS.
                                rt_i = self.__data.resources_node[i]
                                rr_i = self.__data.current_resources_node[i]
                                bwc_fij = self.__data.throughput_current_edge[f][i][j]
                                bwe_fij = self.__data.throughput_expected_edge[f][i][j]
                                weight = self.__calc_weight(rr_i, rt_i, bwc_fij, bwe_fij)
                                self.__data.weight_file_edge[f][i][j] = round(weight, 4)
                            else:  # Não existe aresta de origem em BS parao destino UE.
                                self.__data.weight_file_edge[f][i][j] = NO_EDGE
        self.__data.weight_to_dictionary()

    def __calc_psi_edge(self):
        for f in range(len(self.__data.key_index_file)):
            for i in range(len(self.__data.key_index_all)):
                for j in range(len(self.__data.key_index_all)):
                    if self.__data.throughput_diff_edge[f][i][j] >= self.__data.beta:
                        self.__data.psi_edge[f][i][j] = 1
        self.__data.psi_edge_to_dictionary()

    def __calc_weight(self, rr_i, rt_i, bwc_fij, bwe_fij):
        return (self.__data.alpha * (rr_i / rt_i)) + ((1 - self.__data.alpha) * (bwc_fij / bwe_fij))

    def __is_caching(self, file, bs):
        return self.__data.gama_file_node_dict[file, bs] == 1

    def __is_coverage(self, orig, dest):
        if self.__is_ue(dest):
            return self.__is_coverage_bs_to_ue(orig, dest)
        else:
            return self.__is_coverage_bs_to_bs(orig, dest)

    def __is_ue(self, name):
        return name in self.__data.key_index_ue

    def __is_content(self, name):
        return name in self.__data.key_index_file

    def __is_content_to_bs(self, dest):
        return dest in self.__data.key_index_bs

    def __is_bs_to_content(self, dest):
        return dest in self.__data.key_index_file

    def __is_coverage_bs_to_bs(self, orig, dest):
        return self.__data.e_bs_adj_dict[orig, dest] == 1

    def __is_coverage_bs_to_ue(self, orig, dest):
        return self.__data.omega_user_node_dict[dest, orig] == 1

    # This method update data of the problem.
    def update_data(self):
        if self.__data.mobility.IS_MOBILE:
            self.__update_ue_position()
        self.__update_rtt_min()
        self.__update_rtt()
        self.__update_phi_node()
        self.calc_vars(True)

    def __update_rtt_min(self):
        for i in range(len(self.__data.key_index_with_ue)):
            for j in range(len(self.__data.key_index_with_ue)):
                if self.__data.rtt_edge[i][j] <= self.__data.rtt_min[i][j]:
                    self.__data.rtt_min[i][j] = self.__data.rtt_edge[i][j]
        self.__data.rtt_min_to_dictionary()

    def __update_rtt(self):

        for i in range(len(self.__data.key_index_with_ue)):
            for j in range(len(self.__data.key_index_with_ue)):
                if self.__data.rtt_edge[i][j] != NO_EDGE:
                    if random.uniform(0, 1) == INCREASE:
                        print("increase")
                        self.__data.rtt_edge[i][j] += randrange(1, 10)
                    if random.uniform(0, 1) == DECREASE:
                        print("decrease")
                        self.__data.rtt_edge[i][j] = abs(self.__data.rtt_edge[i][j] - randrange(1, 10))
        self.__data.rtt_edge_to_dictionary()

    def __update_phi_node(self):
        for i, file in enumerate(self.__data.key_index_file):
            for j, bs in enumerate(self.__data.key_index_bs):
                if file == self.path[CONTENT] and bs == self.path[STORE]:
                    self.__data.phi_node[i][j] += 1
        self.__data.phi_node_to_dictionary()

    def __update_ue_position(self):
        for u in range(len(self.__data.key_index_ue)):
            for i in range(len(self.__data.key_index_bs)):
                self.__data.distance_ue[u][i] += np.random.normal(-self.__data.mobility_rate, self.__data.mobility_rate, 1)


# This class execute the optimization model.
class OptimizeData:
    __data = Data()

    model = None
    x = None
    s = ""
    t = ""
    __path = list()

    def __init__(self, data, source, sink):
        self.data = data
        self.s = source
        self.t = sink

    def run_model(self):
        pass

    # n_fij \in {0,1}
    def create_vars(self):
        self.x = self.model.addVars(self.s, self.data.key_index_all, self.data.key_index_all,
                                    vtype=gp.GRB.SEMICONT, name="flow")

    def set_function_objective(self):
        self.model.setObjective(
            gp.quicksum(self.x[f, i, j] * self.data.weight_dict[f, i, j] for f in self.s for i in
                        self.data.key_index_all for j in self.data.key_index_all),
            sense=gp.GRB.MINIMIZE)

    def create_model_in_ortools(self):
        pass

    def create_constraints(self):
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
        self.model.addConstrs(self.data.resources_node_dict[i] * self.x[s, s, i]
                              >= (self.data.current_resources_node_dict[i] + self.data.resources_file_dict[s]) * self.x[
                                  s, s, i] for f in self.data.key_index_file for s in self.s for i in
                              self.data.key_index_bs)

    def __set_constraint_throughput(self):
        self.model.addConstrs(self.data.throughput_expected_edge_dict[f, i, j] * self.x[f, i, j]
                              >= self.data.throughput_current_edge_dict[f, i, j] * self.x[f, i, j] for f in
                              self.s for i in self.data.key_index_all for j in
                              self.data.key_index_all)

    def __set_constraint_flow_conservation(self):
        for f in self.s:
            for i in self.data.key_index_all:
                if all(i != s for s in self.s) and all(i != t for t in self.t):
                    # if i != self.s and i != self.t:
                    self.model.addConstr(gp.quicksum(self.x[f, i, j] for j in self.data.key_index_all)
                                         - gp.quicksum(self.x[f, j, i] for j in self.data.key_index_all)
                                         == 0, 'c4')

    def __set_constraint_flow_conservation_source(self):
        for f in self.s:
            self.model.addConstr(gp.quicksum(self.x[f, s, i] for s in self.s for i in self.data.key_index_bs)
                                 - gp.quicksum(self.x[f, i, s] for s in self.s for i in self.data.key_index_bs)
                                 == self.data.throughput_min_file_dict[f], 'c5')

    def __set_constraint_flow_conservation_sink(self):
        for f in self.s:
            self.model.addConstr(gp.quicksum(self.x[f, t, i] for t in self.t for i in self.data.key_index_bs)
                                 - gp.quicksum(self.x[f, i, t] for t in self.t for i in self.data.key_index_bs)
                                 == - self.data.throughput_min_file_dict[f], 'c6')

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
                if var.X != 0:
                    print(var.VarName, round(var.X, 2))
        else:
            print(RED + "THE SOLVE IS INFEASIBLE.")

    def solution_path(self, show_path):
        self.__path.clear()
        hops = list()
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X != 0:
                    hops.append(self.__get_solution(str(var.VarName)))

        self.__make_path(hops, self.s[0], self.t[0])
        if show_path:
            print(REVERSE, "PATH: ", self.__path, RESET)
        return self.__path

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


# This class show data in parameters and vars.
class LogData:
    data = Data()

    def __init__(self, data):
        self.data = data

    # PARAMETERS
    def __log_rtt_edge(self):
        print("EDGE RTT.")
        for i in range(len(self.data.key_index_with_ue)):
            for j in range(len(self.data.key_index_with_ue)):
                print(self.data.rtt_edge[i][j], end=" ")
            print()
        print()

    def __log_rtt_edge_dict(self):
        print("EDGE RTT.")
        for k in self.data.rtt_edge_dict.keys():
            print(k, self.data.rtt_edge_dict[k])
        print()

    def __log_resources_file_dict(self):
        print("SIZE FILE.")
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
        print("BASE RTT.")
        for i in range(len(self.data.key_index_with_ue)):
            for j in range(len(self.data.key_index_with_ue)):
                print(self.data.rtt_min[i][j], end=" ")
            print()
        print()

    def __log_rtt_min_dict(self):
        print("BASE RTT.")
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

    def __log_weight_file_edge(self):
        print("WEIGHT.")
        for f, filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(str(self.data.weight_file_edge[f][i][j]).format(), end=" ")
                print()
            print()
        print()

    def __log_weight_dict(self):
        print("WEIGHT.")
        for k in self.data.weight_dict.keys():
            print(k, self.data.weight_dict[k])
        print()

    def show_parameters(self):
        print("PARAMETERS.\n")
        self.__log_phi_node()

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
        self.__log_weight_file_edge()

    def show_vars_dict(self):
        print("VARS.\n")
        self.__log_omega_user_node_dict()
        self.__log_expected_throughput_edge_dict()
        self.__log_current_throughput_edge_dict()
        self.__log_diff_throughput_edge_dict()
        self.__log_current_resources_node_dict()
        self.__log_psi_edge_dict()
        self.__log_weight_dict()


# This class store all result and plot a graphics.
class PlotData:
    __data = Data()
    __set_path = None
    __delay = None
    __events_count = 0

    def __init__(self, data):
        self.__data = data
        self.__set_path = pds.DataFrame(columns=['Path', 'Delay'])
        self.__delay = pds.DataFrame(columns=['Event', 'Delay'])

    def insert_path(self, path, event):
        self.__events_count = event
        self.__set_path = self.__set_path.append({'Path': path.copy(), 'Delay': self.__sum_rtt(path)},
                                                 ignore_index=True)
        self.__upload_delay()

    def __sum_rtt(self, path):
        rtt = 0
        for i, j in zip(path[1:], path[2:]):
            if self.__data.rtt_edge_dict[i, j] >= NO_EDGE:
                continue
            rtt += self.__data.rtt_edge_dict[i, j]
        return rtt

    def show_paths(self):
        print("SET PATH.")
        print(self.__set_path)
        print(self.__delay)

    def __upload_delay(self):
        for i, row in self.__set_path.iterrows():
            self.__delay = self.__delay.append(
                {'Id': i, 'Event': self.__events_count, 'Delay': self.__sum_rtt(row['Path'])}, ignore_index=True)
            self.__set_path._set_value(i, 'Delay', self.__sum_rtt(row['Path']))

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
            self.__set_path.to_excel(writer, sheet_name='Request')
