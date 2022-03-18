get_hops_cloud_normalized <- function(sum_cloud,sum_ran){
  sum_cloud_normal <- c()
  all_hops <- c()
  for (i in 1:n){
    all_hops = append(all_hops, sum_cloud[i] + sum_ran[i])
  }
  
  for (i in 1:n){
    sum_cloud_normal[i] = append(sum_cloud_normal,sum_cloud[i] /all_hops[i])
  }
  
  return(sum_cloud_normal)
}

get_hops_ran_normalized <- function(sum_cloud,sum_ran){
  sum_ran_normal <- c()
  all_hops <- c()
  for (i in 1:n){
    all_hops = append(all_hops, sum_cloud[i] + sum_ran[i])
  }
  
  for (i in 1:n){
    sum_ran_normal = append(sum_ran_normal,sum_ran[i] /all_hops[i])
  }
  
  return(sum_ran_normal)
}