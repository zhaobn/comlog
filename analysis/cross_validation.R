
# Use cross-validation to evaluate models
# For each experiment, each condition, and each phase (=> six gen tasks),
# Train on 5 tasks' data for optimal model parameter(s),
# And apply the trained parameter on the held-out task to compute log likelihood (LL)
# Save parameters & LL together with experiment ID, condition name, phase, task, and model name
# Take the _sum_ over experiment partition as the model's performance in the corresponding experiment

# Update 22 May 2022
# Use hazard prob for noise + log softmax (keep original distribution)

#### Packages, data, core funcs ########

library(dplyr)
library(tidyr)

## Load mturk data and aggregate per trial
load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(condition, batch, trial, prediction)

## Read raw model predictions
get_filepath = function(model, cond, phase) {
  return(paste0(
    '../model_data/', tolower(model), '/', 
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

#### AG & PCFG model ########

## Get all model data
model = 'PCFG'
model_data = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in c('construct', 'decon', 'combine', 'flip')) {
  for (phase in c('a', 'b')) {
    model_raw=read.csv(get_filepath(model,cond,phase)) %>%
      select(term=terms, starts_with('prob')) %>%
      gather('trial', 'prob', -term) %>%
      mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
            prediction=term, condition=cond, batch=toupper(phase)) %>%
      select(condition, batch, trial, prediction, prob)

    model_data = rbind(model_data, model_raw)
  }
} 

## Add mturk data
model_ppt=model_data %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

## Cross-validation on conditions
#cross_vl = read.csv(text='model,condition,params,LL')
conditions = c('construct', 'decon', 'combine', 'flip')
for (cond in conditions) {
  ## Train on other three conditions
  training = model_ppt[model_ppt$condition!=cond,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = model_ppt[model_ppt$condition==cond,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, condition=cond, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=paste0('cross_valids.csv'))

cross_vl %>%
  filter(condition!='flip') %>%
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









