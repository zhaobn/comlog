library(RPostgreSQL)
library(rjson)
rm(list=ls())

# First run this in the terminal to connect to the database:

# ssh -L 1111:localhost:5432 s1941626@eco.ppls.ed.ac.uk

#Then you should be able to connect via an ssh port
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = 'bn_comp',
                  host = 'localhost', port = 1111,
                  password = 'Cobs&Rile&Hush85',
                  user = 's1941626')

# If its worked you should be able to detect these databases
dbExistsTable(con, "participant")
dbExistsTable(con, "task")

# Then you can pull the task data from postgreSQL 
td <- dbGetQuery(con, "SELECT * from task")
#Here it is as json
td$subjectwise
td$trialwise

#Un-jsonify it
inv_fromJSON<-function(js)
{
  js <- chartr("\'\"","\"\'",js)
  fromJSON(js)
}
#and turn each subject into a dataframe
sw<-sapply(sapply(td$subjectwise, inv_fromJSON, simplify=F), as.data.frame, simplify=F)
tw<-sapply(sapply(td$trialwise, inv_fromJSON, simplify=F), as.data.frame, simplify=F)
N<-length(tw)

#Combine them
df.sw.aux<-sw[[1]]
df.tw.aux<-tw[[1]]
for (i in 2:length(sw))
{
  df.sw.aux<-rbind(df.sw.aux, sw[[i]])
  df.tw.aux<-rbind(df.tw.aux, tw[[i]])
}
#And append them to the id and upis
df.sw<-data.frame(ix=td$id,
                  id=td$participant)
df.sw<-cbind(df.sw, df.sw.aux)
df.tw<-cbind(ix=rep(df.sw$ix, each=N), id=rep(df.sw$id, each=N), df.tw.aux)

save(file='flaskdemodata.rdata', df.sw, df.tw)
