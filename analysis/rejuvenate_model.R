
library(dplyr)
library(tidyr)

model='pcfg'
eid=1
cond = 'construct'
rj_eid = 1
rj_cond = 'decon'


forward_preds = read.csv(file = paste0(
  '../model_data/', tolower(model), '/exp_', eid, '/', cond, '_preds_b.csv' 
)) %>% 
  select(terms, starts_with('prob_')) %>%
  gather(trial, prob, -terms) %>%
  mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))

backward_preds = read.csv(file = paste0(
  '../model_data/', tolower(model), '/exp_', rj_eid, '/', rj_cond, '_preds_b.csv' 
)) %>% 
  select(terms, starts_with('prob_')) %>%
  gather(trial, bprob, -terms) %>%
  mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))

rj_preds = forward_preds %>%
  left_join(backward_preds, by=c('terms', 'trial')) %>%
  mutate(rprob=0.714*prob+0.286*bprob) 
rj_preds_fmt = rj_preds %>%
  select(terms, trial, rprob) %>%
  spread(trial, rprob)
colnames(rj_preds_fmt) = c('terms', paste0('prob_', seq(8)))

write.csv(rj_preds_fmt, file = paste0(
  '../model_data/', tolower(model), '_rj/exp_', eid, '/', cond, '_preds_b.csv' 
))







