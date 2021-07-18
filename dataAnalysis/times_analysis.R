times <- read.table("instance.dat", header = TRUE)
events <- c(1:length(times$X0.004))
dt <- data.frame(events,times)
plot(dt,type="b",col="red")
