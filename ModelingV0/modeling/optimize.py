import gurobipy as gp
import statistics as s
from utils import utils as utils

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
    key_index_with_file = list()
    key_index_with_ue = list()
    key_index_all = list()
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
    bandwidth_current = dict()
    bandwidth_expected_dict = dict()
    bandwidth_diff = dict()
    resources_file_dict= dict()
    resources_node_dict =  dict()
    actual_resources_node_dict = dict()
    map_user_file_dict = dict()
    bandwidth_min_file_dict = dict()
    gama_file_node_dict = dict()

    def __init__(self, alpha=0, phi=0, num_bs=0, num_ue=0, num_file=0, key1=None, key2=None, key3=None,
                 rf=None, mfu=None, bwf=None, rt_i=None, rtt_base=None, distance=0,avg_rtt=0,
                 sd_rtt=0, loc_UE_node=None, loc_BS_node=None, gama_file_node=None, req=None):

        self.alpha = alpha

        self.phi = phi
        self.num_bs = num_bs
        self.num_ue = num_ue
        if num_bs != 0 and num_ue != 0:
            self.num_nodes = num_bs + num_ue
        self.num_files = num_file

        if key1 is not None and key2 is not None and key3 is not None:
            self.key_index_file = key1
            self.key_index_bs = key2
            self.key_index_ue = key3
            self.key_index_with_file = key2 + key1
            self.key_index_with_ue = key3 + key2
            self.key_index_all = key3 + key2 + key1

        self.resources_file = rf
        self.map_user_file = mfu
        self.bandwidth_min_file = bwf
        self.resources_node = rt_i
        self.file_user_request = req

        self.rtt_base = rtt_base
        self.distance = distance

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.generate_rtt(avg_rtt, sd_rtt)

            self.bandwidth_current_edge = [[[0.0 for i in range(self.num_nodes+self.num_files)] for j in range(self.num_nodes+self.num_files)] for f
                                           in
                                           range(self.num_files)]
            self.actual_resources_node = [0 for i in range(self.num_nodes)]

            self.bandwidth_expected_edge = [[[0.0 for i in range(self.num_nodes+self.num_files)] for j in range(self.num_nodes+ self.num_files)] for f
                                            in
                                            range(self.num_files)]

            self.bandwidth_diff_edge = [[[0.0 for i in range(self.num_nodes+self.num_files)] for j in range(self.num_nodes+self.num_files)] for f in
                                        range(self.num_files)]

            self.weight_file_edge = [[[0.0 for i in range(self.num_nodes+self.num_files)] for j in range(self.num_nodes+self.num_files)] for f in
                                     range(self.num_files)]

            self.omega_user_node = [[0.0 for i in range(self.num_bs)] for j in range(self.num_ue)]

            self.loc_UE_node = loc_UE_node
            self.loc_BS_node = loc_BS_node
            self.gama_file_node = gama_file_node
            self.req =req

            self.weight_to_dictionary()
            self.resources_file_to_dictionary()
            self.resources_node_to_dictionary()
            self.map_user_file_to_dictionary()
            self.bandwidth_min_file_to_dictionary()
            self.gama_file_node_to_dictionary()

    def generate_rtt(self, avg, sd):
        self.rtt_edge = [[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)]
        for i in range(len(self.key_index_with_ue)):
            for j in range(len(self.key_index_with_ue)):
                if i != j:
                    rtt = s.NormalDist(avg, sd).samples(1, seed=None)
                    self.rtt_edge[i][j] = round(rtt[0], 2)
                else:
                    self.rtt_edge[i][j] = NO_EDGE

    def weight_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.weight_dict[tag_file, tag_orig, tag_dest] = self.weight_file_edge[f][i][j]

    def bandwidth_current_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.bandwidth_current[tag_file, tag_orig, tag_dest] = self.bandwidth_current_edge[f][i][j]

    def bandwidth_expected_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.bandwidth_expected_dict[tag_file, tag_orig, tag_dest] = self.bandwidth_expected_edge[f][i][j]

    def bandwidth_diff_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_with_ue)):
                for j in range(len(self.key_index_with_ue)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_with_ue[i]
                    tag_dest = self.key_index_with_ue[j]
                    self.bandwidth_diff[tag_file, tag_orig, tag_dest] = self.bandwidth_diff_edge[f][i][j]

    def resources_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.resources_file_dict[tag] = self.resources_file[f]

    def actual_resources_node_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.actual_resources_node_dict[tag] = self.actual_resources_node[i]

    def resources_node_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.resources_node_dict[tag] = self.resources_node[i]

    def map_user_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for u in range(len(self.key_index_ue)):
                tag_file = self.key_index_file[f]
                tag_user = self.key_index_ue[u]
                self.map_user_file_dict[tag_file,tag_user] = self.map_user_file[f][u]

    def bandwidth_min_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.bandwidth_min_file_dict[tag] = self.bandwidth_min_file[f]

    def gama_file_node_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_bs)):
                tag_file = self.key_index_file[f]
                tag_bs = self.key_index_bs[i]
                self.gama_file_node_dict[tag_file,tag_bs] = self.gama_file_node[f][i]


class HandleData:
    data = Data()

    def __init__(self, data):
        self.data = data

    def calc_omega_user_node(self):
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                dis = utils.euclidean_distance(float(self.data.loc_UE_node[u][X_COORD]), float(self.data.loc_BS_node[i][X_COORD]), float(self.data.loc_UE_node[u][Y_COORD]), float(self.data.loc_BS_node[i][Y_COORD]))
                if dis <= self.data.distance:
                    self.data.omega_user_node[u][i] = 1
                else:
                    self.data.omega_user_node[u][i] = 0

    def calc_current_bandwidth_edge(self):
        rtt_ij = 0
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    size_f = self.data.resources_file[f]
                    if self.data.rtt_edge is not None:
                        rtt_ij = self.data.rtt_edge[i][j]
                    self.data.bandwidth_current_edge[f][i][j] = round(size_f/ rtt_ij,2)
        self.data.bandwidth_current_to_dictionary()

    def calc_expected_bandwidth_edge(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    size_f = self.data.resources_file[f]
                    self.data.bandwidth_expected_edge[f][i][j] = round(size_f /self.data.rtt_base[i][j],2)
        self.data.bandwidth_expected_to_dictionary()

    def calc_diff_bandwidth(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    self.data.bandwidth_diff_edge[f][i][j] = round(self.data.bandwidth_expected_edge[f][i][j] - self.data.bandwidth_current_edge[f][i][j],2)
        self.data.bandwidth_diff_to_dictionary()

    def calc_actual_resources_node(self):
        sum_users = 0
        by_file = 0

        for i in range(len(self.data.key_index_bs)):
            for f in range(len(self.data.key_index_file)):
                if self.data.gama_file_node[f][i] == 1:
                    for u in range(len(self.data.key_index_ue)):
                        sum_users += self.data.map_user_file[f][u]
                    by_file += sum_users * self.data.resources_file[f]
                    sum_users = 0
            self.data.actual_resources_node[i] = by_file
            by_file = 0
        self.data.actual_resources_node_to_dictionary()
            
    def calc_weight_file_edge(self):
        global NO_EDGE
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                for j in range(len(self.data.key_index_bs)):
                    if i != j:
                        rt_i = self.data.resources_node[i]
                        rr_i = self.data.actual_resources_node[i]
                        bwc_fij = self.data.bandwidth_current_edge[f][i][j]
                        bwe_ij = self.data.bandwidth_expected_edge[f][i][j]
                        if rt_i != 0 and bwe_ij != 0 and bwe_ij != NO_EDGE:
                            weight = ((self.data.phi * (rr_i / rt_i)) + ((1 - self.data.phi) * (bwc_fij / bwe_ij)))
                            self.data.weight_file_edge[f][i][j] = round(weight, 4)
                        else:
                            self.data.weight_file_edge[f][i][j] = NO_EDGE
                    else:
                        self.data.weight_file_edge[f][i][j] = NO_EDGE
        self.data.weight_to_dictionary()

    def is_coverage(self,user,bs):
        return self.data.omega_user_node[user][bs] == 1

    def is_caching(self,file,bs):
        return  self.data.gama_file_node[file][bs] == 1


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
        self.x = self.model.addVars(self.data.key_index_file,self.data.key_index_all, self.data.key_index_all,
                                    vtype=gp.GRB.SEMICONT, name="flow")

    def set_function_objective(self):
        self.model.setObjective(
            gp.quicksum(self.x[f,i, j] * self.data.weight_dict[f, i, j] for f in self.data.key_index_file for i in
                        self.data.key_index_all for j in self.data.key_index_all),
            sense=gp.GRB.MINIMIZE)

    def create_constraints(self):
        #limite de recursos do nó.
        c1 = self.set_constraint_1()

        #restrição para vazão esperada seja sempre a menor que a atual.
        c2 = self.set_constraint_2()

        #limiares de custo.
        #c3 = self.set_constraint_3()

        #limiares de capacidade do fluxo.
        c4 = self.set_constraint_4()
        c04 = self.set_constraint_04()

        # restrições de equilibrio de fluxo em nós intermediarios.
        c5 = self.set_constraint_5()

        #restrições de equilibrio de fluxo no nó de origem.
        #c6 = self.set_constraint_6()

        # restrições de equilibrio de fluxo no nó de destino.
        #c7 = self.set_constraint_7()


    def set_constraint_7(self):
        tag_file = self.data.bandwidth_min_file_dict.keys
        return self.model.addConstrs(gp.quicksum(self.x.select(f,'*,','*'))
                                     - gp.quicksum(self.x.select(f,'*,','*'))
                                     == - self.data.bandwidth_min_file[f] for f in
                                     tag_file
                                     )

    def set_constraint_6(self):
        tag_file = self.data.bandwidth_min_file_dict.keys
        return self.model.addConstrs(gp.quicksum(self.x.select(f,'*,','*'))
                                     - gp.quicksum(self.x.select(f,'*,','*'))
                                     == self.data.bandwidth_min_file[f] for f in
                                     tag_file
                                     )

    def set_constraint_5(self):
        return self.model.addConstr(gp.quicksum(
            self.x[f,i, j] - self.x[f,j, i] for f in self.data.key_index_file for i in self.data.key_index_all for j
            in self.data.key_index_all)
                                   == 0)

    def set_constraint_4(self):
        return self.model.addConstrs(
            self.x[f,i,j]
            <= self.data.bandwidth_current[f, i, j] for f in self.data.key_index_file for i in self.data.key_index_all for j in self.data.key_index_all
        )

    def set_constraint_04(self):
        return self.model.addConstrs(0 <=
            self.x[f,i,j] for f in self.data.key_index_file for i in self.data.key_index_all for j in self.data.key_index_all
        )

    def set_constraint_3(self):
        return self.model.addConstrs(0
                                     <= self.data.weight_dict[f, i, j]
                                     <= 1 for f in self.data.key_index_file for i in self.data.key_index_all for j in
                                     self.data.key_index_all)

    def set_constraint_2(self):
        return self.model.addConstrs(self.data.bandwidth_expected_edge[f][i][j]
                                     >= self.data.bandwidth_current_edge[f][i][j] for f in
                                     range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_with_ue))
                                     for j in range(len(self.data.key_index_with_ue)))

    def set_constraint_1(self):
        return self.model.addConstrs(self.data.resources_node[i]
                                     >= self.data.actual_resources_node[i] for i in
                                     range(len(self.data.key_index_bs)))

    def execute(self):
        self.model.optimize()

    def result(self):
        var = self.model.getObjective()
        print(var)
        count =1
        for f in self.data.key_index_file:
            for i in self.data.key_index_all:
                for j in self.data.key_index_all:
                    print(count,self.x[f,i,j])
                    count += 1


class InfoData:
    data = Data()

    def __init__(self, data):
        self.data = data

    # Parameters

    # Vars
    def log_omega_user_node(self):
        print("USER COVERAGE PER BASE STATION(OMEGA).")
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                print(self.data.omega_user_node[u][i], end=" ")
            print()
        print()

    def log_expected_bandwidth_edge(self):
        print("EXPECTED BANDWIDTH.")
        if self.data.bandwidth_expected_edge is not None:
            for f in range(len(self.data.key_index_file)):
                for i in range(len(self.data.key_index_all)):
                    for j in range(len(self.data.key_index_all)):
                        print(self.data.bandwidth_expected_edge[f][i][j], end=" ")
                    print()
                print()
        print()

    def log_current_bandwidth_edge(self):
        print("CURRENT BANDWIDTH.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.bandwidth_current_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def log_diff_bandwidth_edge(self):
        print("DIFFERENCE BANDWIDTH")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.bandwidth_diff_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def log_actual_resources_node(self):
        print("ACTUAL RESOURCES.")
        for i in range(len(self.data.key_index_bs)):
            print(self.data.actual_resources_node[i])
        print()

    def log_actual_resources_node_dict(self):
        print("ACTUAL RESOURCES NODE.")
        for k in self.data.actual_resources_node_dict.keys():
            print(k,self.data.actual_resources_node_dict[k])
        print()

    def log_weight_file_edge(self):
        print("WEIGHT.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.weight_file_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def log_weight_dict(self):
        for k in self.data.weight_dict.keys():
            print(k, self.data.weight_dict[k])
        print()

    # PARAMETERS
    def log_rtt_edge(self):
        print("EDGE RTT.")
        for i in range(len(self.data.key_index_with_ue)):
            for j in range(len(self.data.key_index_with_ue)):
                print(self.data.rtt_edge[i][j], end=" ")
            print()
        print()

    def log_resources_file_dict(self):
        print("RESOURCES FILE.")
        for k in self.data.resources_file_dict.keys():
            print(k, self.data.resources_file_dict[k])
        print()

    def log_resources_node_dict(self):
        print("TOTAL RESOURCES NODE.")
        for k in self.data.resources_node_dict.keys():
            print(k,self.data.resources_node_dict[k])
        print()

    def log_map_user_file(self):
        print("MAPPING REQUEST USER TO FILE.")
        for f in range(len(self.data.key_index_file)):
            for u in range(len(self.data.key_index_ue)):
                print(self.data.map_user_file[f][u],end=" ")
            print()
        print()

    def log_map_user_file_dict(self):
        print("MAPPING REQUEST USER TO FILE.")
        for k in self.data.map_user_file_dict.keys():
            print(k,self.data.map_user_file_dict[k])
        print()

    def log_bandwidth_min_dict(self):
        print("MINIMAL BANDWIDTH.")
        for k in self.data.bandwidth_min_file_dict.keys():
            print(k, self.data.bandwidth_min_file_dict[k])
        print()

    def log_rtt_base(self):
        print("BASE RTT.")
        for i in range(len(self.data.key_index_with_ue)):
            for j in range(len(self.data.key_index_with_ue)):
                print(self.data.rtt_base[i][j],end=" ")
            print()
        print()

    def log_gama_file_node(self):
        print("FILE CACHING PER BASE STATION(GAMA).")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.gama_file_node[f][i], end=" ")
            print()
        print()
