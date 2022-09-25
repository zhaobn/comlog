
library(dplyr)
library(tidyr)
library(ggplot2)
library(nnet) # for multinom

options(scipen=999) 
options(stringsAsFactors = FALSE)
options(warn=-1)
conditions = c('construct','combine','decon','flip')
normalize=function(vec) return(vec/sum(vec))

load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% 
  count(exp_id, condition, batch, trial, prediction) %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=sum(n))

fits_init = read.csv(text='model,condition,batch,trial,nll')
df_init = read.csv(text='condition,batch,trial,prediction,prob,fitted,n')

fits_all = fits_init

#### Symbolic models prep ####

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
convert_haz = function(h, n=NA) if (is.na(n)) return(sigmoid(h)/NCHUNK) else return(round(sigmoid(h)/NCHUNK, n))
read_model_data = function(model_name, iter) {
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in c('a','b')) {
      model_raw=read.csv(paste0('../model_data/',tolower(model_name),'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  return(model_data)
}


#### AG model ####
ag.all = read_model_data('AG', 5000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

ag_fits = fits_init
df.ag = df_init
for (cond in conditions) {
  # Held-out one trial
  training = ag.all %>% filter(condition!=cond)
  trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
      
  testing = ag.all %>% filter(condition==cond)
  tested = hazdata(testing, trained$par)
      
  # Save
  ag_fits = rbind(ag_fits, data.frame(model='AG',condition=cond,nll=sum(tested$ll)))
  df.ag = rbind(df.ag, tested %>% select(condition,batch,trial,prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, ag_fits)


#### PCFG (Rational Rules) model  ####
rr.all = read_model_data('PCFG', 100000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

rr_fits = fits_init
df.rr = df_init
for (cond in conditions) {
  # Held-out one trial
  training = rr.all %>% filter(condition!=cond)
  trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  testing = rr.all %>% filter(condition==cond)
  tested = hazdata(testing, trained$par)
  
  # Save
  rr_fits = rbind(rr_fits, data.frame(model='RR',condition=cond,nll=sum(tested$ll)))
  df.rr = rbind(df.rr, tested %>% select(condition,batch,trial, prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, rr_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))


#### Mix models  ####
get_mix_data = function(base_model, iter) {
  mix_data = read.csv(text='condition,batch,trial,prediction,fprob,bprob')
  forward_data = read_model_data(base_model, iter)
  setups = list(
    list(cond = 'construct', rj_cond = 'decon'),
    list(cond = 'decon', rj_cond = 'construct'),
    list(cond = 'combine', rj_cond = 'flip'),
    list(cond = 'flip', rj_cond = 'combine')
  ) 
  for (pair in setups) {
    fdata = forward_data %>% filter(condition==pair['cond']) %>% rename(fprob=prob)
    bdata = forward_data %>% filter(condition==pair['rj_cond']) %>% rename(bprob=prob) %>% select(-condition)
    mdata = fdata %>% left_join(bdata, by=c('batch','trial','prediction'))
    mix_data = rbind(mix_data, mdata)
  }
  return(mix_data)
}

hazmix = function(par, data) {
  mix_weight = par[1]
  haz_par = par[2]
  
  backward_weight = exp(mix_weight)/(1+exp(mix_weight))
  forward_weight = 1-backward_weight
  
  data$prob = data$fprob
  data$prob[data$batch=='B']=data$fprob[data$batch=='B']*forward_weight+data$bprob[data$batch=='B']*backward_weight
  
  data$transformed = sigmoid(haz_par)/NCHUNK+(1-sigmoid(haz_par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}
hazmixdata = function(par, data) {
  mix_weight = par[1]
  haz_par = par[2]
  
  backward_weight = exp(mix_weight)/(1+exp(mix_weight))
  forward_weight = 1-backward_weight
  
  data$prob = data$fprob
  data$prob[data$batch=='B']=data$fprob[data$batch=='B']*forward_weight+data$bprob[data$batch=='B']*backward_weight
  
  data$transformed = sigmoid(haz_par)/NCHUNK+(1-sigmoid(haz_par))*data$prob
  data$ll = log(data$transformed)*data$n
  
  return(data)
}

agr_fits = fits_init
df.agr = df_init
ag_mix = get_mix_data('ag', 2000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)
for (cond in conditions) {
  # Held-out one trial
  training = ag_mix %>% filter(condition!=cond)
  trained = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=training)
  
  testing = ag_mix %>% filter(condition==cond)
  tested = hazmixdata(c(trained$par[1],trained$par[2]), testing)
  
  # Save
  agr_fits = rbind(agr_fits, data.frame(model='AGR',condition=cond,nll=sum(tested$ll)))
  df.agr = rbind(df.agr, tested %>% select(condition,batch,trial,prediction,prob,fitted=transformed,n))
}
fits_all = fits_all %>% filter(model!='AGR')
fits_all = rbind(fits_all, agr_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))


## RR mix
rrr_fits = fits_init
df.rrr = df_init
rr_mix = get_mix_data('pcfg', 100000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

for (cond in conditions) {
  # Held-out one trial
  training = rr_mix %>% filter(condition!=cond)
  trained = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=training)
  
  testing = rr_mix %>% filter(condition==cond)
  tested = hazmixdata(c(trained$par[1],trained$par[2]), testing)
  
  # Save
  rrr_fits = rbind(rrr_fits, data.frame(model='RRR',condition=cond,nll=sum(tested$ll)))
  df.rrr = rbind(df.rrr, tested %>% select(condition,batch,trial,prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, rrr_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))

save(df.ag, df.agr, df.rr, df.rrr, file = '../data/fitted_models.Rdata')
write.csv(fits_all, file='../data/fits_all.csv')

## Play with them so far
baseline_stats = ppt_data %>% 
  group_by(condition) %>% 
  summarise(n=sum(n)) %>%
  mutate(baseline=n*log(1/17)) %>% select(-n)
fits_all %>% group_by(model, condition) %>%
  summarise(nll=sum(nll)) %>%
  left_join(baseline_stats, by='condition') %>%
  mutate(improv=nll-baseline) %>%
  ggplot(aes(x=reorder(model, -nll), y=improv, fill=condition)) +
  geom_bar(position="stack", stat="identity")



#### Similarity ####
tasks = read.csv('../data/tasks/tasks.csv')
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
  
  return(hazdata(model_ppt, par[['t']]))
  #return(hazfit(model_ppt, par[['t']]))
}


data = expand.grid(condition=conditions, batch=c('A', 'B'),trial=seq(8)) %>% arrange(condition, batch, trial)
# df.sim = get_sim_pred(data, list('a'=.99, 'b'=.81, 'c'=.71, 't'=0.0381))
# df.sim = df.sim %>% select(condition, batch, trial, prediction, prob, fitted=transformed)
sim.out = optim(par=default_param, get_sim_pred, data=data)
model_fits = rbind(model_fits,data.frame(model='similarity',nll=sim.out$value,haz=convert_haz(sim.out$par[4],4),
                                         par=paste0(round(sim.out$par[1],2),',',round(sim.out$par[2],2),',',round(sim.out$par[3],2))))


#### Similarity model ####
tasks = read.csv('../data/tasks/tasks.csv')
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
  
  #return(hazdata(model_ppt, par[['t']]))
  return(hazfit(model_ppt, par[['t']]))
}

get_sim_df = function(data, par) {
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
  
  return(hazdata(model_ppt, par[['t']]))
}

data = expand.grid(condition=conditions, batch=c('A', 'B'),trial=seq(8)) %>% arrange(condition, batch, trial)
sim_fits = fits_init
df.sim = df_init
for (cond in conditions) {
  # Held-out one trial
  training = data %>% filter(condition!=cond)
  trained = optim(par=default_param, get_sim_pred, data=training)
  
  testing = data %>% filter(condition==cond)
  tested = get_sim_df(testing, trained$par)
  
  # Save
  sim_fits = rbind(sim_fits, data.frame(model='Similarity',condition=cond,nll=sum(tested$ll)))
  df.sim = rbind(df.sim, tested %>% select(condition,batch,trial, prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, sim_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))

#### Linear models ####

lm_preds = expand.grid(condition=conditions,batch=c('A','B'),trial=seq(8),prediction=c(0,seq(16)),prob=0) %>%
  arrange(condition,batch,trial,prediction)
for (cond in conditions) {
  for (bt in c('A','B')) {
    # Prep data for lm
    if (bt=='A') {
      obs = tasks %>% filter(condition==cond,batch=='A')
    } else {
      obs = tasks %>% filter(condition==cond,batch!='gen')
    }
    m = lm(result_block~stripe+dot+block, data = obs)
    
    # Get predictions
    for (tid in seq(8)) {
      gen_task = tasks %>% filter(condition==cond,batch=='gen', trial==tid)
      lm_pred = round(suppressWarnings(predict(m, gen_task))[[1]],2)
      
      lower_bd = floor(lm_pred)
      upper_bd = ceiling(lm_pred)
      lm_preds = lm_preds %>%
        mutate(prob=ifelse(condition==cond&batch==bt&trial==tid&prediction==lower_bd, upper_bd-lm_pred, prob)) %>%
        mutate(prob=ifelse(condition==cond&batch==bt&trial==tid&prediction==upper_bd, lm_pred-lower_bd, prob))
    }
  }
}

lm_ppt=lm_preds %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

lm_fits = fits_init
df.lm = df_init
for (cond in conditions) {
  # Held-out one trial
  training = lm_ppt %>% filter(condition!=cond)
  trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  testing = lm_ppt %>% filter(condition==cond)
  tested = hazdata(testing, trained$par)
  
  # Save
  lm_fits = rbind(lm_fits, data.frame(model='LinReg',condition=cond,nll=sum(tested$ll)))
  df.lm = rbind(df.lm, tested %>% select(condition,batch,trial, prediction,prob,fitted=transformed,n))
}
fits_all = fits_all %>% filter(model!='LinReg')
fits_all = rbind(fits_all, lm_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))


## Multinom
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

multinom_preds=multinom_preds %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

mm_fits = fits_init
df.mm = df_init
for (cond in conditions) {
  # Held-out one trial
  training = multinom_preds %>% filter(condition!=cond)
  trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  testing = multinom_preds %>% filter(condition==cond)
  tested = hazdata(testing, trained$par)
  
  # Save
  mm_fits = rbind(mm_fits, data.frame(model='Multinom',condition=cond,nll=sum(tested$ll)))
  df.mm = rbind(df.mm, tested %>% select(condition,batch,trial, prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, mm_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))


## Gaussian Process regression
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

gp_fits = fits_init
df.gp = df_init
for (cond in conditions) {
  # Held-out one trial
  training = gp_ppt %>% filter(condition!=cond)
  trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
  
  testing = gp_ppt %>% filter(condition==cond)
  tested = hazdata(testing, trained$par)
  
  # Save
  gp_fits = rbind(gp_fits, data.frame(model='GpReg',condition=cond,nll=sum(tested$ll)))
  df.gp = rbind(df.gp, tested %>% select(condition,batch,trial, prediction,prob,fitted=transformed,n))
}
fits_all = rbind(fits_all, gp_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))

save(df.sim, df.gp, df.lm, df.mm, file='../data/alter_fitted.Rdata')


















