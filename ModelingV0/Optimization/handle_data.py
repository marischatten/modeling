from data import Data


class HandleData():

    data = Data()

    def __init__(self,data):
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

    def generate_rtt(self, bottom, top):
        pass
