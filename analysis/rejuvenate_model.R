
library(dplyr)
library(tidyr)

iters = c(seq(100,1500,100),seq(2000,5000,500))
options(scipen=999)

setups = list(
  #list(cond = 'construct', rj_cond = 'decon'),
  list(cond = 'decon', rj_cond = 'construct'),
  #list(cond = 'combine', rj_cond = 'flip'),
  list(cond = 'flip', rj_cond = 'combine')
) 

get_reju_mix = function(model, iter, weight=0.5) {
  
  for (pair in setups) {
    
    forward_preds = read.csv(file = paste0(
      '../model_data/', tolower(model), '/process_', iter, '/', pair[['cond']], '_preds_b.csv' 
    )) %>% 
      select(terms, starts_with('prob_')) %>%
      gather(trial, prob, -terms) %>%
      mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))
    
    backward_preds = read.csv(file = paste0(
      '../model_data/', tolower(model), '/process_', iter, '/', pair[['rj_cond']], '_preds_b.csv' 
    )) %>% 
      select(terms, starts_with('prob_')) %>%
      gather(trial, bprob, -terms) %>%
      mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))
    
    backward_weight = weight/(1+weight)
    forward_weight = 1-backward_weight
    
    rj_preds = forward_preds %>%
      left_join(backward_preds, by=c('terms', 'trial')) %>%
      mutate(rprob=forward_weight*prob+backward_weight*bprob) 
    rj_preds_fmt = rj_preds %>%
      select(terms, trial, rprob) %>%
      spread(trial, rprob)
    colnames(rj_preds_fmt) = c('terms', paste0('prob_', seq(8)))
    
    write.csv(rj_preds_fmt, file = paste0(
      '../model_data/', tolower(model), 'r/process_', iter, '/', pair[['cond']], '_preds_b.csv' 
    )) 
  }
}


for (i in iters) {
  get_reju_mix('ag', i)
}






# #### ARCHIVE: with exp prefixes ####
# 
# eid=1
# cond='construct'
# rj_eid=1
# rj_cond='decon'
# 
# forward_preds = read.csv(file = paste0(
#   '../model_data/', tolower(model), '/exp_', eid, '/', cond, '_preds_b.csv' 
# )) %>% 
#   select(terms, starts_with('prob_')) %>%
#   gather(trial, prob, -terms) %>%
#   mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))
# 
# backward_preds = read.csv(file = paste0(
#   '../model_data/', tolower(model), '/exp_', rj_eid, '/', rj_cond, '_preds_b.csv' 
# )) %>% 
#   select(terms, starts_with('prob_')) %>%
#   gather(trial, bprob, -terms) %>%
#   mutate(trial=as.numeric(substr(trial, 6, nchar(trial))))
# 
# rj_preds = forward_preds %>%
#   left_join(backward_preds, by=c('terms', 'trial')) %>%
#   mutate(rprob=0.714*prob+0.286*bprob) 
# rj_preds_fmt = rj_preds %>%
#   select(terms, trial, rprob) %>%
#   spread(trial, rprob)
# colnames(rj_preds_fmt) = c('terms', paste0('prob_', seq(8)))
# 
# write.csv(rj_preds_fmt, file = paste0(
#   '../model_data/', tolower(model), '_rj/exp_', eid, '/', cond, '_preds_b.csv' 
# ))
# 
# 





