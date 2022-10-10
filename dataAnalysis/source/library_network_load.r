#get total requests load
get_total_requests_load <- function(poisson,qos,n){
  total_requests_load <- c()
  for(i in 0:n-1){
    poisson_n <- subset(poisson, ...1 == i)
    total_requests_load <- append(total_requests_load,poisson_n$Qtd_Requests)
  }
  return(total_requests_load)
}

#total load BH and FH
get_total_load <- function(paths,rtt,n,buffer) {
  #filter and last status
  events <- paths$Event
  thp_cur_n_ <- c()
  thp_cur_n_sum = 0
  thp_cur_sum = c()
  thp_cur_ <- c()
  thp_cur_sd_ <- c()
  thp_cur_req <- 0
  
  for (e in 1:n){
    # print("EVENTO")
    # print(e)
    if (all(e %in% events)){
      paths_n = subset(paths, Event == e)
      for(row in 1:nrow(paths_n)){
        # print("REQUEST")
        # print(paths_n[row,]$Request)
        paths_split = strsplit(paths_n[row,]$Path,",")[[1]]
        count = 0
        i = 2
        rtt_n = subset(rtt,Event == e)
        while(count < paths_n[row,]$Hops){
          thp_cur_link = 0
          orig = str_replace_all(paths_split[i], "[^[:alnum:]]", "")
          dest = str_replace_all(paths_split[i+1], "[^[:alnum:]]", "")
          orig_dest <- paste("('",orig,"', '",dest,"')",sep="")
          
          rtt_row_paths = subset(rtt_n, Link ==  orig_dest )
          # print("WHILE")
          # print(paths_split)
          # print(orig_dest)
          thp_cur_link = buffer/ rtt_row_paths$RTT
          # print(thp_cur_link)
          thp_cur_req = thp_cur_req + thp_cur_link
          # print(thp_cur_req)
          i = i+1
          count = count + 1
        }
        thp_cur_n_sum = thp_cur_n_sum + thp_cur_req
        thp_cur_n_ = append(thp_cur_n_,thp_cur_req)
        thp_cur_req = 0
        # print("ARRAY BY EVENT")
        # print(thp_cur_n_)
      }
      avg_thp_cur_n_ = mean(thp_cur_n_)
      thp_cur_ =  append(thp_cur_,avg_thp_cur_n_)
      
      sd_thp_cur_n_ = sd(thp_cur_n_)
      thp_cur_sd_ =  append(thp_cur_sd_,sd_thp_cur_n_)
      
      thp_cur_sum =  append(thp_cur_sum,thp_cur_n_sum)
      
      thp_cur_n_ = 0
      thp_cur_n_sum = 0
    }else{
      thp_cur_ =  append(thp_cur_,0)
      thp_cur_sd_ =  append(thp_cur_sd_,0)
      thp_cur_sum = append(thp_cur_sum,0)
    }
  }
  thp_cur_sum_normalized = normalize_thp_cur_sum(thp_cur_sum)
  thp_cur_sd_floor <- set_sd_floor(thp_cur_,thp_cur_sd_) 
  thp_cur_sd_ceiling <- set_sd_ceiling(thp_cur_,thp_cur_sd_)
  
  return(list(thp_cur_,thp_cur_sd_floor,thp_cur_sd_ceiling,thp_cur_sum_normalized))
}

normalize_thp_cur_sum <- function(thp_cur_sum){
  thp_cur_sum_max <- max(thp_cur_sum)
  thp_cur_sum_normalized <- thp_cur_sum/thp_cur_sum_max
  return(thp_cur_sum_normalized)
}

set_sd_floor <-  function(thp_cur_avg, thp_cur_sd){
  thp_cur_sd_floor <- thp_cur_avg - thp_cur_sd
  return (thp_cur_sd_floor)
}
set_sd_ceiling <- function(thp_cur_avg, thp_cur_sd){
  thp_cur_sd_ceiling <- thp_cur_avg + thp_cur_sd
  return(thp_cur_sd_ceiling)
}

#avg min load in links
#WARNING: falta remover os BH. 
avg_load_links <- function(load_links_optic02,qos,n){
  avg_load_links <- c()
  load_n <- c()
  
  for(e in 1:n){
    load_links_n = subset(load_links_optic02, Event == e)
    for(row in 1:nrow(load_links_n)){
      sum_qos_req = load_links_n[row,]$Qtd #* qos
      load_n = append(load_n,sum_qos_req)
    }
    avg_load_n = mean(load_n)
    avg_load_links = append(avg_load_links,avg_load_n)
    avg_load_n = NULL
    load_n = NULL
  }
  return(avg_load_links)
}


#create dataframes
create_df_network_load <- function(total_requests_load,thp_cur_cloud,thp_cur_ran,avg_thp_cur_ran,translator){
  # df_total_requests_load <- data.frame(
  #   event = rep(1:100),
  #   values = total_requests_load,
  #   type = rep("Total Requests Load", 100),
  #   stringsAsFactors = FALSE)

  
  # df_backhaul_load <- data.frame(
  #   event = rep(1:100),
  #   values = thp_cur_cloud[[1]],
  #   type = rep("Backhaul Load", 100),
  #   floor = thp_cur_cloud[[2]],
  #   ceiling = thp_cur_cloud[[3]],
  #   stringsAsFactors = FALSE)
  
  if (translator){
    type_bh <- rep("Carga Backhaul",100)
  }else{
    type_bh <- rep("Backhaul Load",100)
  }
  df_backhaul_load_sum <- data.frame(
    event = rep(1:100),
    values = thp_cur_cloud[[4]],
    type = type_bh,
    stringsAsFactors = FALSE)
  
  # df_fronthaul_load <- data.frame(
  #   event = rep(1:100),
  #   values = thp_cur_ran[[1]],
  #   type = rep("Fronthaul Load", 100),
  #   floor = thp_cur_ran[[2]],
  #   ceiling = thp_cur_ran[[3]],
  #   stringsAsFactors = FALSE)
  
  if (translator){
    type_fh <- rep("Carga Fronthaul",100)
  }else{
    type_fh <- rep("Fronthaul Load",100)
  }
  df_fronthaul_load_sum <- data.frame(
    event = rep(1:100),
    values = thp_cur_ran[[4]],
    type = type_fh,
    stringsAsFactors = FALSE)
  
  # df_avg_fronthaul_load <- data.frame(
  #   event = rep(1:100),
  #   values = avg_thp_cur_ran,
  #   type = rep("Average Fronthaul Load", 100),
  #   stringsAsFactors = FALSE)
  
  df_load_normal <- rbind(df_backhaul_load_sum, df_fronthaul_load_sum)
  
  return(df_load_normal)
}

#plot graphs
plot_graphs_network_load <- function(df_load,translator){
  
  if (translator){
    y.lab <- "Carga da Rede"
    x.lab <- "Eventos"
  }else{
    y.lab <- "Network Load"
    x.lab <- "Events"
  }
  
  load_network <- ggplot(df_load, aes(x=event, y=values, group=type, color=type, fill=type)) + geom_line(position="identity", stat="identity",size=1) +
    #geom_ribbon(aes(ymin =  floor, ymax =  ceiling), alpha=0.25, color=NA)+
    theme_bw() + #scale_y_log10() +
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 16),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16))+
    xlab(x.lab)+
    ylab(y.lab)
  
  return(load_network)
}