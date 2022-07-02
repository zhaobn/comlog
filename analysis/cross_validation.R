
#### Packages, data, core funcs ########
library(dplyr)
library(tidyr)
library(ggplot2)
library(nnet) # for multinom


#### Global prep #####
options(scipen = 999999)

load('../data/all_cleaned.Rdata')
ppt_data <- df.tw %>% count(condition, batch, trial, prediction)

conditions <- c('construct', 'decon', 'combine', 'flip')
save_path = function(model) return(paste0('cross_valids/', tolower(model), '_cl.csv'))

tasks = read.csv('../data/tasks/tasks.csv')

sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
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
  
  # return(hazdata(model_data, par[['t']]))
  model_ppt = model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n), 0, n))

  return(hazfit(model_ppt, par[['t']]))
}


## Fit per condition
cross_vl = read.csv(text='model,condition,params,LL,a,b,c')

test_cond = 'construct'
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


## Get fitted preds
sim_pars = read.csv('cross_valids/similarity_cl.csv')

get_sim_fitted = function(test_cond) {
  trainings = expand.grid(condition=conditions[conditions==test_cond],
                          batch=c('A', 'B'),trial=seq(8)) %>%
    arrange(condition, batch, trial)
  fitted = sim_pars %>% filter(condition==test_cond) %>%
    select(a, b, c, t=params) %>%
    as.list()
  
  df = get_sim_pred(trainings, fitted) %>% 
    mutate(model='similarity') %>%
    select(model, condition, batch, trial, prediction, fitted=transformed)
  
  return(df)
}


df.sim = get_sim_fitted('construct')
for (c in c('decon', 'combine', 'flip')) {
  df.sim = rbind(df.sim, get_sim_fitted(c))
}

#### Linear regression ####
## Get linear regression model preds
lm_preds = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in conditions) {
  for (batch in c('A','B')) {
    # Prep data for lm
    if (batch=='A') {
      obs = tasks %>% filter(condition==cond,batch=='A')
    } else {
      obs = tasks %>% filter(condition==cond,batch!='gen')
    }
    m = lm(result_block~stripe+dot+block, data = obs)
    
    # Get predictions
    for (tid in seq(8)) {
      gen_task = tasks %>% filter(condition==cond,batch=='gen', trial==tid)
      pred = round(predict(m, gen_task)[[1]])
      pred_df = data.frame(condition=rep(cond,NCHUNK),batch=rep(batch,NCHUNK),
                           trial=rep(tid,NCHUNK),prediction=seq(0,16),prob=rep(0,NCHUNK))
      pred_df[pred_df$prediction==pred,'prob']=1
      
      lm_preds=rbind(lm_preds, pred_df)
    }
  }
}

## Fit hazard noise parameter & cross validate
lm_ppt=lm_preds %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

cross_vl = read.csv(text='model,condition,params,LL')
model='lm'
for (cond in conditions) {
  ## Train on other three conditions
  training = lm_ppt[lm_ppt$condition!=cond,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = lm_ppt[lm_ppt$condition==cond,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, condition=cond, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=save_path(model))

## Get fitted preds
lm_pars = read.csv('cross_valids/lm_cl.csv')

get_lm_fitted = function(test_cond) {
  
  fitted = lm_pars %>% filter(condition==test_cond) %>% pull(params)
  
  df = hazdata(filter(lm_preds,condition==test_cond), fitted) %>%
    mutate(model='lm') %>%
    select(model, condition, batch, trial, prediction, fitted=transformed)
  
  return(df)
}


df.lm = get_sim_fitted('construct')
for (c in c('decon', 'combine', 'flip')) {
  df.lm = rbind(df.lm, get_lm_fitted(c))
}


#### Multinomial logistic regression ####
## Get logistic regression model preds
multinom_preds = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in conditions) {
  for (batch in c('A','B')) {
    # Prep data for multinom
    if (batch=='A') {
      obs = tasks %>% filter(condition==cond,batch=='A')
    } else {
      obs = tasks %>% filter(condition==cond,batch!='gen')
    }
    obs = obs %>% mutate(result_block=as.factor(as.character(result_block)))
    m = multinom(result_block~stripe+dot+block, data = obs)
    
    # Get predictions
    for (tid in seq(8)) {
      gen_task = tasks %>% filter(condition==cond,batch=='gen', trial==tid)
      pred = predict(m, gen_task, 'probs')
      pred_df=data.frame(prediction=names(pred),prob=pred) %>% 
        mutate(prediction=as.numeric(prediction))
      
      ret_df = data.frame(condition=rep(cond,NCHUNK),batch=rep(batch,NCHUNK),
                          trial=rep(tid,NCHUNK),prediction=seq(0,16))
      ret_df = ret_df %>%
        left_join(pred_df, by='prediction') %>%
        mutate(prob=ifelse(is.na(prob), 0, prob))
      
      multinom_preds=rbind(multinom_preds, ret_df)
    }
  }
}

## Fit hazard noise parameter & cross validate
multinom_preds=multinom_preds %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

cross_vl = read.csv(text='model,condition,params,LL')
model='multinom'
for (cond in conditions) {
  ## Train on other three conditions
  training = multinom_preds[multinom_preds$condition!=cond,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = multinom_preds[multinom_preds$condition==cond,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, condition=cond, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=save_path(model))


## Get fitted preds
mm_pars = read.csv('cross_valids/multinom_cl.csv')

get_mm_fitted = function(test_cond) {

  fitted = mm_pars %>% filter(condition==test_cond) %>% pull(params)
  
  df = hazdata(filter(multinom_preds,condition==test_cond), fitted) %>%
    mutate(model='multinom') %>%
    select(model, condition, batch, trial, prediction, fitted=transformed)
  
  return(df)
}


df.mm = get_mm_fitted('construct')
for (c in c('decon', 'combine', 'flip')) {
  df.mm = rbind(df.mm, get_mm_fitted(c))
}


#### Gaussian Process regression #####
model='GPR'

gp_pars=read.csv('../python/gp/gp_reg_results.csv') %>% select(-X)
gp_preds = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in conditions) {
  for (bat in c('A','B')) {
    for (tid in seq(8)) {
      # Bin predictions to match task output
      gen_task = tasks %>% filter(condition==cond,batch=='gen', trial==tid)
      gp_task_par = gp_pars %>% filter(condition==cond,batch==bat, trial==tid)
      bins = seq(0,16)
      preds = dnorm(bins, mean=gp_task_par$mean, sd=sqrt(gp_task_par$variance)) 

      pred_df=data.frame(
        condition=rep(cond, NCHUNK),
        batch=rep(bat, NCHUNK),
        trial=rep(tid, NCHUNK),
        prediction=bins,
        prob=normalize(preds))
      
      gp_preds=rbind(gp_preds, pred_df)
    }
  }
}


gp_ppt=gp_preds %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

cross_vl = read.csv(text='model,condition,params,LL')
for (cond in conditions) {
  ## Train on other three conditions
  training = gp_ppt[gp_ppt$condition!=cond,]
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  ## Test on held-out set
  test = gp_ppt[gp_ppt$condition==cond,]
  fitted = hazdata(test, out$par)
  
  ## Save
  cross_vl = rbind(cross_vl, data.frame(
    model=model, condition=cond, params=out$par, LL=sum(fitted$ll)
  ))
}

write.csv(cross_vl, file=save_path(model))


## Get fitted preds
gp_pars = read.csv('cross_valids/gpr_cl.csv')

get_gp_fitted = function(test_cond) {
  
  fitted = mm_pars %>% filter(condition==test_cond) %>% pull(params)
  
  df = hazdata(filter(gp_preds,condition==test_cond), fitted) %>%
    mutate(model='GPR') %>%
    select(model, condition, batch, trial, prediction, fitted=transformed)
  
  return(df)
}


df.gpr = get_gp_fitted('construct')
for (c in c('decon', 'combine', 'flip')) {
  df.gpr = rbind(df.gpr, get_gp_fitted(c))
}



#### Random baseline ####
rand_baseline = df.tw %>%
  count(condition) %>%
  mutate(LL=log(1/NCHUNK)*n, model='random', params='') %>%
  select(model,condition, params,LL)
write.csv(rand_baseline, file=save_path('random'))




#### Overall results ####
cross_vl = read.csv(text='model,condition,params,LL')
for (model in c('ag', 'agr', 'pcfg', 'similarity', 'lm', 'gpr', 'multinom', 'random')) {
  if (model=='similarity') {
    model_cl = read.csv(save_path(model)) %>% select(-c(X,a,b,c))
  } else {
    model_cl = read.csv(save_path(model)) %>% select(-X)
  }
  cross_vl = rbind(cross_vl, model_cl)
}

cross_vl %>%
  group_by(model) %>%
  summarise(LL=sum(LL)) %>%
  arrange(desc(LL))

cross_vl %>%
  mutate(LL=round(-LL)) %>%
  select(model, condition, LL) %>%
  spread(condition, LL) %>%
  mutate(overall=combine+construct+decon+flip) %>%
  select(model, construct, decon, combine, flip, overall) %>%
  arrange(overall) %>%
  write.csv('cross_valids/sum.csv')


save(df.sim, df.lm, df.mm, df.gpr, file='../data/alter_fitted.Rdata')






