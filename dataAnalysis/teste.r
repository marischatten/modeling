library(ggplot2)
X <- rep(1:100)
X_1 <- rep(1:100)

Z <- rnorm(100,mean=10,sd=1)
Z_1 <- rnorm(100,mean=10,sd=1)


Y <- rnorm(100,mean=10,sd=1)
W <- rnorm(100,mean=10,sd=1)
Y_1 <- rnorm(100,mean=10,sd=1)
W_1 <- rnorm(100,mean=10,sd=1)

K <- rep("B",100)
J <- rep("A",100)
L <- rep("C",100)
K_1 <- rep("B",100)
J_1 <- rep("A",100)
L_1 <- rep("C",100)

M <- rep("G1",100)
M_1 <- rep("G2",100)

d_y <- data.frame(id=X, func=Y, type=K, g=M)
d_w <- data.frame(id=X, func=W, type=J ,g=M)
d_z <- data.frame(id=X, func=Z, type=L ,g=M)

d_yw <- rbind(d_y,d_w)

d_y_1 <- data.frame(id=X, func=Y, type=K, g=M_1)
d_w_1 <- data.frame(id=X, func=W, type=J ,g=M_1)
d_z_1 <- data.frame(id=X, func=Z, type=L ,g=M_1)

d_yw_1 <- rbind(d_y,d_w)

d_yw
d_yw_1

df <- rbind(d_yw,d_yw_1)

ggplot(data=df, mapping = aes(x=id, y=func, group=type, color=type)) + geom_boxplot() 
#ggplot(data=df, mapping = aes(x=id, y=func, group=type, color=type, fill=type)) + geom_density(position="identity", stat="identity", alpha=0.25, color="black") 
#ggplot(data=df) + facet_wrap( ~ g, nrow = 1) + theme(legend.position = "none")

###################################################################################################

avg <- rnorm(100,mean=10,sd=1)
avg.sd <- sd(avg)

sd.top <- avg + avg.sd
sd.bottom <- avg - avg.sd

avg
avg.sd
sd.top
sd.bottom


avg[10] <- 0
sd.top[10] <- 0
sd.bottom[10] <- 0
df <- data.frame(id= rep(1:100),value=avg,top=sd.top,bottom=sd.bottom)
df

ggplot(data=df, aes(y=value, x=id)) + geom_line() + geom_ribbon(aes(ymin =  bottom, ymax =  top),alpha=0.25, color=NA)

###############################################################################################
library(dplyr)

df1 <- data.frame(id = c(1, 2, 2, 3, 3, 4, 5, 5),
                  gender = c("F", "F", "M", "F", "B", "B", "F", "M"),
                  variant = c("a", "b", "c", "d", "e", "f", "g", "h"))

# t <- df1 %>% slice(n())
# t
t1 <- df1 %>% group_by(id) %>% slice(n())
t2 <- df1 %>% group_by(gender) %>% slice(1)
t3 <- df1 %>% group_by(variant) %>% slice(1)

t1
t2
t3
###############################################################################################
ID <- rep(1:100)
A <- rep("A",100)
AA <- rnorm(100,mean=10,sd=1)
B <- rep("B",100)
BB <- rnorm(100,mean=10,sd=1)

df_a <- data.frame(id=ID,type=A,value=AA)
df_b <- data.frame(id=ID,type=B,value=BB)
df <- rbind(df_a,df_b)
df


ggplot(df, aes(fill=type, y=value, x=id)) + 
  geom_bar(position="identity", stat="identity")
