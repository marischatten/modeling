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

A <- rnorm(100,mean=10,sd=1)
B <- rnorm(100,mean=10,sd=1)
C <- rnorm(100,mean=10,sd=1)

df_radar <- data.frame(a=A,b=B,c=C)
data <- rbind(rep(20,5) , rep(0,5) , df_radar)
library(fmsb)

radarchart( data[-c(1,2),]  , axistype=0 , maxmin=F,
            #custom polygon
            pcol=colors_border , pfcol=colors_in , plwd=4 , plty=1,
            #custom the grid
            cglcol="grey", cglty=1, axislabcol="black", cglwd=0.8, 
            #custom labels
            vlcex=0.8 
)

# Add a legend
legend(x=0.7, y=1, legend = rownames(data[-c(1,2),]), bty = "n", pch=20 , col=colors_in , text.col = "grey", cex=1.2, pt.cex=3)


library(fmsb)

# Create data: note in High school for several students
set.seed(99)
data <- as.data.frame(matrix( sample( 0:20 , 15 , replace=F) , ncol=5))
colnames(data) <- c("math" , "english" , "biology" , "music" , "R-coding" )
rownames(data) <- paste("mister" , letters[1:3] , sep="-")

# To use the fmsb package, I have to add 2 lines to the dataframe: the max and min of each variable to show on the plot!
data <- rbind(rep(20,5) , rep(0,5) , data)

# Set graphic colors
library(RColorBrewer)
coul <- brewer.pal(3, "BuPu")
colors_border <- coul
library(scales)
colors_in <- alpha(coul,0.3)

# If you remove the 2 first lines, the function compute the max and min of each variable with the available data:
radarchart( data[-c(1,2),]  , axistype=0 , maxmin=F,
            #custom polygon
            pcol=colors_border , pfcol=colors_in , plwd=4 , plty=1,
            #custom the grid
            cglcol="grey", cglty=1, axislabcol="black", cglwd=0.8, 
            #custom labels
            vlcex=0.8 
)

# Add a legend
legend(x=0.7, y=1, legend = rownames(data[-c(1,2),]), bty = "n", pch=20 , col=colors_in , text.col = "grey", cex=1.2, pt.cex=3)

write.csv(data, "teste.csv", row.names = FALSE)