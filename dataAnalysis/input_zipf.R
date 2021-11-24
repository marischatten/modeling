input_zipf = function(){

  rate_admission04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Rate_Admission', col_names=TRUE))
  server_use04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Server_Use', col_names=TRUE))
  cache_vs_cloud04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='CacheVsCloud', col_names=TRUE))
  server_use_by_type04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Server_Use_By_Type', col_names=TRUE))
  scattering_optic04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Scattering_Optic', col_names=TRUE))
  scattering_wireless04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Scattering_Wireless', col_names=TRUE))
  load_links_optic04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Load_Links_Optic', col_names=TRUE))
  load_links_wireless04 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Load_Links_Wireless', col_names=TRUE))
  path_Realloc04 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Paths_Reallocation', col_names=TRUE))
  host_Realloc04 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Hosts_Reallocation', col_names=TRUE))
  
  poisson04 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Poisson', col_names=TRUE))
  zipf04 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Zipf', col_names=TRUE))
  times04 <- read.table("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.dat", header = TRUE)
  delay04 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf04_lambda5fixo.xlsx", sheet='Delay', col_names=TRUE))
  
  # zipf 0.6
  rate_admission06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Rate_Admission', col_names=TRUE))
  server_use06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Server_Use', col_names=TRUE))
  cache_vs_cloud06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='CacheVsCloud', col_names=TRUE))
  server_use_by_type06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Server_Use_By_Type', col_names=TRUE))
  scattering_optic06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Scattering_Optic', col_names=TRUE))
  scattering_wireless06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Scattering_Wireless', col_names=TRUE))
  load_links_optic06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Load_Links_Optic', col_names=TRUE))
  load_links_wireless06 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Load_Links_Wireless', col_names=TRUE))
  path_Realloc06 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Paths_Reallocation', col_names=TRUE))
  host_Realloc06 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Hosts_Reallocation', col_names=TRUE))
  
  poisson06 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Poisson', col_names=TRUE))
  zipf06 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Zipf', col_names=TRUE))
  times06 <- read.table("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.dat", header = TRUE)
  delay06 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf06_lambda5fixo.xlsx", sheet='Delay', col_names=TRUE))
  
  # zipf 0.8
  rate_admission08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Rate_Admission', col_names=TRUE))
  server_use08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Server_Use', col_names=TRUE))
  cache_vs_cloud08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='CacheVsCloud', col_names=TRUE))
  server_use_by_type08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Server_Use_By_Type', col_names=TRUE))
  scattering_optic08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Scattering_Optic', col_names=TRUE))
  scattering_wireless08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Scattering_Wireless', col_names=TRUE))
  load_links_optic08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Load_Links_Optic', col_names=TRUE))
  load_links_wireless08 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Load_Links_Wireless', col_names=TRUE))
  path_Realloc08 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Paths_Reallocation', col_names=TRUE))
  host_Realloc08 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Hosts_Reallocation', col_names=TRUE))
  
  poisson08 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Poisson', col_names=TRUE))
  zipf08 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Zipf', col_names=TRUE))
  times08 <- read.table("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.dat", header = TRUE)
  delay08 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf08_lambda5fixo.xlsx", sheet='Delay', col_names=TRUE))
  
  # zipf 1.0
  rate_admission1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Rate_Admission', col_names=TRUE))
  server_use1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Server_Use', col_names=TRUE))
  cache_vs_cloud1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='CacheVsCloud', col_names=TRUE))
  server_use_by_type1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Server_Use_By_Type', col_names=TRUE))
  scattering_optic1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Scattering_Optic', col_names=TRUE))
  scattering_wireless1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Scattering_Wireless', col_names=TRUE))
  load_links_optic1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Load_Links_Optic', col_names=TRUE))
  load_links_wireless1 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Load_Links_Wireless', col_names=TRUE))
  path_Realloc1 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Paths_Reallocation', col_names=TRUE))
  host_Realloc1 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Hosts_Reallocation', col_names=TRUE))
  
  poisson1 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Poisson', col_names=TRUE))
  zipf1 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Zipf', col_names=TRUE))
  times1 <- read.table("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.dat", header = TRUE)
  delay1 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf10_lambda5fixo.xlsx", sheet='Delay', col_names=TRUE))
  
  # zipf 1.2
  rate_admission12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Rate_Admission', col_names=TRUE))
  server_use12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Server_Use', col_names=TRUE))
  cache_vs_cloud12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='CacheVsCloud', col_names=TRUE))
  server_use_by_type12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Server_Use_By_Type', col_names=TRUE))
  scattering_optic12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Scattering_Optic', col_names=TRUE))
  scattering_wireless12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Scattering_Wireless', col_names=TRUE))
  load_links_optic12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Load_Links_Optic', col_names=TRUE))
  load_links_wireless12 <- data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Load_Links_Wireless', col_names=TRUE))
  path_Realloc12 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Paths_Reallocation', col_names=TRUE))
  host_Realloc12 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Hosts_Reallocation', col_names=TRUE))
  
  poisson12 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Poisson', col_names=TRUE))
  zipf12 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Zipf', col_names=TRUE))
  times12 <- read.table("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.dat", header = TRUE)
  delay12 = data.frame(read_excel("../dataAnalysis/data/zipf/instance_zipf12_lambda5fixo.xlsx", sheet='Delay', col_names=TRUE))
  
  
  zipf = c(0.4,0.6,0.8,1.0,1.2)
  lambda <- 5
  n <- 100
  beta <- 0.2
  mobility <- 40
}