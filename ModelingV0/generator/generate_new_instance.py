# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
# pip install tqdm
# pip install scipy
# pip install seaborn
import numpy as np

import time
import tqdm
import seaborn as sns
from scipy import special
import statistics as s

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
from ortools.graph import pywrapgraph

import igraph as ig
from modeling.optimize import *
import matplotlib.pyplot as plt

from utils import utils as u
from simulation import request as r

NO_EDGE = 99999
INTERFERENCE = 20
DISTANCE_MBS_MBS = 550
MAX_USE_NODE = 0.5

DISTANCE_SBS_MBS = [88.02,
                    87.53,
                    78.13,
                    97.13,
                    202.16,
                    202.97,
                    217.12,
                    215.23,
                    199.8,
                    215.89,
                    217.73,
                    224.54,
                    223.6,
                    222.29,
                    216.1
                    ]

mobility_rate = 0
alpha = 0
beta = 0

num_bs = 0
num_mbs = 0
num_sbs_per_mbs = 0
num_ue = 0
num_files = 0
num_nodes = 0  # sem vértices de conteúdo. BS + UE
key_index_file = list()
key_index_bs = list()
key_index_ue = list()
key_index_bs_ue = list()
key_index_all = list()
e_bs_adj = list()

resources_file = list()
size_file = list()
phi = list()
throughput_min_file = list()

resources_node = list()

rtt_min = list()

distance_ue = list()
distance_bs = list()

gama = list()
radius_mbs = 0
radius_sbs = 0

resources_node_max = 0
resources_node_min = 0

size_file_max = 0
size_file_min = 0
resources_file_max = 0
resources_file_min = 0

rtt_min_mbs_mbs = 0
rtt_min_sbs_mbs = 0
rtt_min_sbs_ue = 0


def main():
    path = r"..\dataset\instance_8.json"  # args[0]
    global mobility_rate, alpha, beta, num_sbs_per_mbs, num_bs, num_mbs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, key_index_bs_ue, e_bs_adj, resources_file, size_file, phi, throughput_min_file, resources_node, rtt_min, gama, distance_ue, distance_bs, radius_mbs, radius_sbs, rtt_min_mbs_mbs, rtt_min_sbs_mbs, rtt_min_sbs_ue, num_nodes, size_file_min, size_file_max, resources_node_min, resources_node_max, resources_file_min, resources_file_max, key_index_all

    mobility_rate = 10
    alpha = 0.5
    beta = 0.1
    num_mbs = 3
    num_sbs_per_mbs = 15
    num_bs = num_mbs + (num_mbs * num_sbs_per_mbs)
    num_files = 20
    num_ue = 200
    num_nodes = num_bs + num_ue + num_files
    size_file_max = 400
    size_file_min = 100
    resources_file_max = 400
    resources_file_min = 100

    resources_node_max = 2048
    resources_node_min = 1024
    radius_mbs = 300
    radius_sbs = 150
    rtt_min_mbs_mbs = 1.0
    rtt_min_sbs_mbs = 3.0
    rtt_min_sbs_ue = 5.0

    generate_nodes(num_files, num_mbs, num_sbs_per_mbs, num_ue)
    key_index_all = key_index_bs + key_index_ue + key_index_file
    generate_resources_file()
    generate_size_file()
    generate_throughput_min()

    generate_distance_ue()
    generate_e_bs_adj()

    generate_resources_node()
    generate_gama()
    generate_phi()

    generate_distance_ue()
    generate_e_bs_adj()
    generate_rtt_min()

    generate_json(path)


def generate_throughput_min():
    global throughput_min_file
    throughput_min_file = [0 for f in range(num_files)]
    for f in range(num_files):
        throughput_min_file[f] = 25

    print("THROUGHPUT MÍNIMA DO CONTEÚDO.")
    for f in range(num_files):
        print(throughput_min_file[f], end=" ")
    print()


def generate_gama():
    global gama
    gama = [[0 for i in range(num_bs + num_ue)] for f in range(num_files)]
    for f in range(len(key_index_file)):
        # retorna inteiros com uma distribuição uniforme discreta
        i = np.random.randint(0, num_bs - 1)
        gama[f][i] = 1

    print("HOSPEDAGEM DE CONTEÚDO.GAMA.")
    for f in range(len(key_index_file)):
        for i in range(len(key_index_bs)):
            print(gama[f][i], end=" ")
        print()
    print()


def generate_distance_ue():
    global distance_ue
    distance_ue = [[0.0 for i in range(num_bs)] for u in range(num_ue)]
    max_ran = ((2 * radius_mbs) * num_mbs) - INTERFERENCE

    for u in range(num_ue):
        for i in range(num_mbs, num_bs):
            dist = s.NormalDist(-radius_sbs, radius_sbs).samples(1, seed=None)[0]
            if dist > max_ran:
                dist = max_ran
            # distance_ue[u][i] = float(np.around(abs(np.random.normal(1, max_ran, 1)), 2))
            distance_ue[u][i] = float(np.around(abs(dist), 2))

    for u in range(num_ue):
        for i in range(num_mbs):
            distance_ue[u][i] = float(radius_mbs + 1)

    print("DISTÂNCIA ENTRE UE E SBS.")
    for u in range(len(key_index_ue)):
        for i in range(len(key_index_bs)):
            print(distance_ue[u][i], end=" ")
        print()
    print()

    # basear no numero de macros e definir como distÂncia maxima os extremos da rede acesso com base nos raios das mbs
    # definir distancias fixas para sbs e mbs


def generate_e_bs_adj():
    global e_bs_adj
    e_bs_adj = [[0 for i in range(num_bs)] for u in range(num_bs)]
    count = 0
    control = num_mbs

    for i in range(num_mbs):
        for j in range(num_mbs):
            if i != j:
                e_bs_adj[i][j] = 1

    for i in range(num_mbs):
        for j in range(control, num_bs):
            if i != j:
                if count < num_sbs_per_mbs:
                    e_bs_adj[i][j] = 1
                    e_bs_adj[j][i] = 1
                    count += 1
        control += count
        count = 0

    print("ADJACÊNCIA ENTRE BS.")
    for i in range(len(key_index_bs)):
        for j in range(len(key_index_bs)):
            print(e_bs_adj[i][j], end=" ")
        print()
    print()


def generate_resources_node():
    global resources_node
    resources_node = [0 for f in range(num_bs)]
    for i, tag_i in enumerate(key_index_bs):
        if tag_i[:3] == 'MBS':
            resources_node[i] = resources_node_max
        if tag_i[:3] == 'SBS':
            resources_node[i] = resources_node_min

    print("CAPACIDADE DA BS.")
    for i in range(num_bs):
        print(resources_node[i], end=" ")
    print()


def generate_phi():
    # alocar até 30% da capacidade de acordo com o gama
    global phi
    use = 0
    phi = [[0 for i in range(num_bs + num_ue)] for f in range(num_files)]

    for f in range(num_files):
        for i in range(num_bs):
            sum_files = 0
            if gama[f][i] == 1:
                rep = int(np.random.randint(1, 2))

                for file in range(num_files):
                    if 0 != phi[file][i]:
                        sum_files += (resources_file[file] * phi[file][i])

                use = ((sum_files + (resources_file[f] * rep)) / resources_node[i])

                if use <= MAX_USE_NODE:
                    phi[f][i] += rep

    print("CONTEÚDO EM ENVIO.PHI.")
    for f in range(len(key_index_file)):
        for i in range(len(key_index_bs)):
            print(phi[f][i], end=" ")
        print()
    print()


def generate_resources_file():
    global resources_file
    resources_file = [0 for f in range(num_files)]
    for f in range(num_files):
        resources_file[f] = np.random.randint(resources_file_min, resources_file_max)

    print("RECURSOS DO CONTEÚDO.")
    for f in range(num_files):
        print(resources_file[f], end=" ")
    print()


def generate_size_file():
    global size_file
    size_file = [0 for f in range(num_files)]
    for f in range(num_files):
        size_file[f] = np.random.randint(size_file_min, size_file_max)

    print("TAMANHO DO CONTEÚDO.")
    for f in range(num_files):
        print(size_file[f], end=" ")
    print()


def generate_rtt_min():
    global rtt_min
    rtt_min = [[NO_EDGE for i in range(num_nodes)] for j in range(num_nodes)]
    for i, tag_i in enumerate(key_index_all):
        for j, tag_j in enumerate(key_index_all):
            if i != j:
                if tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS':
                    if coverage_bs_to_bs(tag_i,tag_j):
                        rtt_min[i][j] = rtt_min_mbs_mbs
                        rtt_min[j][i] = rtt_min_mbs_mbs
                    else:
                        rtt_min[i][j] = NO_EDGE
                        rtt_min[j][i] = NO_EDGE
                if (tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS'):
                    if coverage_bs_to_bs(tag_i,tag_j):
                        rtt_min[i][j] = rtt_min_sbs_mbs
                        rtt_min[j][i] = rtt_min_sbs_mbs
                    else:
                        rtt_min[i][j] = NO_EDGE
                        rtt_min[j][i] = NO_EDGE
                if (tag_i[:3] == 'SBS' and tag_j[:2] == 'UE'):
                    if coverage_bs_ue(tag_i,tag_j):
                        rtt_min[i][j] = rtt_min_sbs_ue
                    else:
                        rtt_min[i][j] = NO_EDGE
                if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                    if caching_to_bs(tag_i,tag_j):
                        rtt_min[i][j] = 0
                    else:
                        rtt_min[i][j] = NO_EDGE
            else:
                rtt_min[i][j] = NO_EDGE
                rtt_min[j][i] = NO_EDGE

    print("RTT MÍNIMO POR ENLACE.")
    for i in range(num_nodes):
        for j in range(num_nodes):
            if rtt_min[i][j] == NO_EDGE:
                print(' ထ ', end=" ")
            else:
                print(rtt_min[i][j], end=" ")
        print()
    print()


def coverage_bs_to_bs(source, sink):
    e_bs_adj_dict = dict()
    for i in range(len(key_index_bs)):
        for j in range(len(key_index_bs)):
            tag_orig = key_index_bs[i]
            tag_dest = key_index_bs[j]
            e_bs_adj_dict[tag_orig, tag_dest] = e_bs_adj[i][j]
    return e_bs_adj_dict[source,sink] == 1


def coverage_bs_ue(source,sink):
    distance_ue_dict = dict()
    for u in range(len(key_index_ue)):
        for i in range(len(key_index_bs)):
            tag_ue = key_index_ue[u]
            tag_bs = key_index_bs[i]
            distance_ue_dict[tag_ue, tag_bs] = distance_ue[u][i]

    return distance_ue_dict[sink,source] <= radius_sbs


def caching_to_bs(source,sink):
    gama_dict = dict()
    for f in range(len(key_index_file)):
        for i in range(len(key_index_bs)):
            tag_file = key_index_file[f]
            tag_bs = key_index_bs[i]
            gama_dict[tag_file, tag_bs] = gama[f][i]
    return gama_dict[source, sink] == 1


def generate_nodes(num_contents, num_mbs, num_sbs, num_users):
    global key_index_bs_ue
    generate_contents(num_contents)
    generate_users(num_users)
    generate_bs(num_mbs, num_sbs)
    key_index_bs_ue = key_index_bs + key_index_ue


def generate_contents(num_contents):
    global key_index_file
    for i in range(1, num_contents + 1):
        tag = "F" + str(i)
        key_index_file.append(tag)


def generate_users(num_users):
    global key_index_ue
    for i in range(1, num_users + 1):
        tag = "UE" + str(i)
        key_index_ue.append(tag)


def generate_bs(num_mbs, num_sbs):
    generate_mbs(num_mbs)
    generate_sbs(num_mbs, num_sbs)


def generate_mbs(num_mbs):
    for i in range(1, num_mbs + 1):
        tag = "MBS" + str(i)
        key_index_bs.append(tag)


def generate_sbs(num_mbs, num_sbs):
    count = 1
    for i in range(1, num_mbs + 1):
        for j in range(1, num_sbs + 1):
            tag = "SBS" + str(count)
            key_index_bs.append(tag)
            count += 1


def generate_json(path):
    data = {"mobility_rate": mobility_rate,
            "alpha": alpha,
            "beta": beta,
            "num_bs": num_bs,
            "num_ue": num_ue,
            "num_files": num_files,
            "key_index_file": key_index_file,
            "key_index_bs": key_index_bs,
            "key_index_ue": key_index_ue,
            "resources_file": resources_file,
            "size_file": size_file,
            "throughput_min_file": throughput_min_file,
            "resources_node": resources_node,
            "gama": gama,
            "phi": phi,
            "rtt_min": rtt_min,
            "distance_ue": distance_ue,
            "distance_bs": distance_bs,
            "e_bs_adj": e_bs_adj,
            "radius_mbs": radius_mbs,
            "radius_sbs": radius_sbs
            }
    u.write_data(path, data)


if __name__ == "__main__":
    main()
