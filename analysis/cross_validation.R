
#### Packages, data, core funcs ########
library(dplyr)
library(tidyr)
library(ggplot2)


#### Play with ag data ####
load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(exp_id, condition, batch, trial, prediction)
ppt_data = ppt_data %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=sum(n))

## Helper functions
sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17

hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}


## Setup
iters = seq(100,1500,100)

## Fit
conditions = c('construct','combine','decon','flip')
batches = c('a','b')
fit_pred = function(model, iter) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0('../model_data/',tolower(model),'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add ppt data
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  # Return
  return (list(model=toupper(model), iter=iter, fit=out$value, param=out$par))
}


## Fit all
fit_results = read.csv(file='cross_valids/processes.csv') %>% select(-X)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('ag',i)))
  fit_results = rbind(fit_results,data.frame(fit_pred('agr',i)))
}
#write.csv(fit_results, file='cross_valids/processes.csv')


## Quick plot
fit_results %>%
  #filter(iter>101, iter<80001) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line()



#### Play with pcfg data ####
load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(exp_id, condition, batch, trial, prediction)
ppt_data = ppt_data %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=sum(n))

## Helper functions
sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17

hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}


## Setup
iters = c(seq(100,1000,100), seq(2000,10000,1000))

## Fit
conditions = c('construct','combine','decon','flip')
batches = c('a','b')
fit_pred = function(model, iter) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0('../model_data/',tolower(model),'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add ppt data
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  # Return
  return (list(model=toupper(model), iter=iter, fit=out$value, param=out$par))
}


## Fit all
fit_results = read.csv(text='model,iter,fit,param')
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('pcfg',i)))
}
write.csv(fit_results, file='cross_valids/processes.csv')


## Quick plot
fit_results %>%
  #filter(iter>101, iter<80001) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line()



#### Overall fits per iteration ####
## Load mturk data and aggregate per condition
load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(exp_id, condition, batch, trial, prediction)
ppt_data = ppt_data %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=sum(n))


## Helper functions
sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17

hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}


## Setup
models = c('AG', 'AGR', 'PCFG', 'PCFGR')
iters = c(10,50,100, seq(200,1000,200), seq(2000,10000,2000), seq(20000,100000,20000))

## Fit
conditions = c('construct','combine','decon','flip')
batches = c('a','b')
fit_pred = function(model, iter) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0('../model_data/',tolower(model),'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
    
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add ppt data
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  # Return
  return (list(model=toupper(model), iter=iter, fit=out$value, param=out$par))
}


## Fit all
fit_results = read.csv(text='model,iter,fit,param')
for (m in models) {
  for (i in iters) {
    fit_results = rbind(fit_results,data.frame(fit_pred(m,i)))
  }
}
write.csv(fit_results, file='cross_valids/processes.csv')


## Quick plot
fit_results %>%
  filter(iter<10001) %>%
  #filter(iter>101, iter<80001) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line()





#### Fixed fits ####
# Load mturk data and aggregate per trial
load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(exp_id, condition, batch, trial, prediction)

## Read raw model predictions
get_filepath = function(model, exp_id, cond, phase) {
  return(paste0(
    '../model_data/', tolower(model), '/exp_', exp_id, '/',
    cond, '_preds_', tolower(phase), '.csv'
  ))
}

## Helper functions
sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17

## Hazard fitting
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}

hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}

#### End of Packages, data, helper funcs ########

#### AG & PCFG model per experiment ########

## Get all model data
model = 'AG_rj'
model_data = read.csv(text='condition,batch,trial,prediction,prob')
for (eid in seq(4)) {
  conditions = if (eid<3) c('construct', 'decon', 'combine') else c('combine', 'flip')
  for (cond in conditions) {
    for (phase in c('a', 'b')) {
      model_raw=read.csv(get_filepath(model,eid,cond,phase)) %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(phase), exp_id=eid) %>%
        select(exp_id, condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  } 
}


## Add mturk data
model_ppt=model_data %>%
  left_join(ppt_data, by=c('exp_id', 'condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(exp_id, condition, batch, trial, prediction)

## Cross-validation on conditions
cross_vl = read.csv(text='model,exp_id,params,LL')
cross_vl = read.csv('cross_valids/cross_valids_per_exp.csv') %>% select(-X)
conditions = c('construct', 'decon', 'combine', 'flip')

for (eid in seq(4)) {
#for (cond in conditions) {
  ## Train on other three conditions
  training = model_ppt[model_ppt$exp_id!=eid,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = model_ppt[model_ppt$exp_id==eid,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, exp_id=eid, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=paste0('cross_valids/cross_valids_per_exp_40.csv'))

cross_vl %>%
  group_by(model) %>%
  summarise(sum(LL))

cross_vl %>%
  select(model, exp_id, LL) %>%
  spread(exp_id, LL)

#############################


#### AG & PCFG model per condition ########

## Get all model data
model = 'PCFG_rj'
model_data = read.csv(text='exp_id,condition,batch,trial,prediction,prob')
for (eid in seq(4)) {
  conditions = if (eid<3) c('construct', 'decon', 'combine') else c('combine', 'flip')
  for (cond in conditions) {
    for (phase in c('a', 'b')) {
      model_raw=read.csv(get_filepath(model,eid,cond,phase)) %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(phase), exp_id=eid) %>%
        select(exp_id, condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  } 
}


## Add mturk data
model_ppt=model_data %>%
  left_join(ppt_data, by=c('exp_id', 'condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(exp_id, condition, batch, trial, prediction)


## Collapse conditions
model_ppt_conds = model_ppt %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(prob=sum(prob)/n(), n=sum(n))

## Cross-validation on conditions
#cross_vl = read.csv(text='model,cond,params,LL')
#cross_vl = read.csv('cross_valids/cross_valids_per_exp.csv') %>% select(-X)
conditions = c('construct', 'decon', 'combine', 'flip')

for (cond in conditions) {
  ## Train on other three conditions
  training = model_ppt_conds[model_ppt_conds$condition!=cond,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = model_ppt_conds[model_ppt_conds$condition==cond,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, condition=cond, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=paste0('cross_valids/cross_valids_per_exp_40.csv'))

cross_vl %>%
  group_by(model) %>%
  summarise(sum(LL))

cross_vl %>%
  select(model, condition, LL) %>%
  spread(condition, LL)

#############################




#### Multinom ####
model = 'multinom'
experi = 'exp_2'

load(paste0('../data/', experi, '_cleaned.rdata'))
cross_vl=read.csv(text='model,expt,condition,phase,trial,params,LL')

for (cond in c('construct', 'decon', 'combine')) {
  for (phase in c('a', 'b')) {
    for (tid in seq(8)) {
      # Prep data
      data_path = paste0('alt_models/multinom_preds/', experi, '/', cond, '_preds_', tolower(phase), '.csv')
      model_raw = read.csv(data_path) %>%
        select(term, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial)))) %>%
        select(trial, term, prob)
      ppt_list = expand.grid(condition=cond, phase=toupper(phase), trial=seq(8), term=seq(0,16))
      ppt_model_data = df.tw %>% 
        filter(condition==cond, batch==toupper(phase)) %>%
        mutate(phase=batch, term=prediction) %>%
        count(condition, phase, trial, term) %>%
        right_join(ppt_list, by=c('condition', 'phase', 'trial', 'term')) %>%
        mutate(n=ifelse(is.na(n), 0, n)) %>%
        arrange(condition, phase, trial, term) %>%
        left_join(model_raw, by=c('trial', 'term'))
      # Optimize
      out = optim(par=0, sftmx_trial, method="L-BFGS-B", data=filter(ppt_model_data, trial!=tid))
      # Perform
      nll = sftmx_trial(filter(ppt_model_data, trial==tid), out$par)
      # Save
      cross_vl = rbind(cross_vl, data.frame(
        model=model, expt=experi, condition=cond, phase=toupper(phase), trial=tid, params=out$par, LL=-nll
      ))
    }
  }
}
write.csv(cross_vl, file=paste0('cross_valids/', model, '_', experi, '.csv'))


#### Overall cross validation results ####
cross_vl=read.csv(text='model,expt,condition,phase,trial,params,LL')
for (mm in c('AG', 'PCFG', 'similarity', 'multinom')) {
  for (expt in seq(2)) {
    cross_vl = rbind(cross_vl, read.csv(paste0('cross_valids/', mm, '_exp_', expt, '.csv'))%>%select(-X))
  }
}
cross_vl %>%
  group_by(model, expt) %>%
  summarise(LL=sum(LL)) %>%
  arrange(expt, desc(LL))









