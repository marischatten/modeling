from info_data import InfoData
from handle_data import HandleData
from data import Data

import gurobipy as gp

class Optimize(Data):

    model = null

    def create_model(self):
        model = gp.Model("Orchestrator")

    #n_fij \in {0,1}
    def create_vars(self):
        n = model.addVars(key_index_file,key_index_orig,key_index_dest,vtype=gp.GRB.BINARY)

    def set_function_objetive(self):
        model.setObjective(gp.quicksum(n[f,i,j] * weight_file_edge[f][i][j] for f in key_index_file for i in key_index_orig for j in key_index_dest) ,
                           sense=gp.GRB.MINIMIZE
                           )

    def create_constraints(self):
        c1 = model.addConstrs(resources_node[i]
                              >= actual_resources_node[i] for i in key_index_orig)

        c2 = model.addConstrs(total_bandwidth_edge[i][j]
                              >= bandwidth_actual_edge[i][j] for i in key_index_orig for j in key_index_dest )

        c3 = model.addConstrs((bandwidth_actual_edge[i][j] for i in key_index_orig for j in key_index_dest)
                              >=
                              gp.quicksum(file_resource[f] * n[f, i, j] for f in key_index_file for i in key_index_orig for j in key_index_dest))

        c4 = model.addConstrs( 0
            <= weight_edge_file[f][i][j]
            <= 1 for f in key_index_file for i in key_index_orig for j in key_index_dest)

        c5 = model.addConstrs(gp.quicksum(map_node_file[f][i] for i in key_index_bs)
                              <= 2 for f in key_index_file )

        c6 = model.addConstrs(
            gp.quicksum(n[f, i, j] for i in key_index_orig for j in key_index_dest)
            >= 1 for f in key_index_file)

        c7 = model.addConstrs(
            go.quicksum(n[f, i, j] for i in key_index_orig for j in key_index_dest)
            <= abs(key_index_orig * key_index_dest) for f in key_index_file)


        c8 = model.addConstrs()

        #c9 = model.addConstrs(gp.quicksum(n[f,i,j] for i in key_index_orig) - gp.quicksum(n[f,k,i] for k in key_index_orig) == 1 if i == f -1 if i==u else 0)

    def execute(self):
        model.optimize()