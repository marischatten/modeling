import sys
from random import randrange
import math

import gurobipy as gp
import time
import numpy as np
# import ortools as otlp  # somente LP
from enum import Enum
import pandas as pds
from utils.utils import *

NO_EDGE = 99999
DELTA = 0.0001
EPSILON = 0.9999

NUM_CLOUD = 1

CURRENT_NODE = 0
NEXT_HOP = 1

CONTENT = 0
HOST = 1

INCREASE = 1
DECREASE = 0

SOURCE = 1
SINK = 2
KEY = 3

MAXIMUM_SBS_PER_UE = 2


# This class changes the type of trials.
class Type(Enum):
    SINGLE = 1
    ZIPF = 2


# This class manages and handles the data of an instance of the problem.
class Data:
    __BREAK = 100

    max_events = 0
    requests = list()
    id_req = 0
    __id_event = 0
    __s = list()
    hops = list()
    hops_with_id = list()
    graph_adj_matrix = None
    req = list()
    req_dict = dict()
    load_links = list()
    reallocation_path = list()
    reallocation_host = list()

    mobility = False
    mobility_rate = 0
    location_ue = None

    # Input
    alpha = 0
    beta = 0
    # Parameters
    num_bs = 0
    num_ue = 0
    num_nodes = 0
    num_files = 0
    num_mbs = 0
    num_sbs = 0

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

    # cs_k \in N
    size_file = list()
    buffer_file = list()
    # thp \in N
    throughput_min_file = list()

    # b \in F
    beta_file = list()
    # bsr_i \in R
    resources_node = list()

    # rtt_ij \in R
    rtt_edge = None
    rtt_min_cloud_mbs = 0
    rtt_min_mbs_mbs = 0
    rtt_min_sbs_mbs = 0
    rtt_min_sbs_ue = 0

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

    load_links_dict = dict()
    throughput_current_edge_dict = dict()
    throughput_diff_edge_dict = dict()

    size_file_dict = dict()
    buffer_file_dict = dict()
    throughput_min_file_dict = dict()

    resources_node_dict = dict()

    gama_file_node_dict = dict()
    omega_user_node_dict = dict()
    e_bs_adj_dict = dict()
    psi_edge_dict = dict()
    rtt_edge_dict = dict()

    distance_ue_dict = dict()

    exponential_scale_rtt = dict()
    total_load_links = dict()

    total_req = 0

    def __init__(self, mobility=None, mr=0,
                 alpha=0, beta=0, num_bs=0, num_ue=0, num_file=0, num_mbs = 0, num_sbs=0,
                 key_f=None, key_i=None, key_u=None,
                 e_bs_adj=None,
                 sf=None, bf=None, thp=None, rt_i=None, rtt_edge=None, radius_mbs=0, radius_sbs=0,
                 gama_file_node=None, dis_ue=None, dis_bs=None, max_event =None, location_ue=None, rtt_min_cloud_mbs=0, rtt_min_mbs_mbs=0, rtt_min_sbs_mbs=0,  rtt_min_sbs_ue=0):

        self.mobility = mobility
        self.mobility_rate = mr
        self.alpha = alpha
        self.beta = beta
        self.num_bs = num_bs + NUM_CLOUD
        self.num_ue = num_ue
        if num_bs != 0 and num_ue != 0:
            self.num_nodes = num_bs + num_ue + NUM_CLOUD
        self.num_files = num_file
        self.num_mbs = num_mbs
        self.num_sbs = num_sbs

        if key_f is not None and key_i is not None and key_u is not None:
            self.key_index_file = key_f
            self.key_index_bs = key_i
            self.key_index_ue = key_u
            self.key_index_with_file = key_i + key_f
            self.key_index_with_ue = key_i + key_u
            self.key_index_all = key_i + key_u + key_f

        self.e_bs_adj = e_bs_adj

        self.size_file = sf
        self.buffer_file = bf
        self.throughput_min_file = thp

        self.resources_node = rt_i

        self.rtt_edge = rtt_edge
        self.radius_mbs = radius_mbs
        self.radius_sbs = radius_sbs
        self.distance_ue = dis_ue
        self.distance_bs = dis_bs
        self.max_events = max_event
        self.location_ue = location_ue
        self.rtt_min_cloud_mbs = rtt_min_cloud_mbs
        self.rtt_min_mbs_mbs = rtt_min_mbs_mbs
        self.rtt_min_sbs_mbs = rtt_min_sbs_mbs
        self.rtt_min_sbs_ue = rtt_min_sbs_ue

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.req = [[0 for f in range(self.num_files)] for u in range(self.num_ue)]
            self.load_links = [[0 for i in range(self.num_nodes + self.num_files)] for j in
                                     range(self.num_nodes + self.num_files)]
            self.gama_file_node = gama_file_node

            self.load_links_to_dictionary()
            self.__size_file_to_dictionary()
            self.__buffer_file_to_dictionary()
            self.__resources_node_to_dictionary()
            self.__throughput_min_file_to_dictionary()
            self.__gama_file_node_to_dictionary()
            self.__e_bs_adj_to_dictionary()
            self.rtt_edge_to_dictionary()
            self.distance_ue_to_dictionary()
            self.req_to_dictionary()
            self.__create_exponential_scale_rtt()

    def __create_exponential_scale_rtt(self):
        init = 1
        scale = list()
        breaks = list(range(0, self.total_req, self.__BREAK))

        for i in range(len(breaks)):
            scale.append(init)
            init = init * 2

        for i in range(len(breaks)):
            tag = breaks[i]
            self.exponential_scale_rtt[tag] = scale[i]

    def clear_hops(self):
        self.hops.clear()

    def clear_hops_with_id(self):
        self.hops_with_id.clear()
        self.clear_dict(self.load_links_dict)

    def insert_requests(self, sources, sinks):
        self.req_dict[sinks[0], sources[0]] = 1
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

    def drop_requests(self, source, sink, key):
        index = 0
        self.req_dict[sink[0], source[0]] = 0
        self.__s.remove(key)
        for r in self.requests:
            if r[KEY] == key:
                index = self.requests.index(r)
                break
        self.requests.pop(index)

    # PARAMETERS TO DICTIONARY
    def __size_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.size_file_dict[tag] = self.size_file[f]

    def __buffer_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.buffer_file_dict[tag] = self.buffer_file[f]

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
        for i in range(len(self.key_index_all)):
            for j in range(len(self.key_index_all)):
                tag_orig = self.key_index_all[i]
                tag_dest = self.key_index_all[j]
                self.rtt_edge_dict[tag_orig, tag_dest] = self.rtt_edge[i][j]

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

    def req_to_dictionary(self):
        for u in range(len(self.key_index_ue)):
            for f in range(len(self.key_index_file)):
                tag_ue = self.key_index_ue[u]
                tag_file = self.key_index_file[f]
                self.req_dict[tag_ue, tag_file] = self.req[u][f]

    def connectivity_edges_to_dictionary(self):
        for c in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[c]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.connectivity_edges_dict[tag_file, tag_orig, tag_dest] = self.connectivity_edges[c][i][j]

    def load_links_to_dictionary(self):
        for i in range(len(self.key_index_all)):
            for j in range(len(self.key_index_all)):
                tag_i = self.key_index_all[i]
                tag_j = self.key_index_all[j]
                self.load_links_dict[tag_i, tag_j] = self.load_links[i][j]

    def set_graph_adj_matrix(self):
        self.graph_adj_matrix = [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in
                                 range(self.num_nodes + self.num_files)]

        for c in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    if (self.weight_network[c][i][j] != NO_EDGE) and (self.graph_adj_matrix[i][j] == NO_EDGE):
                        self.graph_adj_matrix[i][j] = self.weight_network[c][i][j]

    def clear_dict(self, dictionary):
        for k in dictionary.keys():
            dictionary[k] = 0
        return dictionary


# This class handles and calculates the variables and parameters.
class HandleData:
    hosts = None
    paths = None
    __old_hosts = None
    old_paths = None
    __data = Data()
    __counter_requests = list()

    def __init__(self, data):
        self.__data = data

    def calc_vars(self, is_update=False):
        if not is_update:
            self.__calc_omega_user_node()
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

    def __calc_rtt_bs_to_ue_increase(self, bs, ue, rtt_previous):
        rtt = 0
        if self.__is_coverage_bs_to_ue(ue, bs):
            rtt = round(rtt_previous * (1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs)), 4)
        else:
            rtt = NO_EDGE
        if rtt < self.__data.rtt_min_sbs_ue:
            rtt = self.__data.rtt_min_sbs_ue
        return rtt

    def __calc_rtt_bs_to_ue_decrease(self, bs, ue, rtt_previous):
        rtt = 0
        if self.__is_coverage_bs_to_ue(ue, bs):
            rtt = round(rtt_previous / (1 + (self.__data.distance_ue_dict[ue, bs] / self.__data.radius_sbs)), 4)
        else:
            rtt = NO_EDGE
        if rtt < self.__data.rtt_min_sbs_ue:
            rtt = self.__data.rtt_min_sbs_ue
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
                for j, tag_j in enumerate(self.__data.key_index_all):
                    size_f = self.__data.buffer_file[f]
                    if self.__data.rtt_edge_dict is not None:
                        if self.__data.rtt_edge_dict[tag_i,tag_j] == 0:
                            if tag_f == tag_i:
                                self.__data.throughput_current_edge[f][i][j] = NO_EDGE
                        else:
                            self.__data.throughput_current_edge[f][i][j] = round(size_f // self.__data.rtt_edge_dict[tag_i,tag_j],
                                                                                 0)

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
                    if self.__data.throughput_diff_edge[f][i][j] >= (self.__data.throughput_min_file[f] * self.__data.beta):
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
                        if self.__is_coverage_bs_to_ue(tag_j, tag_i):
                            self.__data.weight_network[f][i][j] = self.__weight_network(thp_c, thp_min)

                    if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                        if self.__is_caching(tag_i, tag_j) and (tag_f == tag_i):
                            self.__data.weight_network[f][i][j] = 0

        self.__data.weight_network_to_dictionary()

    def __weight_network(self, thp_c, thp_min):
        if thp_c == 0:
            return NO_EDGE
        if thp_c == NO_EDGE:
            return 0
        return (thp_min / thp_c)

    def __is_caching(self, file, bs):
        return self.__data.gama_file_node_dict[file, bs] == 1

    def __is_coverage_bs_to_bs(self, orig, dest):
        return self.__data.e_bs_adj_dict[orig, dest] == 1

    def __is_coverage_bs_to_ue(self, u, bs):
        return self.__data.omega_user_node_dict[u, bs] == 1

    # This follow method update data of the problem.
    def update_data(self, event, location_fixed):
        if self.__data.mobility:
            self.__update_ue_position(event, location_fixed)
        self.__update_rtt_optic_links()
        self.calc_vars(True)

    def __update_rtt_optic_links(self):
        for i, tag_i in enumerate(self.__data.key_index_all):
            for j, tag_j in enumerate(self.__data.key_index_all):
                if self.__data.rtt_edge_dict[tag_i, tag_j] != NO_EDGE:
                    if tag_i[:4] == "MBS0" and tag_j[:3] == "MBS":
                        self.__calc_rtt_by_load(tag_i,tag_j,self.__data.rtt_min_cloud_mbs)
                    if tag_i[:3] == "MBS" and tag_j[:3] == "MBS":
                        self.__calc_rtt_by_load(tag_i, tag_j, self.__data.rtt_min_mbs_mbs)
                    if (tag_i[:3] == "MBS" and tag_j[:3] == "SBS") or (tag_i[:3] == "SBS" and tag_j[:3] == "MBS"):
                        self.__calc_rtt_by_load(tag_i, tag_j, self.__data.rtt_min_sbs_mbs)

    def __calc_rtt_by_load(self, tag_i,tag_j,rtt_min):
        self.__data.rtt_edge_dict[tag_i, tag_j] = rtt_min * self.__calc_exponential_scale_rtt(self.__data.total_load_links[tag_i, tag_j])

    def __calc_exponential_scale_rtt(self, load):
        scale = 1
        for k in self.__data.exponential_scale_rtt.keys():
            if load < k:
                scale = self.__data.exponential_scale_rtt[k]
                break
        return scale

    def update_counter(self):
        self.__update_counter_requests()
        self.__verify_max_events()

    def insert_counter_requests(self, source, sink, key):
        self.__counter_requests.append([1, source, sink, key])

    def __update_counter_requests(self):
        for i in self.__counter_requests:
            i[0] += 1

    def __verify_max_events(self):
        extract = list()
        for i in self.__counter_requests:
            if i[0] > self.__data.max_events:
                extract.append(i)
                self.__data.drop_requests(i[SOURCE], i[SINK], i[KEY])
        diff = [x for x in self.__counter_requests if x not in extract]
        self.__counter_requests = diff

    def __update_omega_user_node(self, u, tag_i, i, new_dis, rtt_previous):
        if tag_i[:3] == 'MBS':
            # if self.__data.distance_ue[u][i] <= self.__data.radius_mbs: UE não tem cobertura de MBS.
            self.__data.omega_user_node[u][i] = 0
            return rtt_previous
        else:
            if rtt_previous == NO_EDGE:
                if new_dis <= self.__data.radius_sbs:
                    self.__data.omega_user_node[u][i] = 1
                    return self.__data.rtt_min_sbs_ue
                else:
                    self.__data.omega_user_node[u][i] = 0
                    return rtt_previous
            else:
                if new_dis <= self.__data.radius_sbs:
                    self.__data.omega_user_node[u][i] = 1
                    return rtt_previous
                else:
                    self.__data.omega_user_node[u][i] = 0
                    return NO_EDGE

    def __update_ue_position(self, event, location_fixed):
        for u, tag_u in enumerate(self.__data.key_index_ue):

            old_bs, old_rtt = self.get_old_values_ue(tag_u, u)

            for i, tag_i in enumerate(self.__data.key_index_bs):

                new_dis = self.new_distance_ue(event, i, location_fixed, u)

                if new_dis > self.__data.distance_ue[u][i]:
                    rtt_previous = self.__update_omega_user_node(u, tag_i, i, new_dis, self.__data.rtt_edge_dict[tag_i, tag_u])
                    self.__data.omega_user_node_to_dictionary()
                    self.__data.distance_ue[u][i] = new_dis
                    if rtt_previous != NO_EDGE:
                        self.__data.rtt_edge_dict[tag_i,tag_u] = self.__calc_rtt_bs_to_ue_increase(tag_i, tag_u, rtt_previous)
                    else:
                        self.__data.rtt_edge_dict[tag_i, tag_u] = NO_EDGE
                elif new_dis < self.__data.distance_ue[u][i]:
                    rtt_previous = self.__update_omega_user_node(u, tag_i, i, new_dis,self.__data.rtt_edge_dict[tag_i, tag_u])
                    self.__data.omega_user_node_to_dictionary()
                    self.__data.distance_ue[u][i] = new_dis
                    if rtt_previous != NO_EDGE:
                        self.__data.rtt_edge_dict[tag_i,tag_u] = self.__calc_rtt_bs_to_ue_decrease(tag_i, tag_u, rtt_previous)
                    else:
                        self.__data.rtt_edge_dict[tag_i, tag_u] = NO_EDGE

            # Ensure that UE has at last one coverage of SBS.
            self.minimum_coverage(old_bs, old_rtt, tag_u, u)

        # Ensure that a UE doesn't have more than three coverage of SBS.
        self.maximum_coverage()

    def new_distance_ue(self, event, i, location_fixed, u):
        if location_fixed:
            rand_dis = self.__data.location_ue[event][u][i]
        else:
            rand_dis = randrange(-self.__data.mobility_rate, self.__data.mobility_rate + 1)
        new_dis = (rand_dis + self.__data.distance_ue[u][i])
        return new_dis

    def get_old_values_ue(self, tag_u, u):
        old_bs = [(i, tag_i) for i, tag_i in enumerate(self.__data.key_index_bs) if
                  self.__data.omega_user_node[u][i] == 1]
        old_rtt = self.__data.rtt_edge_dict[old_bs[0][1], tag_u]
        return old_bs, old_rtt

    def maximum_coverage(self):
        bound = 0
        for u in range(len(self.__data.key_index_ue)):
            bound = 0
            for i in range(len(self.__data.key_index_bs)):
                if self.__data.omega_user_node[u][i] == 1:
                    bound += 1

            if bound > MAXIMUM_SBS_PER_UE:
                diff = bound - MAXIMUM_SBS_PER_UE
                while diff != 0:
                    k = randrange(0, self.__data.num_bs)
                    if self.__data.omega_user_node[u][k] == 1:
                        self.__data.omega_user_node[u][k] = 0
                        diff -= 1
        self.__data.omega_user_node_to_dictionary()

    def minimum_coverage(self, old_bs, old_rtt, tag_u, u):
        if 1 not in self.__data.omega_user_node[u]:
            self.__data.omega_user_node[u][old_bs[0][0]] = 1
            self.__data.omega_user_node_to_dictionary()
            self.__data.rtt_edge_dict[old_bs[0][1], tag_u] = old_rtt

    def reallocation(self, show_reallocation, event):
        if self.__old_hosts is not None and self.old_paths is not None:
            for op, oh in zip(self.old_paths, self.__old_hosts):
                for np, nh in zip(self.paths[:-1], self.hosts[:-1]):
                    if op[0][:1] == np[0][:1]:
                        if (op[1][2:] != np[1][2:]) and (oh[1] == nh[1]):
                            if show_reallocation:
                                print("SHIFT PATH {0}".format(np[0]))
                            self.__data.reallocation_path.append([event, np[0]])
                    if oh[0] == nh[0]:
                        if oh[1] != nh[1]:
                            if show_reallocation:
                                print("SHIFT HOST [{0}].".format(nh[0]))
                            self.__data.reallocation_host.append([event, nh[0]])

        if self.paths is not None:
            self.__old_hosts = self.hosts.copy()
            self.old_paths = self.paths.copy()


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
        self.__data.__s = self.__data.insert_requests(sources, sinks)

    def run_model(self, show_log, enable_ceil_nodes_capacity):
        # self.model.reset()
        self.create_vars()
        self.__set_function_objective()
        self.__create_constraints(enable_ceil_nodes_capacity)
        self.execute(show_log)
        return self.__data.__s[-1]

    def create_vars(self):
        self.__create_var_flow()
        self.__create_var_host()
        self.__create_var_fit()

    # x_ijk \in R+
    def __create_var_flow(self):
        self.x = self.model.addVars(self.__data.__s, self.__data.key_index_all, self.__data.key_index_all,
                                    vtype=gp.GRB.BINARY, name="flow")

    # y_ik \in R+
    def __create_var_host(self):
        self.y = self.model.addVars(self.__data.__s, self.__data.key_index_bs,
                                    vtype=gp.GRB.BINARY, name="host")

    # This variable this is a logical fit.
    def __create_var_fit(self):
        self.z = self.model.addVars(self.__data.key_index_file, self.__data.key_index_bs,
                                    vtype=gp.GRB.BINARY, name="fit")

    def __set_function_objective(self):
        self.model.setObjective(((gp.quicksum(((self.__data.resources_node_dict[i] -
                                                self.__data.size_file_dict[req[SOURCE]]) *
                                                                   self.__data.req_dict[req[SINK], req[SOURCE]] * (
                                                                   self.y[req[KEY], i])) / ((
                                                                                                        self.__data.resources_node_dict[
                                                                                                            i] *
                                                                                                        self.__data.gama_file_node_dict[
                                                                                                            req[
                                                                                                                SOURCE], i]) + DELTA)
                                                                  for i in self.__data.key_index_bs for req in
                                                                  self.__data.requests)))
                                +
                                ((gp.quicksum(
                                    self.__data.weight_network_dict[req[SOURCE], i, j]
                                    * self.x[req[KEY], i, j]
                                    * self.__data.req_dict[req[SINK], req[SOURCE]]
                                    * self.__data.psi_edge_dict[req[SOURCE], i, j]
                                    * self.__data.connectivity_edges_dict[req[SOURCE], i, j] for j in
                                    self.__data.key_index_all for i in self.__data.key_index_all for req in
                                    self.__data.requests)))
                                , sense=gp.GRB.MINIMIZE)


    def __create_constraints(self, enable_ceil_nodes_capacity):
        # This constraint set y value.
        self.__set_constraint_y_value()

        # This constraint this is a logical fit.
        self.__set_constraints_fit()

        # This constraint limit the use  of node resources.
        if enable_ceil_nodes_capacity:
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
                self.model.addConstr(self.y[req[KEY], i] <= (
                            self.x[req[KEY], req[SOURCE], i] / self.__data.size_file_dict[req[SOURCE]]) + EPSILON,'c1_0')
                self.model.addConstr(
                    self.y[req[KEY], i] >= (self.x[req[KEY], req[SOURCE], i] / self.__data.size_file_dict[req[SOURCE]]), 'c1_1')

    def __set_constraints_fit(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_bs:
                self.model.addConstr(self.z[req[SOURCE], i] <= (self.y.sum(req[KEY], i)/self.__data.size_file_dict[req[SOURCE]] + EPSILON), 'c2_0')
                self.model.addConstr(self.z[req[SOURCE], i] >= (self.y.sum(req[KEY], i)/self.__data.size_file_dict[req[SOURCE]]), 'c2_1')

    def __set_constraint_node_resources_capacity(self):
        for i in self.__data.key_index_bs:
            self.model.addConstr(self.__data.resources_node_dict[i] >= gp.quicksum(
                self.__data.size_file_dict[c] * self.z[c, i] for c in self.__data.key_index_file),'c3')

    def __set_constraint_throughput(self):
        for req in self.__data.requests:
            for i in self.__data.key_index_all:
                for j in self.__data.key_index_all:
                    self.model.addConstr((self.x[req[KEY], i, j] * self.__data.req_dict[req[SINK], req[SOURCE]]) *
                                         self.__data.throughput_min_file_dict[req[SOURCE]]
                                         <= (self.x[req[KEY], i, j] * self.__data.req_dict[req[SINK], req[SOURCE]]) *
                                         self.__data.throughput_current_edge_dict[req[SOURCE], i, j] *
                                         self.__data.connectivity_edges_dict[req[SOURCE], i, j])

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
                                     == 0, 'c5')

    def __set_constraint_flow_conservation_source(self):
        for req in self.__data.requests:
            self.model.addConstr(
                (1) == (
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
                , 'c6')

    def __set_constraint_flow_conservation_sink(self):
        for req in self.__data.requests:
            self.model.addConstr(
                (- 1) == (
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
                , 'c7')

    def execute(self, log):
        self.model.setParam("LogToConsole", log)
        start_time_execution_optimize = time.time()
        self.model.optimize()
        print(CYAN, "EXECUTION OPTIMIZE TIME --- %s seconds ---" % round((time.time() - start_time_execution_optimize), 4), RESET)
        # if self.model.status != gp.GRB.OPTIMAL:
            # self.model.computeIIS()
            #self.model.write("..\\dataset\\model.mps")

    def result(self):
        if self.model.status == gp.GRB.OPTIMAL:
            print(GREEN, "OPTIMAL SOLVE.", RESET)
            obj = self.model.getObjective()
            print(CYAN, "OBJECTIVE FUNCTION: ", RED, str(obj.getValue()), RESET)
            print(BOLD, "DECISION VARIABLE:", BOLD)
            for var in self.model.getVars():
                if var.X != 0:
                    print(var.VarName, round(var.X, 2))
        else:
            print(RED, "THE SOLVE IS INFEASIBLE.")

    def solutions(self, show_path):
        self.__solution_path()
        self.__solution_host()
        if self.__paths is None:
            return (None, None)
        if show_path:
            for r,h in zip(self.__paths,self.__hosts):
                print(REVERSE, " {0} >> PATH: {1} | HOST: {2}".format(r[0][0], r[1], h[1]),
                      RESET)
        return (self.__paths, self.__hosts)

    def __solution_host(self):
        self.__hosts.clear()
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X != 0 and var.VarName[:4] == "host":
                    self.__hosts.append([str(var.VarName).split(',')[0][5:], str(var.VarName).split(',')[1][:-1]])

    def __solution_path(self):
        self.__paths.clear()
        aux = list()
        hops = list()
        key = None
        if self.model.status == gp.GRB.OPTIMAL:
            for var in self.model.getVars():
                if var.X > NO_EDGE:
                    print(REVERSE,"Unexpected error", RESET)
                    sys.exit()
                if var.X != 0 and var.VarName[:4] == "flow":
                    hops.append(self.__get_solution(str(var.VarName)))

            for req in self.__data.requests:
                for h in range(len(hops)):
                    if hops[h][0] == req[KEY]:
                        key = hops[h][:1]
                        aux.append(hops[h][1:])
                        self.__data.hops.append(hops[h][1:])
                        self.__data.hops_with_id.append(hops[h])
                self.__make_path(key, aux, req[SOURCE], req[SINK])

                aux.clear()

    def __get_solution(self, hop):
        next_hop = list()
        hop = hop[5:]
        hop = hop[:-1]
        aux = hop.split(',')
        next_hop.append(aux[0])
        next_hop.append(aux[1])
        next_hop.append(aux[2])
        return next_hop

    def __make_path(self, key, hops, source, sink):
        self.__next_hop(hops, source)
        self.__path.append(sink)
        self.__paths.append([key, self.__path.copy()])
        self.__path.clear()

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
    def __log_rtt_edge_dict(self):
        print("EDGE RTT.")
        for k in self.data.rtt_edge_dict.keys():
            print(k, self.data.rtt_edge_dict[k])
        print()

    def __log_size_file_dict(self):
        print("SIZE FILE.")
        for k in self.data.size_file_dict.keys():
            print(k, self.data.size_file_dict[k], "MB")
        print()

    def __log_buffer_file_dict(self):
        print("BUFFER FILE.")
        for k in self.data.buffer_file_dict.keys():
            print(k, self.data.buffer_file_dict[k], "Mb")
        print()

    def __log_throughput_min_dict(self):
        print("MINIMAL THROUGHPUT.")
        for k in self.data.throughput_min_file_dict.keys():
            print(k, self.data.throughput_min_file_dict[k], "Mb")
        print()

    def __log_resources_node_dict(self):
        print("TOTAL RESOURCES NODE.")
        for k in self.data.resources_node_dict.keys():
            print(k, self.data.resources_node_dict[k])
        print()

    def __log_gama_file_node(self):
        print("FILE CACHING PER BASE STATION(GAMA).")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.gama_file_node[f][i], end=" ")
            print()
        print()

    def __log_gama_file_node_dict(self):
        print("FILE CACHING PER BASE STATION(GAMA).")
        for k in self.data.gama_file_node_dict.keys():
            print(k, self.data.gama_file_node_dict[k])

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

        self.__log_size_file_dict()
        self.__log_buffer_file_dict()
        self.__log_throughput_min_dict()

        self.__log_resources_node_dict()

        self.__log_rtt_edge_dict()
        self.__log_gama_file_node()
        # self.__log_gama_file_node_dict()
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
    __paths = None
    set_paths = list()
    set_hosts = list()
    __all_requests = 0
    __admission_requests = 0
    __rate_admission_requests = 0
    __server_use = dict()
    __all_server_use = None
    __server_use_by_type = None
    __all_links_optic = 0
    __all_links_wireless = 0
    __enabled_links_optic = 0
    __enabled_links_wireless = 0
    __scattering_optic = None
    __scattering_wireless = None
    __load_links_optic = None
    __load_links_wireless = None
    __reallocation_path = None
    __reallocation_host = None
    __poisson = None
    __zipf = None
    __rtt = None

    __hops = None
    __hops_id = None
    __ll = list()
    __load_links_optic_dict = dict()
    __load_links_wireless_dict = dict()

    __delay = None

    def __init__(self, data):
        self.__data = data
        self.__paths = pds.DataFrame(columns=['Event', 'Request', 'Source', 'Sink', 'Path', 'Host'])
        self.__all_server_use = pds.DataFrame(columns=['Event', 'BS', 'Use'])
        self.__server_use_by_type = pds.DataFrame(columns=['Event', 'Cloud','Total_Cloud','Rate_Cloud', 'MBS','Total_MBS','Rate_MBS', 'SBS','Total_SBS','Rate_SBS'])
        self.__scattering_optic = pds.DataFrame(columns=['Event', 'Enabled', 'All', 'Scattering'])
        self.__scattering_wireless = pds.DataFrame(columns=['Event', 'Enabled', 'All', 'Scattering'])
        self.__load_links_optic = pds.DataFrame(columns=['Event', 'Link','Total_Load'])
        self.__load_links_wireless = pds.DataFrame(columns=['Event', 'Link', 'Total_Load'])
        self.__reallocation_path = pds.DataFrame(columns=['Event', 'Request'])
        self.__reallocation_host = pds.DataFrame(columns=['Event', 'Request'])
        self.__poisson = pds.DataFrame(columns=['Qtd_Requests'])
        self.__zipf = pds.DataFrame(columns=['Caches'])
        self.__rtt = pds.DataFrame(columns=['Event','Link','RTT','Throughput'])
        self.__delay = pds.DataFrame(columns=['Event','Request','Delay'])

        self.__load_links_optic_to_dictionary()
        self.__load_links_wireless_to_dictionary()

    def set_distribution(self, bulks, zipf):
        for b in bulks:
            self.__poisson = self.__poisson.append({'Qtd_Requests': b},ignore_index=True)
        for z in zipf:
            self.__zipf = self.__zipf.append({'Caches': z[0]}, ignore_index=True)

    def set_request(self,path,host):
        self.set_paths.append(path)
        self.set_hosts.append(host)

    def set_hops(self, hops, hops_id):
        self.__hops = hops
        self.__hops_id = hops_id

    def insert_req(self, paths, hosts, event):
        for r,h in zip(paths,hosts):
            self.__paths = self.__paths.append(
                {'Event': event, 'Request': r[0], 'Source': r[1][:1], 'Sink': r[1][-1:], 'Path': r[1],
                 'Host': h[1]}, ignore_index=True)

    def calc_rate_admission_requests(self, admission_requests, all_requests):
        self.__admission_requests = admission_requests
        self.__all_requests = all_requests
        self.__rate_admission_requests = admission_requests / all_requests

    def calc_server_use_by_type(self, event, event_null):
        cloud_lst = list()
        mbs_lst = list()
        sbs_lst = list()
        if event_null:
            repeat = self.__server_use_by_type[self.__server_use_by_type['Event'] == (event - 1)]
            cloud = repeat['Cloud'].to_list()
            total_cloud = repeat['Total_Cloud'].to_list()
            rate_cloud = repeat['Rate_Cloud'].to_list()
            mbs = repeat['MBS'].to_list()
            total_mbs = repeat['Total_MBS'].to_list()
            rate_mbs = repeat['Rate_MBS'].to_list()
            sbs = repeat['SBS'].to_list()
            total_sbs = repeat['Total_SBS'].to_list()
            rate_sbs = repeat['Rate_SBS'].to_list()

            for r in range(len(repeat)):
                self.__server_use_by_type = self.__server_use_by_type.append(
                    {'Event': event, 'Cloud': cloud[r], 'Total_Cloud': total_cloud[r], 'Rate_Cloud': rate_cloud[r], 'MBS': mbs[r],
                     'Total_MBS': total_mbs[r], 'Rate_MBS': rate_mbs[r], 'SBS': sbs[r],
                     'Total_SBS': total_sbs[r], 'Rate_SBS': rate_sbs[r]}, ignore_index=True)
        else:
            for k in self.__server_use.keys():
                if self.__server_use[k] != 0:
                    if k[:4] == 'MBS0':
                        cloud_lst.append(k)
                    if k[:3] == 'MBS' and k[:4] != 'MBS0':
                        mbs_lst.append(k)
                    if k[:3] == 'SBS':
                        sbs_lst.append(k)

            cloud_count = len(cloud_lst)
            mbs_count = len(mbs_lst)
            sbs_count = len(sbs_lst)
            self.__server_use_by_type = self.__server_use_by_type.append(
                    {'Event': event, 'Cloud': cloud_count,'Total_Cloud': 1,'Rate_Cloud': cloud_count/1, 'MBS': mbs_count,'Total_MBS': self.__data.num_mbs,'Rate_MBS': mbs_count/self.__data.num_mbs, 'SBS': sbs_count,'Total_SBS': self.__data.num_sbs,'Rate_SBS': sbs_count/self.__data.num_sbs}, ignore_index=True)

    def calc_server_use(self, event, event_null, paths=None, hosts=None):
        if event_null:
            repeat = self.__all_server_use[self.__all_server_use['Event'] == (event - 1)]
            bs = repeat['BS'].to_list()
            use = repeat['Use'].to_list()
            for r in range(len(repeat)):
                self.__all_server_use = self.__all_server_use.append({'Event': event, 'BS': bs[r], 'Use': use[r]}, ignore_index=True)
        else:
            for i in range(len(self.__data.key_index_bs)):
                tag_bs = self.__data.key_index_bs[i]
                self.__server_use[tag_bs] = 0

            server_use_gama_dict = dict()
            for f in range(len(self.__data.key_index_file)):
                for i in range(len(self.__data.key_index_bs)):
                    tag_file = self.__data.key_index_file[f]
                    tag_bs = self.__data.key_index_bs[i]
                    server_use_gama_dict[tag_file, tag_bs] = 0

            for p, h in zip(paths, hosts):
                server_use_gama_dict[p[1][CONTENT],h[1][HOST]] = 1

            for k in server_use_gama_dict.keys():
                if server_use_gama_dict[k] == 1:
                    self.__server_use[k[1]] += self.__data.size_file_dict[k[0]]

            for i in self.__data.key_index_bs:
                rate = round(self.__server_use[i] / self.__data.resources_node_dict[i], 4)

                self.__all_server_use = self.__all_server_use.append(
                    {'Event': event, 'BS': i, 'Use': rate}, ignore_index=True)

            self.__data.clear_dict(server_use_gama_dict)

    def calc_delay_by_request(self,event,event_null, paths=None):
        if event_null:
            pass
        else:
            for r in paths:
                self.__delay = self.__delay.append({'Event': event, 'Request': r[0], 'Delay': self.__sum_rtt(r[1])}, ignore_index=True)

    def __sum_rtt(self, path):
        rtt = 0
        for i, j in zip(path[1:], path[2:]):
            rtt += self.__data.rtt_edge_dict[i, j]
        return rtt

    def __calc_all_links(self):
        self.__calc_all_links_optic()
        self.__calc_all_links_wireless()

    def __calc_all_links_optic(self):
        self.__all_links_optic = 0
        for i in range(len(self.__data.key_index_bs)):
            self.__all_links_optic += sum(self.__data.e_bs_adj[i])

    def __calc_all_links_wireless(self):
        self.__all_links_wireless = 0
        for i in range(len(self.__data.key_index_ue)):
            self.__all_links_wireless += sum(self.__data.omega_user_node[i])

    def __calc_enabled_links(self):
        self.__calc_enabled_links_optic()
        self.__calc_enabled_links_wireless()

    def __calc_enabled_links_optic(self):
        df = pds.DataFrame(columns=['hop1', 'hop2'])
        for i in range(len(self.__hops)):
            if ((self.__hops[i][0][:2] != 'UE') and (self.__hops[i][0][:1] != 'F')) and ((self.__hops[i][1][:2] != 'UE') and (self.__hops[i][1][:1] != 'F')):
                df = df.append({'hop1': self.__hops[i][0], 'hop2': self.__hops[i][1]}, ignore_index=True)
        df = df.drop_duplicates()
        h = df.values.tolist()
        self.__enabled_links_optic = len(h)

    def __calc_enabled_links_wireless(self):
        df = pds.DataFrame(columns=['hop1', 'hop2'])
        for i in range(len(self.__hops)):
            if ((self.__hops[i][0][:1] != 'F')) and (self.__hops[i][1][:3] != 'SBS') and (self.__hops[i][1][:3] != 'MBS'):
                df = df.append({'hop1': self.__hops[i][0], 'hop2': self.__hops[i][1]}, ignore_index=True)
        df = df.drop_duplicates()
        h = df.values.tolist()
        self.__enabled_links_wireless = len(h)

    def calc_scattering(self, event, event_null):
        self.__calc_all_links()
        if not event_null:
            self.__calc_enabled_links()

        scattering_optic = self.__enabled_links_optic / self.__all_links_optic
        scattering_wireless = self.__enabled_links_wireless / self.__all_links_wireless

        self.__scattering_optic = self.__scattering_optic.append(
            {'Event': event, 'Enabled': self.__enabled_links_optic, 'All': self.__all_links_optic, 'Scattering': scattering_optic},
            ignore_index=True)
        self.__scattering_wireless = self.__scattering_wireless.append(
            {'Event': event, 'Enabled': self.__enabled_links_wireless, 'All': self.__all_links_wireless, 'Scattering': scattering_wireless},
            ignore_index=True)
        self.clear_hops()

    def calc_load_link(self, event, event_null):
        if event_null:
            self.__set_load_event_null_optic(event)
            self.__set_load_event_null_wireless(event)
        else:
            self.__calc_load_link_optic(event)
            self.__calc_load_link_wireless(event)
            if self.__enabled_links_optic == 0:
                self.__set_load_event_null_optic(event)
            if self.__enabled_links_wireless == 0:
                self.__set_load_event_null_wireless(event)

        self.clear_hops_with_id()

    def __set_load_event_null_optic(self, event):
        repeat_optic = self.__load_links_optic[self.__load_links_optic['Event'] == (event - 1)]
        link = repeat_optic['Link'].to_list()
        load = repeat_optic['Total_Load'].to_list()
        for r in range(len(repeat_optic)):
            self.__load_links_optic = self.__load_links_optic.append(
                {'Event': event, 'Link': link[r], 'Total_Load': load[r]}, ignore_index=True)

    def __set_load_event_null_wireless(self, event):
        repeat_wireless = self.__load_links_wireless[self.__load_links_wireless['Event'] == (event - 1)]
        link = repeat_wireless['Link'].to_list()
        load = repeat_wireless['Total_Load'].to_list()
        for r in range(len(repeat_wireless)):
            self.__load_links_wireless = self.__load_links_wireless.append(
                {'Event': event, 'Link': link[r], 'Total_Load': load[r]}, ignore_index=True)

    def __calc_load_link_optic(self, event):
        for req in self.__data.requests:
            for h in self.__hops_id:
                if req[KEY] == h[0]:
                    if ((h[1][:2] != 'UE') and (h[1][:1] != 'F')) and ((h[2][:2] != 'UE') and (h[2][:1] != 'F')):
                        buffer = self.__data.buffer_file_dict[req[SOURCE]]
                        self.__load_links_optic_dict[h[1], h[2]] += buffer

        for k in self.__load_links_optic_dict.keys():
            if self.__load_links_optic_dict[k] != 0:
                self.__load_links_optic = self.__load_links_optic.append(
                    {'Event': event, 'Link': k, 'Total_Load': self.__load_links_optic_dict[k]}, ignore_index=True)

        # Warning: execute when the configuration save data is enabled.
        self.__set_load_to_calc_rtt()

    def __set_load_to_calc_rtt(self):
        self.__data.total_load_links = self.__load_links_optic_dict.copy()

    def __calc_load_link_wireless(self, event):
        for req in self.__data.requests:
            for h in self.__hops_id:
                if req[KEY] == h[0]:
                     if (h[1][:1] != 'F') and (h[2][:3] != 'SBS') and (h[2][:3] != 'MBS'):
                        buffer = self.__data.buffer_file_dict[req[SOURCE]]
                        self.__load_links_wireless_dict[h[1], h[2]] += buffer

        for k in self.__load_links_wireless_dict.keys():
            if self.__load_links_wireless_dict[k] != 0:
                self.__load_links_wireless = self.__load_links_wireless.append(
                    {'Event': event, 'Link': k, 'Total_Load': self.__load_links_wireless_dict[k]}, ignore_index=True)

    def calc_reallocation(self, event, event_null):
        self.__calc_reallocation_path(event, event_null)
        self.__calc_reallocation_host(event, event_null)

    def __calc_reallocation_path(self, event, event_null):
        if (event_null) or (len(self.__data.reallocation_path) == 0):
            self.__reallocation_path = self.__reallocation_path.append({'Event': event, 'Request': None}, ignore_index=True)
        else:
            for i in self.__data.reallocation_path:
                self.__reallocation_path = self.__reallocation_path.append({'Event': event, 'Request': i[1]}, ignore_index=True)
            self.__data.reallocation_path.clear()

    def __calc_reallocation_host(self, event, event_null):
        if (event_null) or (len(self.__data.reallocation_host) == 0):
            self.__reallocation_host = self.__reallocation_host.append({'Event': event, 'Request': None}, ignore_index=True)
        else:
            for i in self.__data.reallocation_host:
                self.__reallocation_host = self.__reallocation_host.append({'Event': event, 'Request': i[1]}, ignore_index=True)
            self.__data.reallocation_host.clear()

    def rtt_to_dataframe(self, event):
        for (key,value) in self.__data.rtt_edge_dict.items():
            if value != NO_EDGE and value != 0:
                if (key[1][:3] != 'SBS') and (key[1][:3] != 'MBS'):
                    # WARNING correct throughput only for cache with same buffer size
                    self.__rtt = self.__rtt.append({'Event': event, 'Link': key, 'RTT': value, 'Throughput': round(self.__data.buffer_file[0]/value,0)}, ignore_index=True)

    def save_data(self, path):
        dt_rate_admission = pds.DataFrame(
            {'Rate_Admission': [self.__rate_admission_requests], 'Admission_Requests': [self.__admission_requests],
             'All_Requests': [self.__all_requests]})
        with pds.ExcelWriter(path) as writer:
            self.__paths.to_excel(writer, sheet_name='Requests')
            dt_rate_admission.to_excel(writer, sheet_name='Rate_Admission')
            self.__all_server_use.to_excel(writer, sheet_name='Server_Use')
            self.__server_use_by_type.to_excel(writer, sheet_name='Server_Use_By_Type')
            self.__scattering_optic.to_excel(writer, sheet_name='Scattering_Optic')
            self.__scattering_wireless.to_excel(writer, sheet_name='Scattering_Wireless')
            self.__load_links_optic.to_excel(writer,sheet_name='Load_Links_Optic')
            self.__load_links_wireless.to_excel(writer, sheet_name='Load_Links_Wireless')
            self.__reallocation_path.to_excel(writer, sheet_name='Paths_Reallocation')
            self.__reallocation_host.to_excel(writer, sheet_name='Hosts_Reallocation')
            self.__poisson.to_excel(writer, sheet_name='Poisson')
            self.__zipf.to_excel(writer, sheet_name='Zipf')
            self.__rtt.to_excel(writer, sheet_name='RTT')
            self.__delay.to_excel(writer, sheet_name='Delay')

    def __load_links_optic_to_dictionary(self):
        self.__ll = [[0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
                     range(self.__data.num_nodes + self.__data.num_files)]
        for i in range(len(self.__data.key_index_all)):
            for j in range(len(self.__data.key_index_all)):
                tag_i = self.__data.key_index_all[i]
                tag_j = self.__data.key_index_all[j]
                self.__load_links_optic_dict[tag_i, tag_j] = self.__ll[i][j]

    def __load_links_wireless_to_dictionary(self):
        self.__ll = [[0 for i in range(self.__data.num_nodes + self.__data.num_files)] for j in
                     range(self.__data.num_nodes + self.__data.num_files)]
        for i in range(len(self.__data.key_index_all)):
            for j in range(len(self.__data.key_index_all)):
                tag_i = self.__data.key_index_all[i]
                tag_j = self.__data.key_index_all[j]
                self.__load_links_wireless_dict[tag_i, tag_j] = self.__ll[i][j]

    def clear_hops(self):
        self.__hops.clear()

    def clear_hops_with_id(self):
        self.__hops_id.clear()
        self.__data.clear_dict(self.__load_links_optic_dict)
        self.__data.clear_dict(self.__load_links_wireless_dict)