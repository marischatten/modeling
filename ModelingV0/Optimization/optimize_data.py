from data import Data
import gurobipy as gp


class OptimizeData(Data):
    model = None
    n = None

    def create_model(self):
        model = gp.Model("Orchestrator")

    # n_fij \in {0,1}
    def create_vars(self):
        n = self.model.addVars(self.key_index_file, self.key_index_orig, self.key_index_dest, vtype=gp.GRB.BINARY)

    def set_function_objective(self):
        self.model.setObjective(gp.quicksum(
            n[f, i, j] * self.weight_file_edge[f][i][j] for f in self.key_index_file for i in self.key_index_orig for j
            in self.key_index_dest),
                                sense=gp.GRB.MINIMIZE
                                )

    def create_constraints(self):
        c1 = self.model.addConstrs(self.resources_node[i]
                                   >= self.actual_resources_node[i] for i in self.key_index_orig)

        c2 = self.model.addConstrs(self.total_bandwidth_edge[i][j]
                                   >= self.bandwidth_actual_edge[i][j] for i in self.key_index_orig for j in
                                   self.key_index_dest)

        c3 = self.model.addConstrs(
            (self.bandwidth_actual_edge[i][j] for i in self.key_index_orig for j in self.key_index_dest)
            >=
            gp.quicksum(
                self.file_resource[f] * n[f, i, j] for f in self.key_index_file for i in self.key_index_orig for j in
                self.key_index_dest))

        c4 = self.model.addConstrs(0
                                   <= self.weight_edge_file[f][i][j]
                                   <= 1 for f in self.key_index_file for i in self.key_index_orig for j in
                                   self.key_index_dest)

        c5 = self.model.addConstrs(gp.quicksum(self.map_node_file[f][i] for i in self.key_index_bs)
                                   <= 2 for f in self.key_index_file)

        c6 = self.model.addConstrs(
            gp.quicksum(n[f, i, j] for i in self.key_index_orig for j in self.key_index_dest)
            >= 1 for f in self.key_index_file)

        c7 = self.model.addConstrs(
            gp.quicksum(n[f, i, j] for i in self.key_index_orig for j in self.key_index_dest)
            <= abs(self.key_index_orig * self.key_index_dest) for f in self.key_index_file)

        c8 = self.model.addConstrs()

        # c9 = model.addConstrs(gp.quicksum(n[f,i,j] for i in key_index_orig) - gp.quicksum(n[f,k,i] for k in key_index_orig) == 1 if i == f -1 if i==u else 0)

    def execute(self):
        self.model.optimize()
