#Create dataframe
create_dataframe_latency <- function(delay){

  type_storage <- rep(0.4,length(delay$Delay))
  df <- data.frame(id = rep(1:length(delay$Delay)),
                     delay = c(delay$Delay),
                     type = type_storage,
                     # top = delay_links_sd_top04,
                     # bottom = delay_links_sd_bottom04,
                     stringsAsFactors = FALSE)
  return(df)
}

plot_graph_latency <- function(save_pt,save,df_delay){
  
  #Translate
  if (save_pt){
    x.lab <- "Popularity"
    y.lab <- "Latência"
    leg <- "Popularity"
  }else{
    x.lab <- "Popularity "
    y.lab <- "Network Delay (ms)"
    leg <- "Popularity"
  }
  
  g_delay <- ggplot(df_delay,aes(x=type, y=delay, group=type, color=type,fill=type)) +
    geom_boxplot(alpha=0.8,color="Black") + 
    theme_bw()+
    scale_x_continuous(breaks=c(0.4,0.8,1.2), labels=c("0.4","0.8","1.2"))+
    theme(legend.position = "none",
          #       #legend.direction = "vertical",
          #       #legend.box = "horizontal",
          #       #legend.justification = c("right", "top"),
          #       #legend.box.background = element_rect(color="black", size=1),
          #       #legend.box.just = "right",
          #       #legend.margin = margin(4, 4, 4, 2),
          #       legend.title = element_blank(),
          #       legend.text = element_text(size = 18),
          axis.text=element_text(size=16),
          axis.title=element_text(size=16))+
    ylab(y.lab) + xlab(element_blank()) +ylim(c(0,70))
}

save_graph <- function(save_pt, save){
  if (save_pt){
    ggsave(g_delay,filename = "graph/pt/zipf/zipf_delay.pdf", dpi = 600)
    ggsave(g_delay,filename = "graph/pt/zipf/zipf_delay.png", dpi = 600)
  }else{
    ggsave(g_delay,filename = "graph/zipf/zipf_delay.pdf", dpi = 600)
    ggsave(g_delay,filename = "graph/zipf/zipf_delay.png", dpi = 600)
  }
}