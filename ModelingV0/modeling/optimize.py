import gurobipy as gp
import statistics as s
from utils import utils as utils
from fractions import Fraction as frac
from decimal import Decimal

NO_EDGE = 9999
TAG_COORD = 0
X_COORD = 1
Y_COORD = 2

class Data:
    # Input
    alpha = 0
    phi = 0

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

    # fr \in R
    resources_file = list()
    #mfu \in {0,1}
    map_user_file = list()
    # bwf \in R
    bandwidth_min_file = list()

    # rt_i \in R
    resources_node = list()

    rtt_base = 0

    # rtt_ij \in R
    rtt_edge = None

    #D \in R
    distance = 0

    #loc(x,y)
    loc_UE_node =list()
    loc_BS_node = list()
    #gama \in {0,1}
    gama_file_node = list()

    #r(s,t) \forall s \in F, \forall t \in UE
    req= None
    # Vars

    # omega
    omega_user_node = None

    # bwc_ij \in R
    bandwidth_current_edge = None

    # bwe_ij \in R
    bandwidth_expected_edge = None

    # bwdiff_fij \in R
    bandwidth_diff_edge = None

    # rr_i \in R
    actual_resources_node = list()

    # c_fij \in R
    weight_file_edge = None

    weight_dict = dict()
    bandwidth_diff = dict()
    resources_dict = dict()

    def __init__(self, alpha=0, phi=0, num_bs=0, num_ue=0, num_file=0, key1=None, key2=None, key3=None,
                 rf=None, mfu=None, bwf=None, rt_i=None, rtt_base=0, distance=0,avg_rtt=0,
                 sd_rtt=0, loc_UE_node=None, loc_BS_node=None, gama_file_node=None, req=None):

        self.alpha = alpha

        self.phi = phi
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

        self.resources_file = rf
        self.map_user_file = mfu
        self.bandwidth_min_file = bwf
        self.resources_node = rt_i
        self.file_user_request = req

        self.rtt_base = rtt_base
        self.distance = distance

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.generate_rtt(avg_rtt, sd_rtt)

            self.bandwidth_current_edge = [[[" " for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f
                                           in
                                           range(self.num_files)]
            self.actual_resources_node = [0 for i in range(self.num_nodes)]

            self.bandwidth_expected_edge = [[[" " for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f
                                            in
                                            range(self.num_files)]

            self.bandwidth_diff_edge = [[[" " for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f in
                                        range(self.num_files)]

            self.weight_file_edge = [[[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)] for f in
                                     range(self.num_files)]

            self.omega_user_node = [[0.0 for i in range(self.num_bs)] for j in range(self.num_ue)]

            self.loc_UE_node = loc_UE_node
            self.loc_BS_node = loc_BS_node
            self.gama_file_node = gama_file_node
            self.req =req

            self.weight_to_dictionary()
            self.bandwidth_diff_to_dictionary()

    def weight_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                for j in range(len(self.key_index_dest)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_orig[i]
                    tag_dest = self.key_index_dest[j]
                    self.weight_dict[tag_file, tag_orig, tag_dest] = self.weight_file_edge[f][i][j]

    def bandwidth_diff_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                for j in range(len(self.key_index_dest)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_orig[i]
                    tag_dest = self.key_index_dest[j]
                    self.bandwidth_diff[tag_file, tag_orig, tag_dest] = self.bandwidth_diff_edge[f][i][j]

    def generate_rtt(self, avg, sd):
        self.rtt_edge = [[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)]
        for i in range(len(self.key_index_orig)):
            for j in range(len(self.key_index_dest)):
                if i != j:
                    rtt = s.NormalDist(avg, sd).samples(1, seed=None)
                    self.rtt_edge[i][j] = round(rtt[0], 2)
                else:
                    self.rtt_edge[i][j] = NO_EDGE

    def resources_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.resources_dict[tag] = self.resources_file[f]


class HandleData:
    data = Data()

    def __init__(self, data):
        self.data = data

    def calc_current_bandwidth_edge(self):
        rtt_ij = 0
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    size_f = self.data.resources_file[f]
                    if self.data.rtt_edge is not None:
                        rtt_ij = self.data.rtt_edge[i][j]
                    self.data.bandwidth_current_edge[f][i][j] = round(size_f/ rtt_ij,2)

    def calc_expected_bandwidth_edge(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    size_f = self.data.resources_file[f]
                    self.data.bandwidth_expected_edge[f][i][j] = round(size_f /self.data.rtt_base,2)


    def calc_diff_bandwidth(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    self.data.bandwidth_diff_edge[f][i][j] = round(self.data.bandwidth_expected_edge[f][i][j] - self.data.bandwidth_current_edge[f][i][j],2)

    def calc_actual_resources_node(self):
        sum_users = 0
        by_file = 0
        for i in range(len(self.data.key_index_orig)):
            for f in range(len(self.data.key_index_file)):
                if self.data.gama_file_node[f][i] == 1:
                    for u in range(len(self.data.key_index_orig)):
                        sum_users += self.data.map_user_file[f][u]
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
                    bwc_fij = self.data.bandwidth_current_edge[f][i][j]
                    bwe_ij = self.data.bandwidth_expected_edge[f][i][j]
                    if rt_i != 0 and bwe_ij != 0 and bwe_ij != NO_EDGE:
                        weight = ((self.data.phi * (rr_i / rt_i)) + ((1 - self.data.phi) * (bwc_fij / bwe_ij)))
                        self.data.weight_file_edge[f][i][j] = round(weight, 4)
                    else:
                        self.data.weight_file_edge[f][i][j] = NO_EDGE
        self.data.weight_to_dictionary()

    def calc_omega_user_node(self):
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                dis = utils.euclidean_distance(float(self.data.loc_UE_node[u][X_COORD]), float(self.data.loc_BS_node[i][X_COORD]), float(self.data.loc_UE_node[u][Y_COORD]), float(self.data.loc_BS_node[i][Y_COORD]))
                if dis <= self.data.distance:
                    self.data.omega_user_node[u][i] = 1
                else:
                    self.data.omega_user_node[u][i] = 0


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
    def log_omega_user_node(self):
        print("USER COVERAGE PER BASE STATION.")
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                print(self.data.omega_user_node[u][i], end=" ")
            print()

    def log_expected_bandwidth_edge(self):
        print("EXPECTED BANDWIDTH.")
        if self.data.bandwidth_expected_edge is not None:
            for f in range(len(self.data.key_index_file)):
                for i in range(len(self.data.key_index_orig)):
                    for j in range(len(self.data.key_index_dest)):
                        print(self.data.bandwidth_expected_edge[f][i][j], end=" ")
                    print()
                print()

    def log_current_bandwidth_edge(self):
        print("CURRENT BANDWIDTH.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.bandwidth_current_edge[f][i][j], end=" ")
                print()
            print()

    def log_diff_bandwidth_edge(self):
        print("DIFFERENCE BANDWIDTH")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_orig)):
                for j in range(len(self.data.key_index_dest)):
                    print(self.data.bandwidth_diff_edge[f][i][j], end=" ")
                print()
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

    def log_resources_file_dict(self):
        for k in self.data.resources_dict.keys():
            print(k, self.data.resources_dict[k])


class OptimizeData:
    data = Data()

    name = ""
    model = gp.Model(name)
    x = None

    def __init__(self, data, name=""):
        self.data = data
        self.name = name

    # n_fij \in {0,1}
    def create_vars(self):
        self.x = self.model.addVars(self.data.key_index_file, self.data.key_index_orig, self.data.key_index_dest,
                                    vtype=gp.GRB.BINARY, name="flow")

    def set_function_objective(self):
        self.model.setObjective(
            gp.quicksum(self.x[f, i, j] * self.data.weight_dict[f, i, j] for f in self.data.key_index_file for i in
                        self.data.key_index_orig for j in self.data.key_index_dest),
            sense=gp.GRB.MINIMIZE)

    def create_constraints(self):

        #limite de recursos do nó.
        c1 = self.model.addConstrs(self.data.resources_node[i]
                                   >= self.data.actual_resources_node[i] for i in range(len(self.data.key_index_orig)))

        #restrição para vazão esperada seja sempre a menor que a atual.
        c2 = self.model.addConstrs(self.data.bandwidth_expected_edge[f][i][j]
                                   >= self.data.bandwidth_current_edge[f][i][j] for f in
                                   range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_orig))
                                   for j in range(len(self.data.key_index_dest)))

        #limiares de custo.
        c3 = self.model.addConstrs(0
                                   <= self.data.weight_dict[f, i, j]
                                   <= 1 for f in self.data.key_index_file for i in self.data.key_index_orig for j in
                                   self.data.key_index_dest)

        #limiares de capacidade do fluxo.
        c4 = self.model.addConstrs(0
                                   <= self.x[f,i,j]
                                   <= 1 for f in self.data.key_index_file for i in self.data.key_index_orig for j
                                    in self.data.key_index_dest)


        # restrições de equilibrio de fluxo em nós intermediarios.
        c5 = self.model.addConstrs(gp.quicksum(
            self.x[f, i, j] - self.x[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j
            in self.data.key_index_dest)
                                   == 0)

        #restrições de equilibrio de fluxo no nó de origem.
        c6 = self.model.addConstrs(gp.quicksum(
            self.x[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest)
                                   - gp.quicksum(
            self.x[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest)
                                   == self.data.bandwidth_min_file[f][i][j] for f in
                                   range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_orig))
                                   for j in range(len(self.data.key_index_dest)))

        # restrições de equilibrio de fluxo no nó de destino.
        c7 = self.model.addConstrs(gp.quicksum(
            self.x[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest)
                                   - gp.quicksum(
            self.x[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest)
                                   == - self.data.bandwidth_min_file[f][i][j] for f in
                                   range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_orig))
                                   for j in range(len(self.data.key_index_dest)))

        #retrição de único enlace entre UE e BS.
        c8 = self.model.addConstrs(gp.quicksum(self.x[f,i,j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest) == self.data.bandwidth_min_file[u] for u in range(len(self.data.key_index_ue)))

        # retrição de único enlace entre conteúdo e BS.
        c9 = self.model.addConstrs(gp.quicksum(self.x[f,i,j] for f in self.data.key_index_file for i in self.data.key_index_orig for j in
            self.data.key_index_dest) == self.data.bandwidth_min_file[f] for f in range(len(self.data.key_index_file)))

    def execute(self):
        self.model.optimize()

    def result(self):
        var = self.model.getObjective()
        print(var)
        '''
                for f in self.data.key_index_file:
            for i in self.data.key_index_orig:
                for j in self.data.key_index_dest:
                        print(self.x[f,i,j])
        '''


