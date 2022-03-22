
library(dplyr)

normalize<-function(vec) {
  return (vec/sum(vec))
}

#### Experiment 1 ####
task = read.csv('../../data/tasks/exp_1.csv') %>% select(-X)

# Measure similarity
calc_sim <- function(dx, dy, ws=1, wd=1, wb=1) {
  sim_dist = sum(c(ws*abs(dx$stripe-dy$stripe), wd*abs(dx$dot-dy$dot), wb*abs(dx$block-dy$block)))
  return(exp(-sim_dist))
}

# Generalization preds
get_trial_pred <- function(cond, tid, batch) {
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
    sim_df[row, 'sim_score'] = calc_sim(as.list(trainings[row,]), task_data)
    
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
batch='A'

preds = get_trial_pred(condition, 1, batch)
for (tid in seq(8)) {
  if (tid>1) {
    preds = preds %>% left_join(get_trial_pred(condition, tid, batch), by='terms')
  }
}

# Fit parameters

# Get fitted predictions

# Plots

#### End of Experiment 1
