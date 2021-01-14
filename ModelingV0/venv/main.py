#python -m pip install -i https://pypi.gurobi.com gurobipy
import gurobipy as gp

from Optimization.data import Data
from Optimization.info_data import InfoData
from Optimization.handle_data import HandleData
from Optimization.optimize_data import OptimizeData

def main():

    alpha = 0.5

    key_index_file = ['A','B','C']
    key_index_bs = ['I','J']
    key_index_ue = ['U','W','Z']

    size_file = [200,200,100]
    resources_file = [3,1,1]
    bandwidth_min_file = [50,50,50]

    resources_node = [3,4,0,0,0]

    file_user_request = [
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
    ]
    edge_rtt = [
        [9999, 4, 9999, 9999, 9999],
        [5, 9999, 9999, 9999, 9999],
        [7, 9999, 9999, 9999, 9999],
        [8, 20, 9999, 9999, 9999],
        [9999, 22, 9999, 9999, 9999]
    ]
    total_bandwidth_edge =  [
        [9999, 1024, 300, 300, 0],
        [1024, 9999, 0, 300, 300],
        [300, 0, 0, 0, 0],
        [300, 300, 0, 0, 0],
        [0, 300, 0, 0, 0]
    ]

    d = Data(alpha,beta,key_index_file,key_index_bs,key_index_ue,size_file,resources_file,bandwidth_min_file,resources_node,file_user_request,edge_rtt,total_bandwidth_edge)
    d.weight_to_dictionary()
    d.hd.calc_bandwidth_actual_edge()
    d.id.log_bandwidth_actual_edge()


if __name__ == "__main__":
    main()

