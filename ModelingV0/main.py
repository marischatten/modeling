# python -m pip install -i https://pypi.gurobi.com gurobipy
from optimization.optimize import Data
from optimization.optimize import HandleData
from optimization.optimize import InfoData
from optimization.optimize import OptimizeData
from utils import utils as u


alpha = None

num_bs = None
num_ue = None
num_files = None

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

size_file = list()
resources_file = list()
bandwidth_min_file = list()

resources_node = list()

file_user_request = [[0] * 5] * 3

total_bandwidth_edge = [[0] * 5] * 5

min_rtt = None
max_rtt = None


def main():

    path = r'..\dataset\instance_1.json' #args[0]
    dataset = u.get_data(path)
    convert_to_object(dataset)

    d = Data(alpha, num_bs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, size_file, resources_file,
            bandwidth_min_file,
            resources_node, file_user_request, total_bandwidth_edge, min_rtt, max_rtt)
    hd = HandleData(d)
    id = InfoData(d)
    od = OptimizeData(d)


def convert_to_object(dataset):
    alpha = int(dataset["alpha"])

    num_bs = int(dataset["num_bs"])
    num_ue = int(dataset["num_ue"])
    num_file = int(dataset["num_file"])

    key_index_file = dataset["key_index_file"]
    key_index_bs = dataset["key_index_bs"]
    key_index_ue = dataset["key_index_ue"]

    size_file = dataset["size_file"]
    resources_file = dataset["resources_file"]
    bandwidth_min_file = dataset["bandwidth_min_file"]

    resources_node = dataset["resources_node"]

    file_user_request = dataset["file_user_request"]

    total_bandwidth_edge = dataset["total_bandwidth_edge"]

    min_rtt = int(dataset["min_rtt"])
    max_rtt = int(dataset["max_rtt"])


if __name__ == "__main__":
    main()
