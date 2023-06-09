
library(dplyr)
library(tidyr)
library(ggplot2)

load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(condition, batch, trial, prediction)


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

conditions = c('construct','combine','decon','flip')
batches = c('a','b')
#runs = c('', '_allframes', '_d2')
local_path_prefix = '../python' # '' for server


#### Gather all data #### 
sim_data = read.csv(text='run,iter,condition,batch,trial,prediction,prob')
for (r in c('', '_allframes', '_d2')) {
  iters = c(seq(10),2**seq(4,10))
  if (r == '_allframes') iters = iters[1:length(iters)-1]
  
  for (i in iters) {
    for (cond in conditions) {
      for (batch in batches) {
        sim_raw=read.csv(paste0(local_path_prefix, '/sims/data',r,'/process_',i,'/',cond,'_preds_',tolower(batch),'.csv'))
        sim_raw = sim_raw %>%
          select(term=terms, starts_with('prob')) %>%
          gather('trial', 'prob', -term) %>%
          mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
                 prediction=term, condition=cond, batch=toupper(batch),run=r,iter=i) %>%
          select(run,iter,condition, batch, trial, prediction, prob)
        
        sim_data = rbind(sim_data, sim_raw)
      }
    }
  }
}
save(sim_data, file='../data/revision/all_sim.Rdata')



#### Overall fits #### 
fit_pred = function(run_name, iter) {
  # Get data
  model_data = sim_data[(sim_data$run==run_name&sim_data$iter==iter),]
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  model_name = run_name
  if (nchar(model_name) < 1) {
    model_name = 'd1'
  } else {
    model_name = substr(model_name, 2, nchar(model_name))
  }
  
  # Return
  return (list(run=toupper(model_name), iter=iter, fit=out$value, param=out$par))
}



# fit_results = read.csv(text='run,iter,fit,param')
# fit_results = read.csv('params/fit_results.csv') %>% select(-X)

iters = c(seq(10),2**seq(4,10),seq(11,15)*100, seq(20, 50, 5)*100)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('',i)))
}


iters = c(1,3,5,6,7,9,10) #2**seq(9)
fit_results = read.csv('params/fit_results.csv') %>% select(-X)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('_allframes',i)))
}


iters = 2**seq(4,10) #seq(10)
fit_results = read.csv('params/fit_results.csv') %>% select(-X)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('_d2',i)))
}

fit_results = fit_results %>% arrange(run, iter)
write.csv(fit_results, 'params/fit_results.csv')




#### Cross validation #### 
cross_fit = function(run_name, iter, cond_name) {
  # Get data
  model_data = sim_data[(sim_data$run==run_name&sim_data$iter==iter),]
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  training_set = model_ppt[!(model_ppt$condition==cond_name),]
  test_set = model_ppt[model_ppt$condition==cond_name,]
  
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training_set)
  fitted = hazdata(test_set, out$par)
  
  model_name = run_name
  if (nchar(model_name) < 1) {
    model_name = 'd1'
  } else {
    model_name = substr(model_name, 2, nchar(model_name))
  }
  
  # Return
  return (list(run=toupper(model_name), iter=iter, condition=cond_name, cfit=sum(fitted$ll)))
}


crossv_results = read.csv(text='run,iter,condition,cfit')
#crossv_results = read.csv('params/cross_results.csv') %>% select(-X)

configs = sim_data %>% select(run, iter) %>% unique()
for (i in 1:nrow(configs)) {
  r = configs[i,'run']
  iter = configs[i,'iter']
  for (c in conditions) {
    crossv_results = rbind(crossv_results,data.frame(cross_fit(r, iter, c)))
  }
}
write.csv(crossv_results, file = 'params/cross_results.csv')



#### AGR model ####
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
cross_fit_mix = function(run, iter, cond) {
  # Get data
  forward_data = sim_data[(sim_data$run==run&sim_data$iter==iter),]
  setups = list(
    list(cond = 'construct', rj_cond = 'decon'),
    list(cond = 'decon', rj_cond = 'construct'),
    list(cond = 'combine', rj_cond = 'flip'),
    list(cond = 'flip', rj_cond = 'combine')
  ) 
  mix_data = read.csv(text='run,iter,condition,batch,trial,prediction,fprob,bprob')
  for (pair in setups) {
    fdata = forward_data %>% filter(condition==pair['cond']) %>% rename(fprob=prob)
    bdata = forward_data %>% filter(condition==pair['rj_cond']) %>% rename(bprob=prob) %>% select(-c(condition,run,iter))
    mdata = fdata %>% left_join(bdata, by=c('batch','trial','prediction'))
    mix_data = rbind(mix_data, mdata)
  }
  mix_data = mix_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
    
  
  # Held-out one trial
  training = mix_data %>% filter(condition!=cond)
  trained = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=training)
  
  testing = mix_data %>% filter(condition==cond)
  tested = hazmixdata(c(trained$par[1],trained$par[2]), testing)
  
  # Save
  model_name = run
  if (nchar(model_name) < 1) {
    model_name = 'd1'
  } else {
    model_name = substr(model_name, 2, nchar(model_name))
  }
  return((list(run=toupper(model_name), iter=iter, condition=cond, cfit=sum(tested$ll))))
  
}


configs = sim_data %>% select(run, iter) %>% unique()
cross_mix = read.csv(text='run,iter,condition.cfit')
for (i in 1:nrow(configs)) {
  r = configs[i,'run']
  iter = configs[i,'iter']
  for (c in conditions) {
    cross_mix = rbind(cross_mix,data.frame(cross_fit_mix(r, iter, c)))
  }
}
write.csv(cross_mix, file = 'params/cross_fit_mix.csv')



#### Random baseline ####
base = sim_data %>%
  filter(run=='', iter==1) %>%
  select(condition, batch, trial, prediction)
base = base %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

base$ll = log(1/17)
rand_base = base %>%
  group_by(condition) %>%
  summarise(ll=sum(ll*n))
write.csv(rand_base, file='params/random_base.csv')



#### Put together and compare ####
rand_base = read.csv('params/random_base.csv') %>% select(-X) %>% rename(rand=ll)

sims = read.csv('params/cross_results.csv') %>% select(-X) %>% mutate(type='ag')
mixs = read.csv('params/cross_fit_mix.csv') %>% select(-X) %>% mutate(type='revisit')

fits = rbind(sims, mixs) %>%
  select(type, run, iter, condition, cfit) %>%
  left_join(rand_base, by='condition') %>%
  mutate(improv = cfit - rand)


# Overall plot
fits_checked = fits %>% 
  filter(run!='D1') %>%
  group_by(type, run, iter) %>%
  summarise(improv=sum(improv)) %>%
  mutate(model=paste0(ifelse(type=='ag','AG','Revisit'),'-',ifelse(run=='D2','d2','d1')))

library(wesanderson)
ggplot(data=fits_checked, aes(x=iter, y=improv, group=model)) +
  geom_line(aes(color=model), size=1.2) +
  scale_x_continuous(trans='log2') +
  geom_hline(yintercept=4495, color = "black", linetype='dashed') +
  theme_bw() +
  scale_color_manual(values=wes_palette(n=4, name="Zissou1"))


# Plot per condition
fits %>%
  filter(run!='D1') %>%
  mutate(model=paste0(ifelse(type=='ag','AG','Revisit'),'-',ifelse(run=='D2','d2','d1')),
         condition=factor(condition, levels=c('construct','decon','combine', 'flip'))) %>%
  ggplot(aes(x=iter, y=improv, group=model)) +
  geom_line(aes(color=model), size=1.1) +
  scale_x_continuous(trans='log2') +
  facet_wrap(~condition) +
  theme_bw() +
  scale_color_manual(values=wes_palette(n=4, name="Zissou1")) +
  theme(legend.position = 'bottom')





























