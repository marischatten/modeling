import gurobipy as gp
import statistics as s
from utils import utils as utils
import itertools
import numpy as np
import ortools as otlp  #somente LP

NO_EDGE = 9999
TAG_COORD = 0
X_COORD = 1
Y_COORD = 2

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"

class Data:
    # Input
    alpha = 0
    beta = 0

    #source
    s = None
    #sink
    t = None

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

    x_bs_adj = list()

    # fr \in R
    resources_file = list()

    # phi \in R
    phi = list()

    # bwf \in R
    bandwidth_min_file = list()

    # rt_i \in R
    resources_node = list()

    rtt_base = 0

    # rtt_ij \in R
    rtt_edge = None

    # D \in R
    distance = 0

    # loc(x,y)
    loc_UE_node = list()
    loc_BS_node = list()
    # gama \in {0,1}
    gama_file_node = list()

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
    current_resources_node = None

    # c_fij \in R
    weight_file_edge = None

    weight_dict = dict()
    bandwidth_current_edge_dict = dict()
    bandwidth_expected_edge_dict = dict()
    bandwidth_diff_edge_dict = dict()
    resources_file_dict = dict()
    resources_node_dict = dict()
    current_resources_node_dict = dict()
    phi_dict = dict()
    bandwidth_min_file_dict = dict()
    gama_file_node_dict = dict()
    omega_user_node_dict = dict()
    x_bs_adj_dict = dict()

    def __init__(self, alpha=0, beta=0, num_bs=0, num_ue=0, num_file=0, key1=None, key2=None, key3=None, x_bs_adj=None,
                 rf=None, phi=None, bwf=None, rt_i=None, rtt_base=None, distance=0, avg_rtt=0,
                 sd_rtt=0, loc_UE_node=None, loc_BS_node=None, gama_file_node=None, source=None, sink=None):

        self.alpha = alpha
        self.beta = beta

        self.s = source
        self.t = sink

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
            self.key_index_all = key2 + key3+ key1

        self.x_bs_adj = x_bs_adj

        self.resources_file = rf
        self.phi = phi
        self.bandwidth_min_file = bwf
        self.resources_node = rt_i

        self.rtt_base = rtt_base
        self.distance = distance

        if num_bs != 0 and num_ue != 0 and num_file != 0:
            self.generate_rtt(avg_rtt, sd_rtt)

            self.bandwidth_current_edge = [
                [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f
                in
                range(self.num_files)]
            self.current_resources_node = [0 for i in range(self.num_nodes)]

            self.bandwidth_expected_edge = [
                [[NO_EDGE for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f
                in
                range(self.num_files)]

            self.bandwidth_diff_edge = [
                [[0.0 for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f in
                range(self.num_files)]

            self.weight_file_edge = [
                [[0.0 for i in range(self.num_nodes + self.num_files)] for j in range(self.num_nodes + self.num_files)]
                for f in
                range(self.num_files)]

            self.omega_user_node = [[0.0 for i in range(self.num_bs)] for j in range(self.num_ue)]

            self.loc_UE_node = loc_UE_node
            self.loc_BS_node = loc_BS_node
            self.gama_file_node = gama_file_node

            self.weight_to_dictionary()
            self.resources_file_to_dictionary()
            self.resources_node_to_dictionary()
            self.phi_file_to_dictionary()
            self.bandwidth_min_file_to_dictionary()
            self.gama_file_node_to_dictionary()
            self.x_bs_adj_to_dictionary()

    def generate_rtt(self, avg, sd):
        self.rtt_edge = [[0.0 for i in range(self.num_nodes)] for j in range(self.num_nodes)]
        for i in range(len(self.key_index_with_ue)):
            for j in range(len(self.key_index_with_ue)):
                if i != j:
                    rtt = s.NormalDist(avg, sd).samples(1, seed=None)
                    self.rtt_edge[i][j] = round(rtt[0], 2)
                else:
                    self.rtt_edge[i][j] = NO_EDGE

    # PARAMETERS TO DICTIONARY
    def phi_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_bs)):
                tag_file = self.key_index_file[f]
                tag_user = self.key_index_bs[i]
                self.phi_dict[tag_file, tag_user] = self.phi[f][i]

    def resources_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.resources_file_dict[tag] = self.resources_file[f]

    def bandwidth_min_file_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            tag = self.key_index_file[f]
            self.bandwidth_min_file_dict[tag] = self.bandwidth_min_file[f]

    def resources_node_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            tag = self.key_index_bs[i]
            self.resources_node_dict[tag] = self.resources_node[i]

    def gama_file_node_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_bs)):
                tag_file = self.key_index_file[f]
                tag_bs = self.key_index_bs[i]
                self.gama_file_node_dict[tag_file, tag_bs] = self.gama_file_node[f][i]

    def x_bs_adj_to_dictionary(self):
        for i in range(len(self.key_index_bs)):
            for j in range(len(self.key_index_bs)):
                tag_orig = self.key_index_bs[i]
                tag_dest = self.key_index_bs[j]
                self.x_bs_adj_dict[tag_orig, tag_dest] = self.x_bs_adj[i][j]

    # VARS TO DICTIONARY
    def omega_user_node_to_dictionary(self):
        for u in range(len(self.key_index_ue)):
            for i in range(len(self.key_index_bs)):
                tag_ue = self.key_index_ue[u]
                tag_bs = self.key_index_bs[i]
                self.omega_user_node_dict[tag_ue, tag_bs] = self.omega_user_node[u][i]

    def bandwidth_expected_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.bandwidth_expected_edge_dict[tag_file, tag_orig, tag_dest] = \
                    self.bandwidth_expected_edge[f][i][j]

    def bandwidth_current_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_all)):
                for j in range(len(self.key_index_all)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_all[i]
                    tag_dest = self.key_index_all[j]
                    self.bandwidth_current_edge_dict[tag_file, tag_orig, tag_dest] = self.bandwidth_current_edge[f][i][
                        j]

    def bandwidth_diff_to_dictionary(self):
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_with_ue)):
                for j in range(len(self.key_index_with_ue)):
                    tag_file = self.key_index_file[f]
                    tag_orig = self.key_index_with_ue[i]
                    tag_dest = self.key_index_with_ue[j]
                    self.bandwidth_diff_edge_dict[tag_file, tag_orig, tag_dest] = self.bandwidth_diff_edge[f][i][j]

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


class HandleData:
    data = Data()

    def __init__(self, data):
        self.data = data

    def calc_omega_user_node(self):
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                dis = utils.euclidean_distance(float(self.data.loc_UE_node[u][X_COORD]),
                                               float(self.data.loc_BS_node[i][X_COORD]),
                                               float(self.data.loc_UE_node[u][Y_COORD]),
                                               float(self.data.loc_BS_node[i][Y_COORD]))
                if dis <= self.data.distance:
                    self.data.omega_user_node[u][i] = 1
                else:
                    self.data.omega_user_node[u][i] = 0
        self.data.omega_user_node_to_dictionary()

    def calc_current_bandwidth_edge(self):
        rtt_ij = 0
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    size_f = self.data.resources_file[f]
                    if self.data.rtt_edge is not None:
                        rtt_ij = self.data.rtt_edge[i][j]
                    self.data.bandwidth_current_edge[f][i][j] = round(size_f / rtt_ij, 2)
        self.data.bandwidth_current_to_dictionary()

    def calc_expected_bandwidth_edge(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    size_f = self.data.resources_file[f]
                    self.data.bandwidth_expected_edge[f][i][j] = round(size_f / self.data.rtt_base[i][j], 2)
        self.data.bandwidth_expected_to_dictionary()

    def calc_diff_bandwidth(self):
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_with_ue)):
                for j in range(len(self.data.key_index_with_ue)):
                    self.data.bandwidth_diff_edge[f][i][j] = round(
                        self.data.bandwidth_expected_edge[f][i][j] - self.data.bandwidth_current_edge[f][i][j], 2)
        self.data.bandwidth_diff_to_dictionary()

    def calc_current_resources_node(self):
        for i in range(len(self.data.key_index_bs)):
            file = 0
            for f in range(len(self.data.key_index_file)):
                if self.data.gama_file_node[f][i] == 1 and self.data.phi[f][i] != 0:
                     file += self.data.gama_file_node[f][i] * self.data.resources_file[f] * self.data.phi[f][i]
            self.data.current_resources_node[i] = file
        self.data.current_resources_node_to_dictionary()

    def calc_weight_file_edge(self):
        global NO_EDGE
        for f,filename in enumerate(self.data.key_index_file):
            for i,orig_name in enumerate(self.data.key_index_all):
                for j,dest_name in enumerate(self.data.key_index_all):
                    if i == j: # Origem e destino não podem ser iguais.
                        self.data.weight_file_edge[f][i][j] = NO_EDGE
                    elif self.is_ue(orig_name) or self.is_content(orig_name): #UE ou F
                        if self.is_ue(orig_name): # Não existe aresta saindo de UE.
                            self.data.weight_file_edge[f][i][j] = NO_EDGE
                        elif self.is_content_to_bs(dest_name): #O custo de F para BS é sempre 0. Se o Gama entre BS e F são iguais a 1.
                            if self.is_caching(orig_name,dest_name): # #BS não armazena F.
                                self.data.weight_file_edge[f][i][j] = 0.0
                            else:#BS armazena F.
                                self.data.weight_file_edge[f][i][j] = NO_EDGE
                        else: #F para UE.
                            self.data.weight_file_edge[f][i][j] = NO_EDGE # Não existe aresta entre F e UE.
                    else:#BS
                        if self.is_bs_to_content(dest_name): #Não existe aresta com origem em BS para F.
                            self.data.weight_file_edge[f][i][j] = NO_EDGE
                        else:#BS para UE
                            if self.is_coverage(orig_name,dest_name): #Existe aresta de origem em BS para o destino UE ou origem em BS para o destino BS.
                                rt_i = self.data.resources_node[i]
                                rr_i = self.data.current_resources_node[i]
                                bwc_diff_fij = self.data.bandwidth_diff_edge[f][i][j]
                                weight = self.calc_weight(rr_i,rt_i,bwc_diff_fij)
                                self.data.weight_file_edge[f][i][j] = round(weight, 4)
                            else: #Não existe aresta de origem em BS parao destino UE.
                                self.data.weight_file_edge[f][i][j] = NO_EDGE
        self.data.weight_to_dictionary()

    def calc_weight(self,rr_i,rt_i,bwc_diff_fij):
        return (self.data.alpha * (rr_i / rt_i)) + ((1 - self.data.alpha - self.data.beta) * (self.data.beta*bwc_diff_fij))

    def is_caching(self, file, bs):
        return self.data.gama_file_node_dict[file,bs] == 1

    def is_coverage(self, orig, dest):
        if self.is_ue(dest):
            return self.is_coverage_bs_to_ue(orig,dest)
        else:
            return self.is_coverage_bs_to_bs(orig,dest)

    def is_ue(self,name):
        return name in self.data.key_index_ue

    def is_content(self,name):
        return name in self.data.key_index_file

    def is_content_to_bs(self,dest):
        return dest in self.data.key_index_bs

    def is_bs_to_content(self,dest):
        return dest in self.data.key_index_file

    def is_coverage_bs_to_bs(self,orig,dest):
        return self.data.x_bs_adj_dict[orig,dest] == 1

    def is_coverage_bs_to_ue(self,orig,dest):
        return self.data.omega_user_node_dict[dest,orig] == 1


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
        self.x = self.model.addVars(self.data.key_index_file, self.data.key_index_all, self.data.key_index_all,
                                    vtype=gp.GRB.SEMICONT, name="flow")

    def set_function_objective(self):
        self.model.setObjective(
            gp.quicksum(self.x[f, i, j] * self.data.weight_dict[f, i, j] for f in self.data.key_index_file for i in
                        self.data.key_index_all for j in self.data.key_index_all),
            sense=gp.GRB.MINIMIZE)

    def create_model_in_ortools(self):
        pass

    def create_constraints(self):
        # limite de recursos do nó.
        self.set_constraint_node_resources_capacity()

        # restrição para vazão esperada seja sempre a menor que a atual.
        self.set_constraint_throughput()

        # limiares de capacidade do fluxo.
        #self.set_constraint_flow_capacity_max()

        # restrições de equilibrio de fluxo em nós intermediarios.
        self.set_constraint_flow_conservation()

        # restrições de equilibrio de fluxo no nó de origem.
        self.set_constraint_flow_conservation_source()

        # restrições de equilibrio de fluxo no nó de destino.
        self.set_constraint_flow_conservation_sink()

    def set_constraint_flow_conservation_sink(self):
        for f in self.data.s:
            self.model.addConstr(gp.quicksum(self.x[f, t, i] for t in self.data.t for i in self.data.key_index_bs)
                - gp.quicksum(self.x[f, i, t] for t in self.data.t for i in self.data.key_index_bs)
                == - self.data.bandwidth_min_file_dict[f],'c6')

    def set_constraint_flow_conservation_source(self):
        for f in self.data.s:
            self.model.addConstr(gp.quicksum(self.x[f, s, i] for s in self.data.s for i in self.data.key_index_bs)
                - gp.quicksum(self.x[f, i, s] for s in self.data.s for i in self.data.key_index_bs)
                == self.data.bandwidth_min_file_dict[f],'c5')

    def set_constraint_flow_conservation(self):
        for f in self.data.s:
            for i in self.data.key_index_all:
                if i != self.data.s and i != self.data.t:
                    self.model.addConstr(gp.quicksum(self.x[f, i, j] for j in self.data.key_index_all)
                    - gp.quicksum(self.x[f, j, i] for j in self.data.key_index_all)
                    == 0,'c4')

    def set_constraint_flow_capacity_max(self):
        self.model.addConstrs(
            self.x[f, i, j] <= self.data.bandwidth_current_edge_dict[f, i, j] for f in self.data.s for i in self.data.key_index_all for j in self.data.key_index_all)

    def set_constraint_throughput(self):
        self.model.addConstrs(self.data.bandwidth_expected_edge[f][i][j]
            >= self.data.bandwidth_current_edge[f][i][j] for f in range(len(self.data.key_index_file)) for i in range(len(self.data.key_index_with_ue)) for j in range(len(self.data.key_index_with_ue)))

    def set_constraint_node_resources_capacity(self):
        self.model.addConstrs(self.data.resources_node[i]
             >= self.data.current_resources_node[i] for i in range(len(self.data.key_index_bs)))

    def execute(self):
        self.model.optimize()

    def result(self):
        if self.model.status == gp.GRB.OPTIMAL:
            print(GREEN +"SOLUÇÃO ÓTIMA."+RESET)
            obj = self.model.getObjective()
            print(CYAN +"FUNÇÃO OBJETIVO: "+ RED +str(obj.getValue())+RESET)
            print("CAMINHO:")
            for var in self.model.getVars():
                if var.X != 0:
                    print(var.VarName, round(var.X,2))
        else:
            print(RED + "NÃO EXISTE SOLUÇÃO ÓTIMA.")


# This class show data in parameters and vars.
class InfoData:
    data = Data()

    def __init__(self, data):
        self.data = data

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
            print(k, self.data.resources_node_dict[k])
        print()

    def log_phi(self):
        print("RESOURCES LOADED PER BASE STATION.")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.phi[f][i], end=" ")
            print()
        print()

    def log_phi_dict(self):
        print("RESOURCES LOADED PER BASE STATION.")
        for k in self.data.phi_dict.keys():
            print(k, self.data.phi_dict[k])
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
                print(self.data.rtt_base[i][j], end=" ")
            print()
        print()

    def log_gama_file_node(self):
        print("FILE CACHING PER BASE STATION(GAMA).")
        for f in range(len(self.data.key_index_file)):
            for i in range(len(self.data.key_index_bs)):
                print(self.data.gama_file_node[f][i], end=" ")
            print()
        print()

    def log_x_bs_adj(self):
        print("COVERAGE BETWEEN BASE STATIONS(X).")
        for i in range(len(self.data.key_index_bs)):
            for j in range(len(self.data.key_index_bs)):
                print(self.data.x_bs_adj[i][j], end=" ")
            print()
        print()

    def log_x_bs_adj_dict(self):
        print("COVERAGE BETWEEN BASE STATIONS(X).")
        for k in self.data.x_bs_adj_dict.keys():
            print(k, self.data.x_bs_adj_dict[k])
        print()

    # VARS
    def log_omega_user_node(self):
        print("USER COVERAGE PER BASE STATION(OMEGA).")
        for u in range(len(self.data.loc_UE_node)):
            for i in range(len(self.data.loc_BS_node)):
                print(self.data.omega_user_node[u][i], end=" ")
            print()
        print()

    def log_omega_user_node_dict(self):
        for k in self.data.omega_user_node_dict.keys():
            print(k, self.data.omega_user_node_dict[k])

    def log_expected_bandwidth_edge(self):
        print("EXPECTED BANDWIDTH.")
        if self.data.bandwidth_expected_edge is not None:
            for f, filename in enumerate(self.data.key_index_file):
                print(filename.upper())
                for i in range(len(self.data.key_index_all)):
                    for j in range(len(self.data.key_index_all)):
                        print(self.data.bandwidth_expected_edge[f][i][j], end=" ")
                    print()
                print()
        print()

    def log_expected_bandwidth_edge_dict(self):
        for k in self.data.bandwidth_expected_edge_dict.keys():
            print(k, self.data.bandwidth_expected_edge_dict[k])

    def log_current_bandwidth_edge(self):
        print("CURRENT BANDWIDTH.")
        for f,filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.bandwidth_current_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def log_current_bandwidth_edge_dict(self):
        for k in self.data.bandwidth_current_edge_dict.keys():
            print(k, self.data.bandwidth_current_edge_dict[k])

    def log_diff_bandwidth_edge(self):
        print("DIFFERENCE BANDWIDTH")
        for f,filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(self.data.bandwidth_diff_edge[f][i][j], end=" ")
                print()
            print()
        print()

    def log_diff_bandwidth_edge_dict(self):
        for k in self.data.bandwidth_diff_edge_dict.keys():
            print(k, self.data.bandwidth_diff_edge_dict[k])

    def log_current_resources_node(self):
        print("CURRENT RESOURCES.")
        for i in range(len(self.data.key_index_bs)):
            print(self.data.current_resources_node[i])
        print()

    def log_current_resources_node_dict(self):
        print("CURRENT RESOURCES NODE.")
        for k in self.data.current_resources_node_dict.keys():
            print(k, self.data.current_resources_node_dict[k])
        print()

    def log_weight_file_edge(self):
        print("WEIGHT.")
        for f,filename in enumerate(self.data.key_index_file):
            print(filename.upper())
            for i in range(len(self.data.key_index_all)):
                for j in range(len(self.data.key_index_all)):
                    print(str(self.data.weight_file_edge[f][i][j]).format(), end=" ")
                print()
            print()
        print()

    def log_weight_dict(self):
        print("WEIGHT.")
        for k in self.data.weight_dict.keys():
            print(k, self.data.weight_dict[k])
        print()
