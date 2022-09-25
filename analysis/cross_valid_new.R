
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

#### Fit hazard prob ####

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


## AG model
ag.all = read_model_data('AG', 5000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

ag_fits = fits_init
df.ag = df_init
for (cond in conditions) {
  for (bt in c('A','B')) {
    for (tid in seq(8)) {
      
      # Held-out one trial
      training = ag.all %>% filter(condition==cond, batch==bt, trial!=tid)
      trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
      
      testing = ag.all %>% filter(condition==cond, batch==bt, trial==tid)
      tested = hazdata(testing, trained$par)
      
      # Save
      ag_fits = rbind(ag_fits, data.frame(model='AG',condition=cond,batch=bt,
                                          trial=tid,nll=sum(tested$ll)))
      df.ag = rbind(df.ag, tested %>% select(condition,batch,trial,
                                             prediction,prob,fitted=transformed,n))
    }
  }
}
fits_all = rbind(fits_all, ag_fits)


## PCFG (Rational Rules) model
rr.all = read_model_data('PCFG', 100000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

rr_fits = fits_init
df.rr = df_init
for (cond in conditions) {
  for (bt in c('A','B')) {
    for (tid in seq(8)) {
      
      # Held-out one trial
      training = rr.all %>% filter(condition==cond, batch==bt, trial!=tid)
      trained = optim(par=0, hazfit, method="L-BFGS-B", data=training)
      
      testing = rr.all %>% filter(condition==cond, batch==bt, trial==tid)
      tested = hazdata(testing, trained$par)
      
      # Save
      rr_fits = rbind(rr_fits, data.frame(model='RR',condition=cond,batch=bt,
                                          trial=tid,nll=sum(tested$ll)))
      df.rr = rbind(df.rr, tested %>% select(condition,batch,trial,
                                             prediction,prob,fitted=transformed,n))
    }
  }
}
fits_all = rbind(fits_all, rr_fits)
fits_all %>% group_by(model) %>% summarise(sum(nll))


## Mix model
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
ag_mix = get_mix_data('ag', 2000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

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
  
  cur_batch=data$batch[1]
  if (cur_batch=='A') {
    data$prob = data$fprob
  } else {
    data$prob = data$fprob*forward_weight+data$bprob*backward_weight
  }
  data$transformed = sigmoid(haz_par)/NCHUNK+(1-sigmoid(haz_par))*data$prob
  data$ll = log(data$transformed)*data$n
  
  return(data)
}

agr_fits = fits_init
df.agr = df_init
for (cond in conditions) {
  for (bt in c('A','B')) {
    for (tid in seq(8)) {
      
      # Held-out one trial
      training = ag_mix %>% filter(condition==cond, batch==bt, trial!=tid)
      trained = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=training)
      
      testing = ag_mix %>% filter(condition==cond, batch==bt, trial==tid)
      tested = hazmixdata(c(trained$par[1],trained$par[2]), testing)
      
      # Save
      agr_fits = rbind(agr_fits, data.frame(model='AGR',condition=cond,batch=bt,
                                          trial=tid,nll=sum(tested$ll)))
      df.agr = rbind(df.agr, tested %>% select(condition,batch,trial,
                                             prediction,prob,fitted=transformed,n))
    }
  }
}
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
  for (bt in c('A','B')) {
    for (tid in seq(8)) {
      
      # Held-out one trial
      training = rr_mix %>% filter(condition==cond, batch==bt, trial!=tid)
      trained = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=training)
      
      testing = rr_mix %>% filter(condition==cond, batch==bt, trial==tid)
      tested = hazmixdata(c(trained$par[1],trained$par[2]), testing)
      
      # Save
      rrr_fits = rbind(rrr_fits, data.frame(model='RRR',condition=cond,batch=bt,
                                            trial=tid,nll=sum(tested$ll)))
      df.rrr = rbind(df.rrr, tested %>% select(condition,batch,trial,
                                               prediction,prob,fitted=transformed,n))
    }
  }
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

















