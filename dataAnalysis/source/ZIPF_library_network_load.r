#get total requests load
get_total_requests_load <- function(poisson,qos,n){
  total_requests_load <- c()
  for(i in 0:n-1){
    poisson_n <- subset(poisson, ...1 == i)
    total_requests_load <- append(total_requests_load,poisson_n$Qtd_Requests * qos)
  }
  return(total_requests_load)
}

#total load BH and FH
get_total_load <- function(paths02_cloud,n,buffer) {
  #filter and last status
  events <- paths02_cloud$Event
  thp_cur_n_02 <- c()
  thp_cur_cloud_02 <- c()
  thp_cur_cloud_sd_02 <- c()
  thp_cur_req <- 0
  
  for (e in 1:n){
    print("EVENTO")
    print(e)
    if (all(e %in% events)){
      paths02_cloud_n = subset(paths02_cloud, Event == e)
      for(row in 1:nrow(paths02_cloud_n)){
        print("REQUEST")
        print(paths02_cloud_n[row,]$Request)
        paths02_cloud_split = strsplit(paths02_cloud_n[row,]$Path,",")[[1]]
        count = 0
        i = 2
        rtt02_n = subset(rtt02,Event == e)
        while(count < paths02_cloud_n[row,]$Hops){
          thp_cur_link = 0
          orig = str_replace_all(paths02_cloud_split[i], "[^[:alnum:]]", "")
          dest = str_replace_all(paths02_cloud_split[i+1], "[^[:alnum:]]", "")
          orig_dest <- paste("('",orig,"', '",dest,"')",sep="")
          
          rtt_row_paths02 = subset(rtt02_n, Link ==  orig_dest )
          print("WHILE")
          print(paths02_cloud_split)
          print(orig_dest)
          thp_cur_link = buffer/ rtt_row_paths02$RTT
          print(thp_cur_link)
          thp_cur_req = thp_cur_req + thp_cur_link
          print(thp_cur_req)
          i = i+1
          count = count + 1
        }
        #thp_cur_n_02 = append(thp_cur_n_02,thp_cur_req)
        thp_cur_n_02 = append(thp_cur_n_02,thp_cur_req)
        thp_cur_req = 0
        print("ARRAY BY EVENT")
        print(thp_cur_n_02)
      }
      avg_thp_cur_n_02 = mean(thp_cur_n_02)
      thp_cur_cloud_02 =  append(thp_cur_cloud_02,avg_thp_cur_n_02)
      
      sd_thp_cur_n_02 = sd(thp_cur_n_02)
      thp_cur_cloud_sd_02 =  append(thp_cur_cloud_sd_02,sd_thp_cur_n_02)
      
      thp_cur_n_02 = 0
    }else{
      thp_cur_cloud_02 =  append(thp_cur_cloud_02,0)
      thp_cur_cloud_sd_02 =  append(thp_cur_cloud_sd_02,0)
    }
  }
  thp_cur_sd_floor <- set_sd_floor(thp_cur_cloud_02,thp_cur_cloud_sd_02) 
  thp_cur_sd_ceiling <- set_sd_ceiling(thp_cur_cloud_02,thp_cur_cloud_sd_02)
  
  return(list(thp_cur_cloud_02,thp_cur_sd_floor,thp_cur_sd_ceiling))
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
avg_load_links <- function(load_links_optic02,qos,n){
  avg_load_links <- c()
  load_n <- c()
  
  for(e in 1:n){
    load_links_n = subset(load_links_optic02, Event == e)
    for(row in 1:nrow(load_links_n)){
      sum_qos_req = load_links_n[row,]$Qtd * qos
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
create_df_network_load <- function(total_requests_load,thp_cur_cloud,thp_cur_ran,avg_thp_cur_ran){
  df_total_requests_load <- data.frame(
    event = rep(1:100),
    values = total_requests_load,
    type = rep("Total Requests Load", 100),
    stringsAsFactors = FALSE)
  
  df_backhaul_load <- data.frame(
    event = rep(1:100),
    values = thp_cur_cloud[[1]],
    type = rep("Backhaul Load", 100),
    stringsAsFactors = FALSE)
  
  df_backhaul_load_floor <- data.frame(
    event = rep(1:100),
    values = thp_cur_cloud[[2]],
    type = rep("Backhaul Load Floor", 100),
    stringsAsFactors = FALSE)
  
  df_backhaul_load_ceiling <- data.frame(
    event = rep(1:100),
    values = thp_cur_cloud[[3]],
    type = rep("Backhaul Load Ceiling", 100),
    stringsAsFactors = FALSE)
  
  df_fronthaul_load <- data.frame(
    event = rep(1:100),
    values = thp_cur_ran[[1]],
    type = rep("Fronthaul Load", 100),
    stringsAsFactors = FALSE)
  
  df_fronthaul_load_floor <- data.frame(
    event = rep(1:100),
    values = thp_cur_ran[[2]],
    type = rep("Fronthaul Load Floor", 100),
    stringsAsFactors = FALSE)
  
  df_fronthaul_load_ceiling <- data.frame(
    event = rep(1:100),
    values = thp_cur_ran[[3]],
    type = rep("Fronthaul Load Ceiling", 100),
    stringsAsFactors = FALSE)
  
  df_avg_fronthaul_load <- data.frame(
    event = rep(1:100),
    values = avg_thp_cur_ran,
    type = rep("Average Fronthaul Load", 100),
    stringsAsFactors = FALSE)
  
  df_load <- rbind(df_total_requests_load,df_backhaul_load, df_fronthaul_load, df_avg_fronthaul_load)
  #df_load <- rbind(df_total_requests_load,df_backhaul_load,df_backhaul_load_floor,df_backhaul_load_ceiling, df_fronthaul_load, df_fronthaul_load_floor, df_fronthaul_load_ceiling, df_avg_fronthaul_load)
  return(df_load)
}

#plot graphs
plot_graphs_network_load <- function(df_load,translator){
  
  if (translator){
    y.lab <- "Network Load"
    x-lab <- "Events"
  }else{
    y.lab <- "Carga da Rede"
    x.lab <- "Eventos"
  }
  
  load_network <- ggplot(df_load) + geom_line(mapping= aes(x=event, y=values, group=type, color=type, fill=type),size=1) +
    #geom_ribbon(aes(ymin =  floor, ymax =  ceiling), alpha=0.25, color=NA)+
    theme_bw()+
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 12),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16))+
    xlab(x.lab)+
    ylab(y.lab)
  
  return(load_network)
}