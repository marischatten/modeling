import gurobipy as gp


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
    file_user_request = [[0] * num_nodes] * num_files

    # rtt_ij \in R
    edge_rtt = [[0] * num_nodes] * num_nodes
    # bwt_ij \in R
    total_bandwidth_edge = [[0] * num_nodes] * num_nodes

    # Vars
    # bwa_ij \in R
    bandwidth_actual_edge = [[[0] * num_nodes] * num_nodes] * num_files

    # mf_i \in {0,1}
    map_node_file = [[0] * num_nodes] * num_files

    # rr_i \in R
    actual_resources_node = list()

    # c_fij \in R
    weight_file_edge = [[[0] * num_nodes] * num_nodes] * num_files

    weight_dict = dict()

    def __init__(self, alpha=None, num_bs=None, num_ue=None, num_file=None, key1=None, key2=None, key3=None, fs=None,
                 fr=None, bwf=None, rt_i=None, fu=None, bwt_ij=None, min_rtt=None,
                 max_rtt=None):
        self.alfa = alpha
        self.num_bs = num_bs
        self.num_ue = num_ue
        if num_bs is not None and num_ue is not None:
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
        self.edge_rtt = self.generate_rtt(min_rtt, max_rtt)
        self.total_bandwidth_edge = bwt_ij

    def weight_to_dictionary(self):
        tag = " "
        key_weight = list()
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                for j in range(len(self.key_index_dest)):
                    tag += self.key_index_file[f] + "-"
                    tag += self.key_index_orig[i] + "_"
                    tag += self.key_index_dest[j]
                    key_weight.append(tag)
                    tag = ""

        value_weight = list()
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                for j in range(len(self.key_index_dest)):
                    value_weight.append(self.weight_file_edge[f][i][j])

        for i, value in enumerate(value_weight):
            key = key_weight[i]
            self.weight_dict[key] = value

    def generate_rtt(self, bottom, top):
        pass


class HandleData:

    data = Data()

    def __init__(self, data):
        self.data = data

    def calc_bandwidth_actual_edge(self):
        for i in range(len(self.data.key_index_orig)):
            for j in range(len(self.data.key_index_dest)):
                for f in range(len(self.data.key_index_file)):
                    size_f = self.data.size_file[f]
                    rtt_ij = self.data.edge_rtt[i][j]
                    self.data.bandwidth_actual_edge[i][j] = round(size_f / rtt_ij, 4)

    def calc_map_file(self, file, orig, dest):
        self.data.map_node_file[file][orig] = 0
        self.data.map_node_file[file][dest] = 1

    def calc_actual_resources_node(self):
        node = 0
        sum_users = 0
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                if self.data.map_node_file[f][i] == 1:
                    for i in range(len(self.data.key_index_orig)):
                        sum_users += self.data.file_user_request[f][i]
                        node += sum_users * self.data.resources_file[f]
                    sum_users = 0
            self.data.actual_resources_node[i] = node
            node = 0

    def calc_weight_file_edge(self):
        for i in range(len(self.data.key_index_orig)):
            for j in range(len(self.data.key_index_dest)):
                for f in range(len(self.data.key_index_file)):
                    rt_i = self.data.resources_node[i]
                    rr_i = self.data.actual_resources_node[i]
                    bwa_ij = self.data.bandwidth_actual_edge[i][j]
                    bwt_ij = self.data.total_bandwidth_edge[i][j]
                    if rt_i != 0 and bwt_ij != 0 and rr_i != 0 and bwa_ij != 0:
                        weight = ((self.data.alpha * (rr_i / rt_i)) + ((1 - self.data.alpha) * (bwa_ij / bwt_ij))) / (
                                self.data.alpha + (1 - self.data.alpha))
                        self.data.weight_file_edge[f][i][j] = round(weight, 4)
                    else:
                        self.data.weight_file_edge[f][i][j] = 1

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
        for i in range(len(self.data.key_index_orig)):
            for j in range(len(self.data.key_index_dest)):
                print(self.data.bandwidth_actual_edge[i][j], end=" ")
            print()

    def log_map_node_file(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                print(self.data.map_node_file[f][i], end=" ")
            print()

    def log_actual_resources_node(self):
        for i in range(len(self.data.key_index_orig)):
            print(self.data.actual_resources_node[i])

    def log_weight_file_edge(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.weight_file_edge[f][i][j], end=" ")
                print()
            print()
            print()


class OptimizeData:
    data = Data()

    model = None
    n = None

    def __init__(self, data):
        self.data = data

    def create_model(self):
        model = gp.Model("Orchestrator")

    # n_fij \in {0,1}
    def create_vars(self):
        n = self.model.addVars(self.data.key_index_file, self.data.key_index_orig, self.data.key_index_dest,
                               vtype=gp.GRB.BINARY)


'''
    def set_function_objective(self):
        self.model.setObjective(gp.quicksum(
            n[f, i, j] * self.data.weight_file_edge[f][i][j] for f in self.data.key_index_file for i in self.data.key_index_orig for j
            in self.data.key_index_dest),
                                sense=gp.GRB.MINIMIZE
                                )     

    def create_constraints(self):
        c1 = self.model.addConstrs(self.data.resources_node[i]
                                   >= self.data.actual_resources_node[i] for i in self.data.key_index_orig)

        c2 = self.model.addConstrs(self.data.total_bandwidth_edge[i][j]
                                   >= self.data.bandwidth_actual_edge[i][j] for i in self.data.key_index_orig for j in
                                   self.data.key_index_dest)

        c3 = self.model.addConstrs(
            (self.data.bandwidth_actual_edge[i][j] for i in self.data.key_index_orig for j in self.data.key_index_dest)
            >=
            gp.quicksum(
                self.data.resources_file[f] * n[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
                self.data.key_index_dest))

        c4 = self.model.addConstrs(0
                                   <= self.data.weight_file_edge[f][i][j]
                                   <= 1 for f in self.data.key_index_file for i in self.data.key_index_orig for j in
                                   self.data.key_index_dest)

        c5 = self.model.addConstrs(gp.quicksum(self.data.map_node_file[f][i] for i in self.data.key_index_bs)
                                   <= 2 for f in self.data.key_index_file)

        c6 = self.model.addConstrs(
            gp.quicksum(n[f, i, j] for i in self.data.key_index_orig for j in self.data.key_index_dest)
            >= 1 for f in self.data.key_index_file)

        c7 = self.model.addConstrs(
            gp.quicksum(n[f, i, j] for i in self.data.key_index_orig for j in self.data.key_index_dest)
            <= abs(self.data.key_index_orig * self.data.key_index_dest) for f in self.data.key_index_file)

        c8 = self.model.addConstrs()

        # c9 = model.addConstrs(gp.quicksum(n[f,i,j] for i in key_index_orig) - gp.quicksum(n[f,k,i] for k in key_index_orig) == 1 if i == f -1 if i==u else 0)

    def execute(self):
        self.model.optimize()
'''
