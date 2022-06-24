
library(dplyr)


tasks = read.csv('../data/tasks/tasks.csv') %>% select(-X)


# 

test = tasks %>% 
  filter(condition=='construct', batch!='gen') %>%
  mutate(result_block=as.factor(as.character(result_block)))
m = glm(data=test, result_block~stripe+dot+block, family="binomial")
gens = tasks %>% 
  filter(condition=='construct', batch=='gen') %>%
  select(trial, stripe, dot, block)
predict(m, gens, type = "response")





