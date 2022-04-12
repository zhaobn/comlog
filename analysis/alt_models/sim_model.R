
library(dplyr)

normalize<-function(vec) return (vec/sum(vec))

#### Experiment 1 ####
task = read.csv('../../data/tasks/exp_1.csv') %>% select(-X)
load('../../data/exp_1_cleaned.rdata')

# Measure similarity
calc_sim <- function(dx, dy, ws=1, wd=1, wb=1) {
  sim_dist = sum(c(ws*abs(dx$stripe-dy$stripe), wd*abs(dx$dot-dy$dot), wb*abs(dx$block-dy$block)))
  return(exp(-sim_dist))
}

# Generalization preds
get_trial_pred <- function(cond, tid, batch, pars=list(ws=1, wd=1, wb=1)) {
  all_terms = data.frame(terms=c(0, seq(16)))
  rt_colname = paste0('prob_', tid)
  
  # Get learning data
  task_data = task %>% filter(condition==cond, batch=='gen', trial==tid) %>% as.list()
  if (batch=='A') {
    trainings = task %>% filter(condition==cond, batch=='A')
  } else {
    trainings = task %>% filter(condition==cond, batch %in% c('A', 'B'))
  }
  
  # Calc similarity score
  sim_df = data.frame(lid=seq(nrow(trainings)), terms=0, sim_score=0)
  for (row in 1:nrow(sim_df)) {
    sim_df[row, 'terms'] = trainings[row,'result_block']
    sim_df[row, 'sim_score'] = calc_sim(as.list(trainings[row,]), task_data, pars[['ws']], pars[['wd']], pars[['wb']])
    
  }
  sim_df = sim_df %>% group_by(terms) %>% summarise(weight=sum(sim_score))
  sim_df$weight = normalize(sim_df$weight)
  
  # Get predictions
  pred_df = all_terms %>% 
    left_join(sim_df, by='terms') %>% 
    mutate(weight=ifelse(is.na(weight), 0, weight))
  
  # Format for return
  colnames(pred_df)=c('terms', rt_colname)
  return(pred_df)
}

# Get results
condition='construct'
batch='B'
model='sim'
experi='exp_1'

preds = get_trial_pred(condition, 1, batch, list(ws=0, wd=1, wb=0))
# for (tid in seq(8)) {
#   if (tid>1) {
#     preds = preds %>% left_join(get_trial_pred(condition, tid, batch), by='terms')
#   }
# }
# filename=paste0('sim_model_preds/', experi, '_' condition, '_preds_', tolower(batch), '.csv') 
# write.csv(preds, filename)

# Fit parameters
ppt_list = expand.grid(condition=cond, phase=toupper(phase), trial=seq(8), term=seq(0,16))
ppt_data = df.tw %>% 
  filter(condition==cond, batch==toupper(phase)) %>%
  mutate(phase=batch, term=prediction) %>%
  count(condition, phase, trial, term) %>%
  right_join(ppt_list, by=c('condition', 'phase', 'trial', 'term')) %>%
  mutate(n=ifelse(is.na(n), 0, n)) %>%
  arrange(condition, phase, trial, term)

data = ppt_data%>%filter(condition=='construct', phase=='A', trial!=3)
wg_sims<-function(data, par) {
  
  
}

# Get fitted predictions



#### End of Experiment 1
