
#### Packages, data, core funcs ########
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)



runs = seq(0, 40)
depths = c('d2', 'allframes')
iters = c(seq(10), 2**seq(4,10))
conditions = c('construct','combine','decon','flip')
batches = c('a','b')




load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(condition, batch, trial, prediction)

sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  # data$fitted = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  return(data)
}
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}


get_filepath = function(run, depth, iter, cond, batch) {
  return(paste0('sims/run_', run, '/data_', depth, '/process_', iter, '/', cond, '_preds_', batch, '.csv'))
}
get_pred = function(run, depth, iter) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(file=get_filepath(run, depth, iter, cond, batch))
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


#### Fits ########
fit_pred = function(run, depth, iter) {
  # Get data
  model_data = get_pred(run, depth, iter)
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  
  # Return
  model_depth = if (depth=='d2') 2 else 1
  return (list(run=run, iter=iter, depth=model_depth, fit=out$value, param=out$par))
}


fits = read.csv(text='run,iter,depth,fit,param')
for (r in runs) {
  for (i in iters) {
    for (d in depths) {
      fits = rbind(fits, fit_pred(r, d, i))
      write.csv(fits, file='fits.csv')
    }
  }
}



#### Cross validation ####
cross_fit = function(run, depth, iter, cond) {
  # Get data
  model_data = get_pred(run, depth, iter)
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  training_set = model_ppt[!(model_ppt$condition==cond),]
  test_set = model_ppt[model_ppt$condition==cond,]
  
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training_set)
  fitted = hazdata(test_set, out$par)
  
  
  # Return
  model_depth = if (depth=='d2') 2 else 1
  return (list(run=run, iter=iter, depth=model_depth, condition=cond, cfit=sum(fitted$ll)))
}

crossv = read.csv(text='run,iter,depth,condition,cfit')
for (r in runs) {
  for (i in iters) {
    for (d in depths) {
      for (c in conditions) {
        crossv = rbind(crossv, data.frame(cross_fit(r, d, i, c)))
        write.csv(crossv, file = 'cross_fit.csv')
      }
    }
  }
}



#### Revisit model ####
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
cross_fit_mix = function(run, depth, iter, cond) {
  # Get data
  forward_data = get_pred(run, depth, iter)
  setups = list(
    list(cond = 'construct', rj_cond = 'decon'),
    list(cond = 'decon', rj_cond = 'construct'),
    list(cond = 'combine', rj_cond = 'flip'),
    list(cond = 'flip', rj_cond = 'combine')
  ) 
  mix_data = read.csv(text='condition,batch,trial,prediction,fprob,bprob')
  for (pair in setups) {
    fdata = forward_data %>% filter(condition==pair['cond']) %>% rename(fprob=prob)
    bdata = forward_data %>% filter(condition==pair['rj_cond']) %>% rename(bprob=prob) %>% select(batch,trial,prediction,bprob)
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
  model_depth = if (depth=='d2') 2 else 1
  return((list(run=run, iter=iter, depth=model_depth, condition=cond, cfit=sum(tested$ll))))
  
}


crossv_results = read.csv(text='run,iter,depth,condition,cfit')
for (r in runs) {
  for (i in iters) {
    for (d in depths) {
      for (c in conditions) {
        crossv_results = rbind(crossv_results, data.frame(cross_fit_mix(r, d, i, c)))
        write.csv(crossv_results, file = 'cross_fit_mix.csv')
      }
    }
  }
}



#### Plots ####

# All fits
fits = read.csv('../data/param_fits.csv') %>% select(-X)
fits_agg = fits %>%
  group_by(iter, depth) %>%
  summarise(mean=mean(fit), sd=sd(fit)) %>%
  mutate(depth=factor(depth, levels=c(1, 2)))

ggplot(fits_agg, aes(x=iter, y=mean, group=depth, color=depth)) +
  geom_line(size=1) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd))+
  geom_point(aes(shape=depth), size=3) +
  ylim(20000, 22500) +
  scale_x_continuous(trans='log2') +
  scale_color_manual(values=c("#009E73", "#999999")) +
  theme_bw() +
  labs(y='Negative log-likelihood', x='Number of Gibbs interation (log scale)')


# Cross fits
rand_base = read.csv('params/random_base.csv') %>% select(-X) %>% rename(rand=ll)
sims = read.csv('../data/cross_fits.csv') %>% select(-X) %>% mutate(type='AG')
mixs = read.csv('../data/cross_fit_mix.csv') %>% select(-X) %>% mutate(type='AGR')

fits = rbind(sims, mixs) %>%
  select(type, run, iter, depth, condition, cfit) %>%
  left_join(rand_base, by='condition')%>%
  mutate(improv = cfit - rand, model=paste0(type,'-d',depth))




# Overall plot
library(wesanderson)
p_runs = fits %>% 
  group_by(model, iter, run) %>%
  summarise(improv=sum(improv)) %>%
  group_by(model, iter) %>%
  summarise(mean=mean(improv), sd=sd(improv)) %>%
  mutate(model=factor(model, levels=c('AG-d1', 'AGR-d1', 'AG-d2', 'AGR-d2'))) %>%
  ggplot(aes(x=iter, y=mean, group=model, color=model)) +
  geom_line(size=1) +
  geom_point(aes(shape=model), size=3) +
  #geom_ribbon(aes(ymin = mean-sd, ymax = mean+sd), alpha = 0.1) +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd))+
  scale_x_continuous(trans='log2') +
  #ylim(0,6500) +
  theme_bw() +
  labs(y='Model fits (improv. over baseline)', x='Number of Gibbs interation (log scale)') +
  scale_color_manual(values=wes_palette(n=4, name="Zissou1"))


# # Look at per condition at last run
# fits %>%
#   group_by(model, iter, condition) %>%
#   summarise(mean=mean(improv), sd=sd(improv)) %>%
#   mutate(model=factor(model, levels=c('AG-d1', 'AGR-d1', 'AG-d2', 'AGR-d2'))) %>%
#   ggplot(aes(x=iter, y=mean, group=model, color=model)) +
#   geom_line(size=1) +
#   #geom_ribbon(aes(ymin = mean-sd, ymax = mean+sd), alpha = 0.1) +
#   geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd))+
#   geom_point(aes(shape=model), size=3) +
#   scale_x_continuous(trans='log2') +
#   #ylim(0,6500) +
#   theme_bw() +
#   labs(y='Model fits (improv. over baseline)', x='Number of Gibbs interation (log scale)') +
#   scale_color_manual(values=wes_palette(n=4, name="Zissou1"))+
#   facet_grid(~condition)


p_conds = fits %>%
  filter(iter==1024) %>%
  group_by(model, condition) %>%
  summarise(mean=mean(improv), sd=sd(improv)) %>%
  mutate(model=factor(model, levels=c('AG-d1', 'AGR-d1', 'AG-d2', 'AGR-d2')),
         condition=factor(condition, 
                          levels=c('construct', 'decon', 'combine', 'flip'), 
                          labels=c('construct', 'de-construct', 'combine', 'flip'))) %>%
  ggplot(aes(x=condition, y=mean, fill=model)) +
  geom_bar(position=position_dodge(), stat = 'identity') +
  geom_errorbar(aes(ymin=mean-sd, ymax=mean+sd), position=position_dodge(.9), width=.2)+
  scale_fill_manual(values=wes_palette(n=4, name="Zissou1"))+
  labs(y='Model fits (improv. over baseline)') +
  theme_bw()

ggarrange(p_runs, p_conds, ncol=2, common.legend = TRUE, legend="right", widths=c(.6,.4))




##### Compare with mix run ####
get_filepath = function(cond, batch) {
  return(paste0('../data/sims/data_mix/', cond, '_preds_', batch, '.csv'))
}

# Get model data
model_data = read.csv(text='condition,batch,trial,prediction,prob')
for (cond in conditions) {
  for (batch in batches) {
    model_raw=read.csv(file=get_filepath(cond, batch))
    model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
    model_data = rbind(model_data, model_raw)
  }
}

model_ppt=model_data %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)

cross_fit = function(cond) {
  # Fit
  training_set = model_ppt[!(model_ppt$condition==cond),]
  test_set = model_ppt[model_ppt$condition==cond,]
  
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training_set)
  fitted = hazdata(test_set, out$par)
  
  # Return
  model_depth = 'dist'
  return (list(type='AG', run=1, iter=1024, depth=model_depth, condition=cond, cfit=sum(fitted$ll)))
}


cross_fit_mix = function(cond) {
  # Get data
  setups = list(
    list(cond = 'construct', rj_cond = 'decon'),
    list(cond = 'decon', rj_cond = 'construct'),
    list(cond = 'combine', rj_cond = 'flip'),
    list(cond = 'flip', rj_cond = 'combine')
  ) 
  mix_data = read.csv(text='condition,batch,trial,prediction,fprob,bprob')
  for (pair in setups) {
    fdata = model_data %>% filter(condition==pair['cond']) %>% rename(fprob=prob)
    bdata = model_data %>% filter(condition==pair['rj_cond']) %>% rename(bprob=prob) %>% select(batch,trial,prediction,bprob)
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
  model_depth = 'dist'
  return((list(type='AGR', run=1, iter=1024, depth=model_depth, condition=cond, cfit=sum(tested$ll))))
  
}



dist_results = read.csv(text='type,run,iter,depth,condition,cfit')
for (c in conditions) {
  dist_results = rbind(dist_results, data.frame(cross_fit(c)))
  dist_results = rbind(dist_results, data.frame(cross_fit_mix(c)))
}

# quick comparison
dist_results = dist_results %>% mutate(type=ifelse(type=='D', 'AG', 'AGR'))

dist_results_extended = dist_results %>% 
  left_join(rand_base, by='condition') %>%
  mutate(improv = cfit-rand, model=paste0(type,'-geo')) %>%
  select(type, run, iter, depth, condition, cfit, rand, improv, model)

prev_fits = fits %>% filter(iter==1024, run==1)
to_compare = rbind(prev_fits, dist_results_extended)

x = to_compare %>%
  group_by(condition, model) %>%
  summarise(improv=sum(improv)) %>%
  arrange(condition, desc(improv))
  
to_compare %>%
  group_by(model) %>%
  summarise(improv=sum(improv)) %>%
  arrange(desc(improv))

