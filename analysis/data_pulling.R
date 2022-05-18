
library(RPostgreSQL)
library(rjson)
library(dplyr)
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
# Here it is as json
# td$subjectwise
# td$trialwise
# Reorder according to id
td = arrange(td, id)
td_batch = td[td$id>194,] # Re-retrieve exp 2 data
td_batch = td_batch[td_batch$id<360,]


#Un-jsonify it
inv_fromJSON<-function(js) {
  js <- chartr("\'\"","\"\'",js)
  fromJSON(js)
}
# and turn each subject into a dataframe
sw<-sapply(sapply(td_batch$subjectwise, inv_fromJSON, simplify=F), as.data.frame, simplify=F)
tw<-sapply(sapply(td_batch$trialwise, inv_fromJSON, simplify=F), as.data.frame, simplify=F)
N<-length(tw)
M<-22

start_index = 1
end_index = nrow(td_batch)

# Combine them
df.sw.aux<-sw[[start_index]]
df.tw.aux<-tw[[start_index]]
for (i in (start_index+1):end_index) {
  df.sw.aux<-rbind(df.sw.aux, sw[[i]])
  df.tw.aux<-rbind(df.tw.aux, tw[[i]])
}
# And append them to the id and upis
df.sw<-data.frame(ix=td_batch$id, id=td_batch$participant)
df.sw<-cbind(df.sw, df.sw.aux)

df.tw.aux = df.tw.aux %>% rename(tid=id)
df.tw<-cbind(ix=rep(df.sw$ix, each=M), id=rep(df.sw$id, each=M), prolific_id=rep(df.sw$prolific_id, each=M), df.tw.aux)


# Check for Prolific
df.sw %>% filter(prolific_id=='6093e78e30fb90f291b261f9')

# Remove data
df.sw = df.sw %>% filter(!prolific_id=='5d270f5b1f68140019729a94')
df.tw = df.tw %>% filter(!prolific_id=='5d270f5b1f68140019729a94')

# Remove prolific ID
df.sw<-df.sw%>%select(-prolific_id) 
df.tw<-df.tw%>%select(-prolific_id) 

save(file='../data/raw/exp_2_raw.rdata', df.sw, df.tw)


