from data import Data
from random import choices


class HandleData(Data):

    def calc_bandwidth_actual_edge(self):
        for i in range(len(self.key_index_orig)):
            for j in range(len(self.key_index_dest)):
                for f in range(len(self.key_index_file)):
                    size_f = self.size_file[f]
                    rtt_ij = self.edge_rtt[i][j]
                    self.bandwidth_actual_edge[i][j] = round(size_f / rtt_ij, 4)

    def calc_map_file(file, orig, dest):
        self.map_node_file[file][orig] = 0
        self.map_node_file[file][dest] = 1

    def calc_actual_resources_node(self):
        node = 0
        sum_users = 0
        for f in range(len(self.key_index_file)):
            for i in range(len(self.key_index_orig)):
                if (self.map_node_file[f][i] == 1):
                    for i in range(len(self.key_index_orig)):
                        sum_users += self.file_user_request[f][i]
                        node += sum_users * self.resources_file[f]
                    sum_users = 0
            self.actual_resources_node[i] = node
            node = 0

    def calc_weight_file_edge(self):
        for i in range(len(self.key_index_orig)):
            for j in range(len(self.key_index_dest)):
                for f in range(len(self.key_index_file)):
                    rt_i = self.resources_node[i]
                    rr_i = self.actual_resources_node[i]
                    bwa_ij = self.bandwidth_actual_edge[i][j]
                    bwt_ij = self.total_bandwidth_edge[i][j]
                    if rt_i != 0 and bwt_ij != 0 and rr_i != 0 and bwa_ij != 0:
                        weight = ((self.alpha * (rr_i / rt_i)) + ((1 - self.alpha) * (bwa_ij / bwt_ij))) / (
                                    self.alpha + (1 - self.alpha))
                        self.weight_file_edge[f][i][j] = round(weight, 4)
                    else:
                        self.weight_file_edge[f][i][j] = 1



    def generate_rtt(min, max):
        pass
'''    
        p150 = list()
        p200 = list()
        wmin = list()
        wmax = list()
        for i in range(150):
            p150.append(i)
            wmin.append(min)
        for i in range(200):
            p200.append(i)
            wmax.append(max)

        population = p150 + p200
        weights = wmin + wmax

        for i in range(5):
            for j in range(5):
                self.edge_rtt[i][j] = choices(population, weights, k=1)
'''
