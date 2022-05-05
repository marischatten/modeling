load_data <-
  function(path,
           path_time ="",
           paths = FALSE,
           rate_admission = FALSE,
           server_use = FALSE,
           cache_vs_cloud = FALSE,
           server_use_by_type = FALSE,
           scattering_optic = FALSE,
           scattering_wireless = FALSE,
           load_links_optic = FALSE,
           load_links_wireless = FALSE,
           path_realloc = FALSE,
           host_realloc = FALSE,
           poisson = FALSE,
           zipf = FALSE,
           times = FALSE,
           delay = FALSE,
           rtt = FALSE) 
  {
    paths <-
      data.frame(read_excel(path, sheet = 'Requests', col_names = TRUE))
    rate_admission <-
      data.frame(read_excel(path, sheet = 'Rate_Admission', col_names = TRUE))
    server_use <-
      data.frame(read_excel(path, sheet = 'Server_Use', col_names = TRUE))
    cache_vs_cloud <-
      data.frame(read_excel(path, sheet = 'CacheVsCloud', col_names = TRUE))
    server_use_by_type <-
      data.frame(read_excel(path, sheet = 'Server_Use_By_Type', col_names = TRUE))
    scattering_optic <-
      data.frame(read_excel(path, sheet = 'Scattering_Optic', col_names = TRUE))
    scattering_wireless <-
      data.frame(read_excel(path, sheet = 'Scattering_Wireless', col_names =
                              TRUE))
    load_links_optic <-
      data.frame(read_excel(path, sheet = 'Load_Links_Optic', col_names = TRUE))
    load_links_wireless <-
      data.frame(read_excel(path, sheet = 'Load_Links_Wireless', col_names =
                              TRUE))
    path_realloc = data.frame(read_excel(path, sheet = 'Paths_Reallocation', col_names =
                                           TRUE))
    host_realloc = data.frame(read_excel(path, sheet = 'Hosts_Reallocation', col_names =
                                           TRUE))
    
    poisson = data.frame(read_excel(path, sheet = 'Poisson', col_names = TRUE))
    zipf = data.frame(read_excel(path, sheet = 'Zipf', col_names = TRUE))
    times <- read.table(path_time, header = TRUE)
    delay = data.frame(read_excel(path, sheet = 'Delay', col_names = TRUE))
    rtt =  data.frame(read_excel(path, sheet = 'RTT', col_names = TRUE))
    
    if (paths) {
      data = append(datas, paths)
    }
    if (rate_admission) {
      data = append(datas, rate_admission)
    }
    if (server_use) {
      data = append(datas, server_use)
    }
    if (cache_vs_cloud) {
      data = append(datas, cache_vs_cloud)
    }
    if (server_use_by_type) {
      data = append(datas, server_use_by_type)
    }
    if (scattering_optic) {
      data = append(datas, scattering_optic)
    }
    if (scattering_wireless) {
      data = append(datas, scattering_wireless)
    }
    if (load_links_optic) {
      data = append(datas, load_links_optic)
    }
    if (load_links_wireless) {
      data = append(datas, load_links_wireless)
    }
    if (path_realloc) {
      data = append(datas, path_realloc)
    }
    if (host_realloc) {
      data = append(datas, host_realloc)
    }
    if (poisson) {
      data = append(datas, poisson)
    }
    if (zipf) {
      data = append(datas, zipf)
    }
    if (times) {
      data = append(datas, times)
    }
    if (delay) {
      data = append(datas, delay)
    }
    if (rtt) {
      data = append(datas, rtt)
    }
    
    return (data)
  }