library(dplyr)
times <- read.table("../ModelingV0/output/data/instance_9.dat", header = TRUE)
max_time <- max(times$times)
times.optimize <- times$times[times$times != max_time]
times.optimize 
events <- c(1:length(times.optimize))
dt <- data.frame(events,times.optimize)

times.lm <- lm(times.optimize~events,data=dt)
(summary(times.lm))
times.next <- data.frame(n=c(1000))
times.pred <- data.frame(predict(times.lm,newdata=times.next,int="p",level=0.95))
times.pred
plot(dt)
# abline(times.lm, col="red")

(all.req <-length(times.optimize))