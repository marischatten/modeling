set_qtd_realloc <- function(path_Realloc){
  
  path_realloc_by_request <- aggregate(path_Realloc$Request, by=list(path_Realloc$Request), FUN=length)
  requests <- unique(requests00$Request)
  realloc_path <- c()
  for (i in 1:r){
    if (requests[i] %in% path_realloc_by_request$Group.1){
      qtd_realloc_row = path_realloc_by_request %>% filter(path_realloc_by_request$Group.1 == requests[i])
      qtd_realloc = qtd_realloc_row$x  
      realloc_path = append(realloc_path, qtd_realloc)
    }else{
      realloc_path = append(realloc_path,0)
    }
  }
  return(realloc_path)
}

create_df_realloc <- function(r,realloc_path){
  df_path <- data.frame(request=rep(1:r), count_realloc=realloc_path,stringsAsFactors = FALSE)
  return(df_path)
}

plot_graph_realloc_path <- function(df_path){
  gg_path <- ggplot(df_path, aes(y=count_realloc, x=request)) + geom_bar(position="identity", stat="identity")+
  scale_y_continuous(limit = c(0, 5))+
  theme_bw()+ 
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 18),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16)
          )

  
    # xlab(x.lab)+
    # ylab(y.lab)
  
  return(gg_path)
}

set_qtd_realloc_host <- function(host_Realloc,all_requests,r){
  host_realloc_by_request <- aggregate(host_Realloc$Request, by=list(host_Realloc$Request), FUN=length)
  requests_raw <- unique(all_requests$Request)
  realloc_host <- c()
  requests <- c()
  
  for(i in 1:r){
    requests_str_1 <- str_replace(requests_raw[i],"\\['","")
    requests_str_2 <- str_replace(requests_str_1,"\\']","")
    requests <- append(requests,requests_str_2)
  }

  for (i in 1:r){
    if (requests[i] %in% host_realloc_by_request$Group.1){
      qtd_realloc_row = host_realloc_by_request %>% filter(host_realloc_by_request$Group.1 == requests[i])
      qtd_realloc = qtd_realloc_row$x  
      realloc_host = append(realloc_host, qtd_realloc)
    }else{
      realloc_host = append(realloc_host,0)
    }
  }
  return(realloc_host)
}

plot_graph_realloc_host <- function(df_path){
  gg_path <- ggplot(df_path, aes(y=count_realloc, x=request)) + geom_bar(position="identity", stat="identity")+
    scale_y_continuous(limit = c(0, 16))+
    theme_bw()+ 
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 18),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16)
    )
  
  
  # xlab(x.lab)+
  # ylab(y.lab)
  
  return(gg_path)
}


get_last_status_realloc_host <- function(host_Realloc,n){
  host_realloc_last_state <- data.frame()
  for (i in 1:n){
    host_realloc_last_state_n <- host_Realloc %>% filter(host_Realloc$Event == i)
    host_realloc_last_state <- rbind(host_realloc_last_state, host_realloc_last_state_n %>%  group_by(Request) %>% slice(n()))
  }
  return(host_realloc_last_state)
}


set_sum_request_by_event <- function(realloc_last_state){
  realloc_by_event <- aggregate(realloc_last_state$Event, by=list(realloc_last_state$Event), FUN=length)
  return (realloc_by_event)
}

create_df_realloc_host_by_event <- function(realloc_by_event,n){
  df_realloc_by_event <- data.frame(event=rep(1:n), count_realloc_by_event=realloc_by_event$x,stringsAsFactors = FALSE)
  return(df_realloc_by_event)
}

plot_graph_realloc_by_event <- function(df_realloc_by_event){
  gg_path <- ggplot(df_realloc_by_event, aes(y=count_realloc_by_event, x=event)) + geom_bar(position="identity", stat="identity")+
    scale_y_continuous(limit = c(0, 50))+
    theme_bw()+ 
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 18),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16)
    )
  
  
  # xlab(x.lab)+
  # ylab(y.lab)
  
  return(gg_path)
}

set_null_event_empty <- function(realloc_last_state,n){
  realloc_last_state$Request[is.na(realloc_last_state$Request)] <- 0
  return (realloc_last_state)
}

remove_na <- function(path_Realloc){
  path_Realloc_without_null <- path_Realloc %>% filter(!is.na(path_Realloc$Request))
  return (path_Realloc_without_null)
}

get_last_status_realloc_path <- function(path_Realloc,n){
  paths_realloc_last_state <- data.frame()
  for (i in 1:n){
    paths_realloc_last_state_n <- path_Realloc %>% filter(path_Realloc$Event == i)
    paths_realloc_last_state <- rbind(paths_realloc_last_state, paths_realloc_last_state_n %>%  group_by(Request) %>% slice(n()))
  }
  return(paths_realloc_last_state)
  
}


insert_zero <- function(path_realloc_by_event_raw, n){
  event <- rep(1:n)
  path_realloc_by_event <- c()
  
  for(i in 1:n){
    if (i %in% path_realloc_by_event_raw$Group.1)
    {
      insert = path_realloc_by_event_raw %>% filter(path_realloc_by_event_raw$Group.1 == i)
      path_realloc_by_event = append(path_realloc_by_event, insert$x)
    }else{
      path_realloc_by_event = append(path_realloc_by_event, 0)
    }
  }
  return(path_realloc_by_event)
}
create_df_realloc_path_by_event <- function(realloc_by_event,n){
  df_realloc_by_event <- data.frame(event=rep(1:n), count_realloc_by_event=realloc_by_event,stringsAsFactors = FALSE)
  return(df_realloc_by_event)
}

plot_graph_realloc_path_by_event <- function(df_realloc_by_event){
  gg_path <- ggplot(df_realloc_by_event, aes(y=count_realloc_by_event, x=event)) + geom_bar(position="identity", stat="identity")+
    scale_y_continuous(limit = c(0, 5))+
    theme_bw()+ 
    theme(legend.position = "top",
          # legend.direction = "vertical",
          legend.box = "horizontal",
          #legend.justification = c("right", "top"),
          #legend.box.background = element_rect(color="black", size=1),
          #legend.box.just = "right",
          #legend.margin = margin(4, 4, 4, 2),
          legend.title = element_blank(),
          legend.text = element_text(size = 18),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16)
    )
  
  
  # xlab(x.lab)+
  # ylab(y.lab)
  
  return(gg_path)
}

plot_path_realloc_by_event <- function(path_Realloc,n){
  
  path_Realloc_without_null <- remove_na(path_Realloc)
  
  last_status_realloc <- get_last_status_realloc_path(path_Realloc_without_null,n)
   
  path_realloc_by_event_raw <- set_sum_request_by_event(last_status_realloc)

  path_realloc_by_event <- insert_zero(path_realloc_by_event_raw,n)
  
  df_realloc_by_event_path <- create_df_realloc_path_by_event(path_realloc_by_event,n)
  
  gg_path <- plot_graph_realloc_path_by_event(df_realloc_by_event_path)

  return(gg_path)
}