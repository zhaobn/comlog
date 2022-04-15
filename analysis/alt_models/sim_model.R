
library(dplyr)
library(tidyr)

normalize<-function(vec) return (vec/sum(vec))

#### Experiment 1 ####
# Measure similarity
calc_sim <- function(dx, dy, ws=1, wd=1, wb=1) {
  sim_dist = sum(c(ws*abs(dx$stripe-dy$stripe), wd*abs(dx$dot-dy$dot), wb*abs(dx$block-dy$block)))
  return(exp(-sim_dist))
}

# Generalization preds
get_trial_pred <- function(cond, tid, batch, pars=list(ws=1, wd=1, wb=1, b=1)) {
  all_terms = data.frame(terms=c(0, seq(16)))
  rt_colname = paste0('prob_', tid)
  rs_colname = paste0('sfmx_', tid)
  
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
  
  # Add softmax
  pred_df[[rs_colname]]<-exp(pred_df[[rt_colname]]*pars[['b']])
  pred_df[[rs_colname]]<-pred_df[[rs_colname]]/sum(pred_df[[rs_colname]])
  
  return(pred_df[,c('terms',rs_colname)])
}

# Get results
model = 'similarity'
experi='exp_1'
task = read.csv(paste0('../../data/tasks/', experi, '.csv')) %>% select(-X)

load(paste0('../../data/', experi, '_cleaned.rdata'))
cross_vl=read.csv(text='model,expt,condition,phase,trial,params,LL')

# Fit parameters
to_fit<-function(data, par) {
  train_ids = unique(data$trial)
  model_data = get_trial_pred(condition, train_ids[1], toupper(batch), par)
  for (tid in train_ids[2:length(train_ids)]) {
    model_data = left_join(model_data, get_trial_pred(condition, tid, batch, par), by='terms')
  }
  ppt_model_data = model_data %>%
    gather('trial', 'prob', -terms) %>%
    mutate(trial=as.numeric(substr(trial, 6, nchar(trial)))) %>%
    rename(term=terms) %>%
    left_join(ppt_data, by=c('trial', 'term')) %>%
    mutate(lp=log(prob), ll=n*lp) %>%
    filter(ll>-Inf, !is.na(ll))
  
  return (-1*sum(ppt_model_data$ll))
}

# Get fitted predictions
for (cond in c('construct', 'decon', 'combine')) {
  for (batch in c('a', 'b')) {
    ppt_list = expand.grid(condition=cond, phase=toupper(batch), trial=seq(8), term=seq(0,16))
    for (tid in seq(8)) {
      # prep data
      ppt_data = df.tw %>% 
        filter(condition==cond, batch==toupper(batch)) %>%
        mutate(phase=batch, term=prediction) %>%
        count(condition, phase, trial, term) %>%
        right_join(ppt_list, by=c('condition', 'phase', 'trial', 'term')) %>%
        mutate(n=ifelse(is.na(n), 0, n)) %>%
        arrange(condition, phase, trial, term)
      tdata = ppt_data %>%
        filter(condition==condition, phase==toupper(batch))
      
      # get fitted params
      out = optim(par=list(ws=0, wd=1, wb=0, b=1), to_fit, data=filter(tdata, trial!=tid))
      # get preds
      pred = get_trial_pred(condition, tid, toupper(batch), out$par) %>%
      rename(term=terms) %>%
        left_join(filter(ppt_data, condition==condition, phase==toupper(batch), trial==tid), by='term') 
      colnames(pred)[2]<-'sfmx_prob'
      pred$ll=log(pred$sfmx_prob)*pred$n
      ll=sum(pred$ll)
      # save
      cross_vl = rbind(cross_vl, data.frame(
        model=model, expt=experi, condition=cond, phase=toupper(batch), trial=tid, params=toString(out$par), LL=ll
      ))
      write.csv(cross_vl, file=paste0('../cross_valids/', model, '_', experi, '.csv'))
    }
  }
}






#### End of Experiment 1
