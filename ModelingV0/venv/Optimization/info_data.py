from data import Data
from handle_data import HandleData
from optimize_data import OptimizeData

class InfoData(Data):

    #Parameters

    #Vars
    def log_bandwidth_actual_edge(self):
        for i in range(len(key_index_orig)):
            for j in range(len(key_index_dest)):
                print(bandwidth_actual_edge[i][j],end=" ")
            print()

    def log_map_node_file(self):
        for f in range(len(key_index_file)):
            for i in range(len(key_index_orig)):
                print(map_node_file[f][i],end=" ")
            print()

    def log_actual_resources_node(self):
        for i in range(len(key_index_orig)):
            print(actual_resources_node[i])

    def log_weight_file_edge(self):
        for f in range(len(key_index_file)):
            for i in range(len(key_index_orig)):
                for j in range(len(key_index_dest)):
                    print(weight_file_edge[f][i][j], end=" ")
                print()
            print()
            print()