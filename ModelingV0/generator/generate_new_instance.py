# python -m pip install -i https://pypi.gurobi.com gurobipy
# pip install python-igraph
# pip install pycairo
# pip install ortools
# pip install numpy
# pip install matplotlib
# pip install tqdm
# pip install scipy
# pip install seaborn


import time
import tqdm
import seaborn as sns
from scipy import special

import ortools.linear_solver.pywraplp as otlp
from ortools.linear_solver import pywraplp  # https://developers.google.com/optimization/introduction/python
from ortools.graph import pywrapgraph

import igraph as ig
from modeling.optimize import *
import matplotlib.pyplot as plt

from utils import utils as u
from simulation import request as r

alpha = 0
beta = 0

num_bs = 0
num_ue = 0
num_files = 0

key_index_file = list()
key_index_bs = list()
key_index_ue = list()

e_bs_adj = list()

resources_file = list()
phi = list()
bandwidth_min_file = list()

resources_node = list()

rtt_base = list()

distance_ue = list()
distance_bs = list

gama = list()
radius_mbs = 0
radius_sbs = 0


def main():
    path = r'..\dataset\instance_3.json'  # args[0]
    generate_nodes(1, 2, 3, 4)
    generate_json(path)


def generate_json(path):
    u.write_data(path, alpha)
    u.write_data(path, beta)
    u.write_data(path, num_bs)
    u.write_data(path, num_ue)
    u.write_data(path, num_files)
    u.write_data(path, key_index_file)
    u.write_data(path, key_index_bs)
    u.write_data(path, key_index_bs)
    u.write_data(path, e_bs_adj)
    u.write_data(path, resources_file)
    u.write_data(path, phi)
    u.write_data(path, resources_node)
    u.write_data(path, rtt_base)
    u.write_data(path, distance_ue)
    u.write_data(path, distance_bs)
    u.write_data(path, gama)
    u.write_data(path, radius_mbs)
    u.write_data(path, radius_sbs)


def generate_nodes(num_contents, num_mbs, num_sbs, num_users):
    generate_contents(num_contents)
    generate_users(num_users)
    generate_bs(num_mbs, num_sbs)


def generate_contents(num_contents):
    for i in range(num_contents):
        tag = "F" + num_contents
        key_index_file.append(tag)


def generate_users(num_users):
    for i in range(num_users):
        tag = "UE" + num_users
        key_index_file.append(tag)


def generate_bs(num_mbs, num_sbs):
    generate_mbs(num_mbs)
    generate_sbs(num_sbs)


def generate_mbs(num_mbs):
    for i in range(num_mbs):
        tag = "MBS" + num_mbs
        key_index_file.append(tag)


def generate_sbs(num_sbs):
    for i in range(num_sbs):
        tag = "SBS" + num_sbs
        key_index_file.append(tag)


if __name__ == "__main__":
    main()
