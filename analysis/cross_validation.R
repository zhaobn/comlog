
#### Packages, data, core funcs ########
library(dplyr)
library(tidyr)
library(ggplot2)


#### Global prep #####
load('../data/all_cleaned.Rdata')
ppt_data <- df.tw %>% count(condition, batch, trial, prediction)

conditions <- c('construct', 'decon', 'combine', 'flip')
save_path = function(model) return(paste0('cross_valids/', tolower(model), '_cl.csv'))

sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}
normalize=function(vec) return(vec/sum(vec))

#### Bayesian-symbolic models #####
## Helper
get_data_path <- function(cond, phase, model, iter) {
  return(paste0('../model_data/', tolower(model), '/process_', iter, '/', 
                cond, '_preds_', tolower(phase), '.csv'))
}


## Set-up
model='pcfg'
iter=100000

## Read model predictions
model_data = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in conditions) {
  for (phase in c('a', 'b')) {
    model_raw=read.csv(get_data_path(cond, phase, model, iter)) %>%
      select(term=terms, starts_with('prob')) %>%
      gather('trial', 'prob', -term) %>%
      mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
             prediction=term, condition=cond, batch=toupper(phase)) %>%
      select(condition, batch, trial, prediction, prob)
    
    model_data = rbind(model_data, model_raw)
  }
} 

## Add participant (ppt) data
model_ppt=model_data %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

## Cross-validation by conditions
cross_vl = read.csv(text='model,condition,params,LL')

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

write.csv(cross_vl, file=save_path(model))


#### Similarity-based models ####
default_param = list('a'=1, 'b'=1, 'c'=1, 't'=0.2)
all_preds = data.frame(prediction=seq(0,16))

## Function to fit
get_sim_pred = function(data, par) {
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  
  for (i in 1:nrow(data)) {
    i_cond = data[i, 'condition']
    i_phase = data[i, 'batch']
    i_gen = data[i, 'trial']
    if (i_phase=='A') {
      learnings = tasks %>% filter(condition==i_cond, batch==i_phase)
    } else {
      learnings = tasks %>% filter(condition==i_cond, batch!='gen')
    }
    
    # Attach gen task details for calculation
    gen_data = tasks %>% 
      filter(condition==i_cond, batch=='gen', trial==i_gen) %>%
      select(stripe, dot, block) %>%
      as.list()
    learnings = learnings %>%
      mutate(gen_stripe=gen_data[['stripe']], gen_dot=gen_data[['dot']], gen_block=gen_data[['block']]) %>%
      mutate(sim_dist=par[['a']]^2*abs(stripe-gen_stripe)+
               par[['b']]^2*abs(dot-gen_dot)+
               par[['c']]^2*abs(block-gen_block)) %>%
      mutate(sim_score=exp(-sim_dist))
    learnings$sim_normed = normalize(learnings$sim_score)
    
    # Get preds
    preds = learnings %>%
      select(prediction=result_block, prob=sim_normed) %>%
      group_by(prediction) %>%
      summarise(prob=sum(prob)) %>%
      right_join(all_preds, by='prediction') %>%
      mutate(prob=ifelse(is.na(prob), 0, prob), condition=i_cond, batch=i_phase, trial=i_gen) %>%
      arrange(prediction) %>%
      select(condition,batch,trial,prediction,prob)
    
    model_data = rbind(model_data, preds)
    
  }
  
  model_ppt = model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n), 0, n))
  
  return(hazfit(model_ppt, par[['t']]))
}


## Fit per condition
tasks = read.csv('../data/tasks/tasks.csv') %>% select(-X)
cross_vl = read.csv(text='model,condition,params,LL,a,b,c')


test_cond = 'flip'
trainings = expand.grid(condition=conditions[conditions!=test_cond],
                        batch=c('A', 'B'),trial=seq(8)) %>%
  arrange(condition, batch, trial)

out = optim(par=default_param, get_sim_pred, data=trainings)


## Save
test = expand.grid(condition=test_cond, batch=c('A', 'B'),trial=seq(8)) %>%
  arrange(condition, batch, trial)

test_result = as.list(out$par)
test_result[['LL']] = -get_sim_pred(test, as.list(out$par))
test_result[['model']] = 'similarity'
test_result[['condition']] = test_cond
test_result_df = as.data.frame(test_result) %>%
  select(model,condition,params=t,LL,a,b,c)

cross_vl = rbind(cross_vl, test_result_df)
write.csv(cross_vl, file=save_path('similarity'))



#### Linear regression ####



#### Play with Gaussian ####
x=seq(0,16)
y=dnorm(x, mean=5, sd=1/3)




#### Overall results ####
cross_vl = read.csv(text='model,condition,params,LL')
for (model in c('ag', 'agr', 'pcfg', 'similarity')) {
  if (model=='similarity') {
    model_cl = read.csv(save_path(model)) %>% select(-c(X,a,b,c))
  } else {
    model_cl = read.csv(save_path(model)) %>% select(-X)
  }
  cross_vl = rbind(cross_vl, model_cl)
}


cross_vl %>%
  group_by(model) %>%
  summarise(sum(LL))

cross_vl %>%
  select(model, condition, LL) %>%
  spread(condition, LL) %>%
  mutate(overall=combine+construct+decon+flip) %>%
  select(model, construct, decon, combine, flip, overall)








