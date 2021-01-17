from data import Data


class InfoData():

    data = Data()

    def __init__(self,data):
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
