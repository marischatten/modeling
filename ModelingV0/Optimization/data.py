from info_data import InfoData
from handle_data import HandleData
from optimize_data import OptimizeData


class Data():
    id = InfoData()
    hd = HandleData()
    od = OptimizeData()

    # Input
    alpha = None

    # Parameters

    num_bs = None
    num_ue = None
    num_nodes = None
    num_files = None

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

    def __init__(self, alpha, num_bs, num_ue, num_file, key1, key2, key3, fs, fr, bwf, rt_i, fu, bwt_ij, min_rtt,
                 max_rtt):
        self.alfa = alpha
        self.num_bs = num_bs
        self.num_ue = num_ue
        self.num_nodes = num_bs + num_ue
        self.num_files = num_file
        self.key_index_file = key1
        self.key_index_bs = key2
        self.key_index_ue = key3
        self.key_index_orig = key_index_dest = key2 + key3
        self.size_file = fs
        self.resources_file = fr
        self.bandwidth_min_file = bwf
        self.resources_node = rt_i
        self.file_user_request = fu
        self.edge_rtt = self.hd.generate_rtt(min_rtt, max_rtt)
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
