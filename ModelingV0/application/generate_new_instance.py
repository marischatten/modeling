import os
from random import randrange

import numpy as np
import statistics as s
from utils import utils as u
from optimization import optimize as opt

NO_EDGE = 99999
MAX_COVERAGE_PER_UE = 2
MAX_USE_NODE = 0.5
NUM_CLOUD = 1
MAX_GAMA = 32 # WARNING
TO_GB = 1000
TO_MB = 8
mobility_rate = 0
alpha = 0
beta = 0
num_bs = 0
num_mbs = 0
num_sbs_per_mbs = 0
num_ue = 0
num_files = 0
num_nodes = 0  # BS + UE + C
key_index_file = list()
key_index_bs = list()
key_index_ue = list()
key_index_bs_ue = list()
key_index_all = list()
e_bs_adj = list()


size_file = list()
buffer_file = list()
throughput_min_file = list()

resources_node = list()

rtt_min = list()
rtt_edge = list()

distance_ue_dict = dict()
distance_ue = list()
distance_bs = list()

gama = list()
radius_mbs = 0
radius_sbs = 0

storage_node_max = 0
storage_node_min = 0
storage_cloud = 0

# Size - Throughput - Resources
requirements = 0

rtt_min_cloud_mbs = 0
rtt_min_mbs_mbs = 0
rtt_min_sbs_mbs = 0
rtt_min_sbs_ue = 0

path = ''


def main():
    if os.name == 'nt':
        path_config = r'../config/config_generator_instance.json'
    else:
        path_config = r'../config/config_generator_instance.json'

    if path_config != '':
        config = u.get_data(path_config)
        load_config(config)

    global key_index_all
    generate_nodes(num_files, num_mbs, num_sbs_per_mbs, num_ue)
    key_index_all = key_index_bs + key_index_ue + key_index_file
    generate_requirements()
    generate_distance_ue()
    generate_e_bs_adj()
    generate_resources_node()
    generate_gama()
    generate_rtt_min()
    generate_rtt()
    generate_json(path)
    print("Success generating instance!")


def generate_gama():
    global gama
    gama = [[0 for i in range(num_bs + num_ue)] for f in range(num_files)]
    for f in range(len(key_index_file)):
        # retorna inteiros com uma distribuição uniforme discreta
        max =  MAX_GAMA
        while max != 0:
            i = np.random.randint(NUM_CLOUD, num_bs+1)
            while gama[f][i] == 1:
                i = np.random.randint(NUM_CLOUD, num_bs+1)
            gama[f][i] = 1
            max -= 1

    for f in range(len(key_index_file)):
        gama[f][0] = 1

    print("HOSPEDAGEM DE CONTEÚDO.GAMA.")
    for f in range(len(key_index_file)):
        for i in range(len(key_index_bs)):
            print(gama[f][i], end=" ")
        print()
    print()


def generate_distance_ue():
    global distance_ue
    distance_ue = [[0.0 for i in range(num_bs + NUM_CLOUD)] for u in range(num_ue)]

    for u in range(num_ue):

        bs_coverage = list()
        num_coverage = randrange(1, MAX_COVERAGE_PER_UE + 1)
        for i in range(num_coverage):
            bs_coverage.append(randrange(0,len(key_index_bs)))
            while key_index_bs[bs_coverage[-1]][:3] == 'MBS':
                bs_coverage[-1] = randrange(0, len(key_index_bs))

        # without coverage.
        for i in range(num_mbs + NUM_CLOUD, num_bs + NUM_CLOUD):
            dist = randrange(radius_sbs+1, (2*radius_sbs))
            distance_ue[u][i] = float(round(abs(dist), 2))

        # with coverage
        for i in bs_coverage:
            dist = randrange(1, radius_sbs)
            distance_ue[u][i] = float(round(abs(dist), 2))

        # ue to mbs and cloud
        for i in range(num_mbs + NUM_CLOUD):
            distance_ue[u][i] = float(radius_mbs + 1)

    print("DISTÂNCIA ENTRE UE E SBS.")
    for u in range(len(key_index_ue)):
        for i in range(len(key_index_bs)):
            print(distance_ue[u][i], end=" ")
        print()
    print()


def generate_e_bs_adj():
    global e_bs_adj
    e_bs_adj = [[0 for i in range(num_bs + NUM_CLOUD)] for u in range(num_bs + NUM_CLOUD)]
    count = 0
    control = num_mbs + NUM_CLOUD

    for i in range(num_mbs+NUM_CLOUD):
        for j in range(num_mbs+NUM_CLOUD):
            if i != j:
                e_bs_adj[i][j] = 1

    for i in range(NUM_CLOUD, num_mbs+NUM_CLOUD):
        for j in range(control, num_bs + NUM_CLOUD):
            if i != j:
                if count < num_sbs_per_mbs:
                    e_bs_adj[i][j] = 1
                    e_bs_adj[j][i] = 1
                    count += 1
        control += count
        count = 0

    for i in range(num_bs + NUM_CLOUD):
        e_bs_adj[i][0] = 0

    print("ADJACÊNCIA ENTRE BS.")
    for i in range(len(key_index_bs)):
        for j in range(len(key_index_bs)):
            print(e_bs_adj[i][j], end=" ")
        print()
    print()


def generate_resources_node():
    global resources_node
    resources_node = [0 for f in range(num_bs + NUM_CLOUD)]
    for i, tag_i in enumerate(key_index_bs):
        if tag_i[:3] == 'MBS':
            resources_node[i] = storage_node_max
        if tag_i[:3] == 'SBS':
            resources_node[i] = storage_node_min

    resources_node[0] = sum(size_file)
    print("CAPACIDADE DA BS. MB.")
    for i in range(num_bs + NUM_CLOUD):
        print(round(resources_node[i]/TO_MB,0), end=" ")
    print()


def generate_requirements():
    global size_file, buffer_file, throughput_min_file
    size_file = [0 for f in range(num_files)]
    buffer_file = [0 for f in range(num_files)]
    throughput_min_file = [0 for f in range(num_files)]

    for f in range(num_files):
        index = np.random.randint(0, len(requirements))
        size_file[f] = requirements[index][0]
        buffer_file[f] = requirements[index][1]
        throughput_min_file[f] = requirements[index][2]

    print("TAMANHO DO CONTEÚDO.MB.")
    for f in range(num_files):
        print(round(size_file[f] / TO_MB, 0), end=" ")
    print()

    print("TAMANHO DO BUFFER.GB.")
    for f in range(num_files):
        print(round(buffer_file[f] * TO_GB, 0), end=" ")
    print()

    print("THROUGHPUT MÍNIMA DO CONTEÚDO.Mbps")
    for f in range(num_files):
        print(throughput_min_file[f], end=" ")
    print()


def generate_rtt_min():
    global rtt_min
    rtt_min = [[NO_EDGE for i in range(num_nodes)] for j in range(num_nodes)]
    for i, tag_i in enumerate(key_index_all):
        for j, tag_j in enumerate(key_index_all):
            if i != j:
                if tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS':
                    if coverage_bs_to_bs(tag_i, tag_j):
                        rtt_min[i][j] = rtt_min_mbs_mbs
                        rtt_min[j][i] = rtt_min_mbs_mbs
                if (tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS'):
                    if coverage_bs_to_bs(tag_i, tag_j):
                        rtt_min[i][j] = rtt_min_sbs_mbs
                        rtt_min[j][i] = rtt_min_sbs_mbs
                if (tag_i[:3] == 'SBS' and tag_j[:2] == 'UE'):
                    if coverage_bs_ue(tag_i, tag_j):
                        rtt_min[i][j] = rtt_min_sbs_ue
                if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                    if caching_to_bs(tag_i, tag_j):
                        rtt_min[i][j] = 0
                if tag_i[:3] == 'MBS' and tag_j[:4] == 'MBS0':
                    rtt_min[i][j] = NO_EDGE
                    rtt_min[j][i] = rtt_min_cloud_mbs


    print("RTT MÍNIMO POR ENLACE.")
    for i in range(num_nodes):
        for j in range(num_nodes):
            if rtt_min[i][j] == NO_EDGE:
                print(' ထ ', end=" ")
            else:
                print(rtt_min[i][j], end=" ")
        print()
    print()


def generate_rtt():
    global rtt_edge
    rtt_edge = [[NO_EDGE for i in range(num_nodes + num_files)] for j in
                range(num_nodes + num_files)]

    for i, tag_i in enumerate(key_index_all):
        for j, tag_j in enumerate(key_index_all):
            if i != j:
                if (tag_i[:3] == 'MBS' and tag_j[:3] == 'MBS') or (tag_i[:3] == 'SBS' and tag_j[:3] == 'MBS') or (
                        tag_i[:3] == 'MBS' and tag_j[:3] == 'SBS') or (
                        tag_i[:3] == 'SBS' and tag_j[:3] == 'SBS'):
                    if coverage_bs_to_bs(tag_i, tag_j):
                        rtt_edge[i][j] = rtt_min[i][j]
                        rtt_edge[j][i] = rtt_min[j][i]
                if (tag_i[:3] == 'SBS' and tag_j[:2] == 'UE'):
                    rtt_edge[i][j] = calc_rtt_bs_to_ue_increase(tag_i,tag_j,
                                                                rtt_min[
                                                                    i][j])
                if (tag_i[:1] == 'F' and tag_j[:3] == 'MBS') or (tag_i[:1] == 'F' and tag_j[:3] == 'SBS'):
                    if caching_to_bs(tag_i, tag_j):
                        rtt_edge[i][j] = 0

    print("RTT POR ENLACE.")
    for i in range(num_nodes):
        for j in range(num_nodes):
            if rtt_edge[i][j] == NO_EDGE:
                print(' ထ ', end=" ")
            else:
                print(rtt_edge[i][j], end=" ")
        print()
    print()


def calc_rtt_bs_to_ue_increase(bs, ue, rtt_previous):
    rtt = 0
    if coverage_bs_ue(bs, ue):
        rtt = round(rtt_previous * (1 + (distance_ue_dict[ue, bs] / radius_sbs)), 4)
    else:
        rtt = NO_EDGE
    return rtt


def coverage_bs_to_bs(source, sink):
    e_bs_adj_dict = dict()
    for i in range(len(key_index_bs)):
        for j in range(len(key_index_bs)):
            tag_orig = key_index_bs[i]
            tag_dest = key_index_bs[j]
            e_bs_adj_dict[tag_orig, tag_dest] = e_bs_adj[i][j]
    return e_bs_adj_dict[source, sink] == 1


def coverage_bs_ue(source, sink):
    global distance_ue_dict
    for u in range(len(key_index_ue)):
        for i in range(len(key_index_bs)):
            tag_ue = key_index_ue[u]
            tag_bs = key_index_bs[i]
            distance_ue_dict[tag_ue, tag_bs] = distance_ue[u][i]

    return distance_ue_dict[sink, source] <= radius_sbs


def caching_to_bs(source, sink):
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
    generate_cloud_server()
    generate_mbs(num_mbs)
    generate_sbs(num_mbs, num_sbs)


def generate_cloud_server():
    key_index_bs.append("MBS0")


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
            "rtt_min_cloud_mbs": rtt_min_cloud_mbs,
            "rtt_min_mbs_mbs": rtt_min_mbs_mbs,
            "rtt_min_sbs_mbs": rtt_min_sbs_mbs,
            "rtt_min_sbs_ue": rtt_min_sbs_ue,
            "num_bs": num_bs,
            "num_ue": num_ue,
            "num_files": num_files,
            "num_mbs": num_mbs,
            "num_sbs": num_sbs_per_mbs * num_mbs,

            "key_index_file": key_index_file,
            "key_index_bs": key_index_bs,
            "key_index_ue": key_index_ue,

            "size_file": size_file,
            "buffer_file": buffer_file,
            "throughput_min_file": throughput_min_file,

            "resources_node": resources_node,
            "gama": gama,
            "rtt_edge": rtt_edge,
            "distance_ue": distance_ue,
            "distance_bs": distance_bs,
            "e_bs_adj": e_bs_adj,
            "radius_mbs": radius_mbs,
            "radius_sbs": radius_sbs
            }
    u.write_data(path, data)


def load_config(config: object):
    global mobility_rate, alpha, beta, num_sbs_per_mbs, num_bs, num_mbs, num_ue, num_files, key_index_file, key_index_bs, key_index_ue, key_index_bs_ue, e_bs_adj, size_file, throughput_min_file, resources_node, rtt_min, gama, distance_ue, distance_bs, radius_mbs, radius_sbs, rtt_min_cloud_mbs, rtt_min_mbs_mbs, rtt_min_sbs_mbs, rtt_min_cloud_mbs, rtt_min_mbs_mbs, rtt_min_sbs_mbs, rtt_min_sbs_ue, num_nodes, requirements, storage_node_min, storage_node_max, key_index_all, path

    mobility_rate = config["mobility_rate"]
    alpha = config["alpha"]
    beta = config["beta"]
    num_mbs = config["num_mbs"]
    num_sbs_per_mbs = config["num_sbs_per_mbs"]
    num_bs = num_mbs + (num_mbs * num_sbs_per_mbs)
    num_files = config["num_files"]
    num_ue = config["num_ue"]
    num_nodes = num_bs + num_ue + num_files + NUM_CLOUD
    requirements = config["requirements"]

    storage_node_max = config["storage_node_max"]
    storage_node_min = config["storage_node_min"]

    radius_mbs = config["radius_mbs"]
    radius_sbs = config["radius_sbs"]
    rtt_min_cloud_mbs = config["rtt_min_cloud_mbs"]
    rtt_min_mbs_mbs = config["rtt_min_mbs_mbs"]
    rtt_min_sbs_mbs = config["rtt_min_sbs_mbs"]
    rtt_min_sbs_ue = config["rtt_min_sbs_ue"]

    path = config["path"]

    print(opt.CYAN, "LOADED CONFIGURATION.", opt.RESET)


if __name__ == "__main__":
    main()
