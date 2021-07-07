## Model Config

show_log: This configuration show log in Gurobi optimization.

show_results: This configuration show Gurobi results.

show_path: This configuration show the complete path for request.

show_var: This configuration show parameters computed in real time.

show_par: This configuration shows the parameters entered through configuration file. 

plot_distribution: This configuration plot graph of Poison distribution requisitions and Zipf distribution of contents.

plot_data: 
show_all_paths: This configuration show the resume all paths,
type: "zipf
mobility: "is_mobile",
reallocation: "reallocation",
show_reallocation: false,
path_dataset: "..\\dataset\\instance_1.json",
save_data: false,
path_output: "..\\output\\data\\instance_1.xlsx",
plot_graph: true,
path_graph: "..\\output\\graph\\instance_6.png",

avg_qtd_bulk:5,
num_events: 5,
num_alpha: 0.56,

source: ["F2"],
sink: ["UE2"]

##Instance Generator Config

    "mobility_rate" : 10,
    "alpha" :  0.5,
    "beta" :  100,
    "num_mbs" :  2,
    "num_sbs_per_mbs" :  15,

    "num_files" :  100,
    "num_ue" :  200,

    "size_file_max" :  400,
    "size_file_min" :  100,
    "resources_file_max" :  400,
    "resources_file_min" :  100,

    "throughput_min_file_max" :  32,
    "throughput_min_file_min" :  16,

    "resources_node_max" :  2048,
    "resources_node_min" :  1024,
    "radius_mbs" :  300,
    "radius_sbs" :  150,
    "rtt_min_mbs_mbs" :  1.0,
    "rtt_min_sbs_mbs" :  3.0,
    "rtt_min_sbs_ue" :  5.0,

    "path: "..\\dataset\\instance_6.json"
