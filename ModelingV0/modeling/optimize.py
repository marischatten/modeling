import gurobipy as gp
import statistics as s
import numpy as np

NO_EDGE = 9999


class Data:
    # Input
    alpha = 0

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
    key_index_orig = list()
    key_index_dest = list()

    # fs \in R
    size_file = list()
    # fr \in R
    resources_file = list()
    # fbw \in R
    bandwidth_min_file = list()

    # rt_i \in R
    resources_node = list()

    # fu \in {0,1}
    file_user_request = None

    # rtt_ij \in R
    rtt_edge = None
    # bwt_ij \in R
    total_bandwidth_edge = None

    # Vars
    # bwa_ij \in R
    bandwidth_actual_edge = None

    # mf_i \in {0,1}
    map_node_file = None

    # rr_i \in R
    actual_resources_node = list()

    # c_fij \in R
    weight_file_edge = None

    weight_dict = dict()

    def __init__(self, alpha=0, num_bs=0, num_ue=0, num_file=0, key1=None, key2=None, key3=None, fs=None,
                 fr=None, bwf=None, rt_i=None, fu=None, bwt_ij=None, avg_rtt=0,
                 sd_rtt=0, map_node_file=None):

        self.alpha = alpha
        self.num_bs = num_bs
        self.num_ue = num_ue
        if num_bs != 0 and num_ue != 0:
            self.num_nodes = num_bs + num_ue
        self.num_files = num_file
        self.key_index_file = key1
        self.key_index_bs = key2
        self.key_index_ue = key3
        if key2 is not None and key3 is not None:
            self.key_index_orig = self.key_index_dest = key2 + key3
        self.size_file = fs
        self.resources_file = fr
        self.bandwidth_min_file = bwf
        self.resources_node = rt_i
        self.file_user_request = fu

        self.total_bandwidth_edge = bwt_ij

        self.map_node_file = map_node_file

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.generate_rtt(avg_rtt, sd_rtt)

            self.bandwidth_actual_edge = [[[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f in
                                          range(self.num_files)]
            self.actual_resources_node = [0 for i in range(self.num_nodes)]
            self.weight_file_edge = [[[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f in
                                     range(self.num_files)]
            self.weight_to_dictionary()

    def weight_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                for j in range(len(self.key_index_dest)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_orig[i]
                    tag_dest = self.key_index_dest[j]
                    self.weight_dict[tag_file, tag_orig, tag_dest] = self.weight_file_edge[f][i][j]

    def generate_rtt(self, avg, sd):
        self.rtt_edge = [[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)]
        for i in range(len(self.key_index_orig)):
            for j in range(len(self.key_index_dest)):
                if i != j:
                    rtt = s.NormalDist(avg, sd).samples(1, seed=None)
                    self.rtt_edge[i][j] = round(rtt[0], 2)
                else:
                    self.rtt_edge[i][j] = NO_EDGE


class HandleData:
    data = Data()

    def __init__(self, data):
        self.data = data

    def calc_bandwidth_actual_edge(self):
        rtt_ij = 0
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    size_f = self.data.size_file[f]
                    if self.data.rtt_edge is not None:
                        rtt_ij = self.data.rtt_edge[i][j]
                    self.data.bandwidth_actual_edge[f][i][j] = round(size_f / rtt_ij, 2)

    def replace_map_file(self, file, orig, dest):
        self.data.map_node_file[file][orig] = 0
        self.data.map_node_file[file][dest] = 1

    def calc_actual_resources_node(self):
        sum_users = 0
        by_file = 0
        for i in range(len(self.data.key_index_orig)):
            for f in range(len(self.data.key_index_file)):
                if self.data.map_node_file[f][i] == 1:
                    for u in range(len(self.data.key_index_orig)):
                        sum_users += self.data.file_user_request[f][u]
                    by_file += sum_users * self.data.resources_file[f]
                    sum_users = 0
            self.data.actual_resources_node[i] = by_file
            by_file = 0

    def calc_weight_file_edge(self):
        global NO_EDGE
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    rt_i = self.data.resources_node[i]
                    rr_i = self.data.actual_resources_node[i]
                    bwa_fij = self.data.bandwidth_actual_edge[f][i][j]
                    bwt_ij = self.data.total_bandwidth_edge[i][j]
                    if rt_i != 0 and bwt_ij != 0 and bwt_ij != NO_EDGE:
                        weight = ((self.data.alpha * (rr_i / rt_i)) + ((1 - self.data.alpha) * (bwa_fij / bwt_ij))) / (
                                self.data.alpha + (1.0 - self.data.alpha))
                        self.data.weight_file_edge[f][i][j] = round(weight, 4)
                    else:
                        self.data.weight_file_edge[f][i][j] = 1
        self.data.weight_to_dictionary()

    def request(self):
        pass

    def update(self):
        pass


class InfoData:
    data = Data()

    def __init__(self, data):
        self.data = data

    # Parameters

    # Vars
    def log_bandwidth_actual_edge(self):
        print("ACTUAL BANDWIDTH.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.bandwidth_actual_edge[f][i][j], end=" ")
                print()
            print()

    def log_map_node_file(self):
        if self.data.map_node_file is not None:
            print("MAPPING.")
            for f in range(len(self.data.key_index_file)):
                for i in range(len(self.data.key_index_orig)):
                    print(self.data.map_node_file[f][i], end=" ")
                print()

    def log_actual_resources_node(self):
        print("ACTUAL RESOURCES.")
        for i in range(len(self.data.key_index_orig)):
            print(self.data.actual_resources_node[i])

    def log_weight_file_edge(self):
        print("WEIGHT.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.weight_file_edge[f][i][j], end=" ")
                print()
            print()

    def log_weight_dict(self):
        for k in self.data.weight_dict.keys():
            print(k, self.data.weight_dict[k])

    # PARAMETERS
    def log_rtt_edge(self):
        print("RTT EDGE.")
        # if self.data.rtt_edge is not None:
        for i in range(len(self.data.key_index_orig)):
            for j in range(len(self.data.key_index_dest)):
                print(self.data.rtt_edge[i][j], end=" ")
            print()

    def log_total_bandwidth(self):
        print("TOTAL BANDWIDTH.")
        if self.data.total_bandwidth_edge is not None:
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.total_bandwidth_edge[i][j], end=" ")
                print()
            print()


class OptimizeData:
    data = Data()

    name = ""
    model = gp.Model(name)
    n = None

    def __init__(self, data, name=""):
        self.data = data
        self.name = name

    # n_fij \in {0,1}
    def create_vars(self):
        self.n = self.model.addVars(self.data.key_index_file, self.data.key_index_orig, self.data.key_index_dest,
                                    vtype=gp.GRB.BINARY)

    def set_function_objective(self):
        self.model.setObjective(
            gp.quicksum(self.n[f, i, j] * self.data.weight_dict[f, i, j] for f in self.data.key_index_file for i in
                        self.data.key_index_orig for j
                        in self.data.key_index_dest), sense=gp.GRB.MINIMIZE)

    def create_constraints(self):
        c1 = self.model.addConstrs(self.data.resources_node[i]
                                   >= self.data.actual_resources_node[i] for i in range(len(self.data.key_index_orig)))

        c2 = self.model.addConstrs(self.data.total_bandwidth_edge[i][j]
                                   >= self.data.bandwidth_actual_edge[f][i][j] for f in range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_orig)) for j in
                                   range(len(self.data.key_index_dest)))

        c3 = self.model.addConstrs(
                (self.data.bandwidth_actual_edge[f][i][j]
                    for f in range(len(self.data.key_index_file))
                    for i in range(len(self.data.key_index_orig))
                    for j in range(len(self.data.key_index_dest))
                )
                >=
                gp.quicksum(
                    self.data.resources_file[f] * self.n[[f], [i],[j]]
                    for f in self.data.key_index_file
                    for i in self.data.key_index_orig
                    for j in self.data.key_index_dest
                )
            )

        gambiarra = self.model.addConstrs(
                (self.data.bandwidth_actual_edge[f][i][j]
                    for f in range(len(self.data.key_index_file))
                    for i in range(len(self.data.key_index_orig))
                    for j in range(len(self.data.key_index_dest))
                )
                >=
                gp.quicksum(
                    self.data.resources_file[f] * self.n[self.data.key_index_file[f], self.data.key_index_orig[i], self.data.key_index_dest[j]]
                    for f in range(len(self.data.key_index_file))
                    for i in range(len(self.data.key_index_orig))
                    for j in range(len(self.data.key_index_dest))
                )
            )

        c4 = self.model.addConstrs(0
                                   <= self.data.weight_file_edge[f][i][j]
                                   <= 1 for f in range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_orig)) for j in
                                   range(len(self.data.key_index_dest)))

        c5 = self.model.addConstrs(gp.quicksum(self.data.map_node_file[f][i] for i in range(len(self.data.key_index_bs))) <= 2 for f in range(len(self.data.key_index_file)))

        c6 = self.model.addConstrs(
            gp.quicksum(self.n[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in self.data.key_index_dest)
            >= 0 for f in range(len(self.data.key_index_file)))

        #c7 = self.model.addConstrs()

    def execute(self):
        self.model.optimize()
