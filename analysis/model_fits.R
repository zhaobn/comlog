
#### Packages, data, core funcs ########
library(dplyr)
library(tidyr)
library(ggplot2)


#### Prep fitted model data ####

sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  # data$fitted = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  return(data)
}


conditions = c('construct','combine','decon','flip')
batches = c('a','b')
get_pred = function(model, iter, par) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0('../model_data/',tolower(model),'/process_', iter, '/', cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add fitted probs
  model_fitted=hazdata(model_data, par)
  
  # Return
  return (model_fitted)
}


## Get fitted model data
options(scipen = 999)
fit_results = read.csv(file='cross_valids/processes.csv') %>% select(-X)
max_iters = list('ag'=5000, 'agr'=5000, 'pcfg'=100000)

df.ag=get_pred('ag', max_iters[['ag']], 
               filter(fit_results, model==toupper('ag'), iter==max_iters[['ag']])$param)
df.agr=get_pred('agr', max_iters[['agr']], 
                filter(fit_results, model==toupper('agr'), iter==max_iters[['agr']])$param)
df.pcfg=get_pred('pcfg', max_iters[['pcfg']], 
                 filter(fit_results, model==toupper('pcfg'), iter==max_iters[['pcfg']])$param)
save(df.ag, df.agr, df.pcfg, file='../data/fitted_models.Rdata')

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
# fit_results = read.csv(file='cross_valids/processes.csv') %>% select(-X)
# for (i in iters) {
#   fit_results = rbind(fit_results,data.frame(fit_pred('ag',i)))
#   fit_results = rbind(fit_results,data.frame(fit_pred('agr',i)))
# }
#write.csv(fit_results, file='cross_valids/processes.csv')


#iters = c(10,50, 100, seq(200, 1000, 200), seq(2000, 10000, 2000), seq(20000, 100000, 20000))
#options(scipen=999)
iters= c(seq(100,1500,100),seq(2000,5000,500)) #c(seq(100,1000, 100), seq(2000, 10000, 1000))

fit_results = read.csv(file='cross_valids/processes.csv') %>% 
  filter(X<63, model!='AGR') %>%
  select(-X) 

for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('agr',i)))
}



## Quick plot
fit_results %>%
  #filter(iter>101, iter<80001) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line()


## Plot for reasoning workshop
full_iters = fit_results %>%
  filter(model=='PCFG') %>%
  pull(iter) %>%
  unique()
ag_iters = fit_results %>%
  filter(model=='AG') %>%
  pull(iter) %>%
  unique()
ag_batch_iters = setdiff(full_iters, ag_iters)

ag_last_fit = fit_results %>%
  filter(model=='AG', iter==max(ag_iters))
agr_last_fit = fit_results %>%
  filter(model=='AGR', iter==max(ag_iters))

ag_batches = do.call("rbind", replicate(length(ag_batch_iters), ag_last_fit, simplify = FALSE))
ag_batches$iter = ag_batch_iters

agr_batches = do.call("rbind", replicate(length(ag_batch_iters), agr_last_fit, simplify = FALSE))
agr_batches$iter = ag_batch_iters

all_fits = rbind(
  fit_results, ag_batches, agr_batches
)
# Save just in case
# write.csv(all_fits, file='cross_valids/processes_0612.csv')


all_fits %>%
  #filter(iter>101, iter<80001) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line() +
  theme_classic() +
  labs(y='Log Likelihood', x='Iteration')

# Save AG & AGR

ag_fits = fit_results %>%
  filter(model!='PCFG')
#write.csv(ag_fits, file='cross_valids/processes_ag.csv')


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









