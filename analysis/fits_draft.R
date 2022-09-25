
library(dplyr)
library(tidyr)
library(ggplot2)
library(nnet) # for multinom

options(scipen=999) 
options(stringsAsFactors = FALSE)
conditions = c('construct','combine','decon','flip')
normalize=function(vec) return(vec/sum(vec))

#### Fit hazard prob ####
model_fits = read.csv(text='model,nll,haz,par')

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

load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% 
  count(exp_id, condition, batch, trial, prediction) %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=sum(n))


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

df.ag = read_model_data('AG', 1000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)
out.ag = optim(par=0, hazfit, method="L-BFGS-B", data=df.ag)
model_fits = rbind(model_fits, data.frame(model='AG',nll=out.ag$value,haz=convert_haz(out.ag$par,2),par=NA))

# haz_var = model_fits %>% filter(model=='AG') %>% pull(haz)
# df.ag$fitted = sigmoid(haz_var)/NCHUNK+(1-sigmoid(haz_var))*df.ag$prob

df.pcfg = read_model_data('PCFG', 100000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)
out.pfcg = optim(par=0, hazfit, method="L-BFGS-B", data=df.pcfg) #0.3711236, 21287.46

# haz_var = model_fits %>% filter(model=='RR') %>% pull(haz)
haz_var=out.pfcg$par
df.pcfg$fitted = sigmoid(haz_var)/NCHUNK+(1-sigmoid(haz_var))*df.pcfg$prob





#### Fit mixing model ####
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
mix_to_fit = get_mix_data('ag', 1000) %>%
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
  
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  #return(-sum(data$ll))
  return(data)
}

out.mix = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=mix_to_fit) # -0.3395867 -0.1669629 20511.96
convert_weight = function(w, r=NA) if (is.na(r)) return(exp(w)/(1+exp(w))) else return(round(exp(w)/(1+exp(w)),r))
model_fits = model_fits %>% filter(model!='AGR')
model_fits = rbind(model_fits, data.frame(model='AGR',nll=out.mix$value,
                                          haz=convert_haz(out.mix$par[1],4),
                                          par=convert_weight(out.mix$par[2],4),n_par=2, BIC=0))


haz_var = model_fits %>% filter(model=='AGR') %>% pull(haz)
par_var = model_fits %>% filter(model=='AGR') %>% pull(par) %>% as.numeric()
df.agr = hazmix(c(par_var, haz_var), mix_to_fit)
df.agr = df.agr %>% select(condition, batch, trial, prediction, prob, fitted=transformed)

## On a next day, it occurs to me I might want a mixing model for pcfgs too
model_fits = read.csv('../data/fits.csv')

mpcfg_to_fix = get_mix_data('pcfg', 10000) %>%
  left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
  mutate(n=ifelse(is.na(n),0, n)) %>%
  arrange(condition, batch, trial, prediction)
out.mpcfg = optim(par=c(0,0), hazmix, method="L-BFGS-B", data=mpcfg_to_fix) # -1.3307018  0.1433789 21612.34
model_fits = model_fits %>% filter(model!='RRR')
model_fits = rbind(model_fits, data.frame(model='RRR',nll=out.mpcfg$value,
                                          haz=convert_haz(out.mpcfg$par[1],4),
                                          par=convert_weight(out.mpcfg$par[2],4),n_par=2, BIC=0))

haz_var = model_fits %>% filter(model=='RRR') %>% pull(haz)
par_var = model_fits %>% filter(model=='RRR') %>% pull(par) %>% as.numeric()
df.pcfgr = hazmix(c(par_var, haz_var), mpcfg_to_fix)
df.pcfgr = df.pcfgr %>% select(condition, batch, trial, prediction, prob, fitted=transformed)

save(df.ag, df.agr, df.pcfg, df.pcfgr, file = '../data/fitted_models.Rdata')


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
  
  return(hazdata(model_ppt, par[['t']]))
  #return(hazfit(model_ppt, par[['t']]))
}


data = expand.grid(condition=conditions, batch=c('A', 'B'),trial=seq(8)) %>% arrange(condition, batch, trial)
# df.sim = get_sim_pred(data, list('a'=.99, 'b'=.81, 'c'=.71, 't'=0.0381))
# df.sim = df.sim %>% select(condition, batch, trial, prediction, prob, fitted=transformed)
sim.out = optim(par=default_param, get_sim_pred, data=data)
model_fits = rbind(model_fits,data.frame(model='similarity',nll=sim.out$value,haz=convert_haz(sim.out$par[4],4),
           par=paste0(round(sim.out$par[1],2),',',round(sim.out$par[2],2),',',round(sim.out$par[3],2))))

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
lm.out = optim(par=0, hazfit, method="L-BFGS-B", data=lm_ppt)
model_fits = rbind(model_fits, data.frame(model='lm',nll=lm.out$value,
                                          haz=convert_haz(lm.out$par,2),par=NA))
# df.lm = hazdata(lm_ppt, 0.0500) %>%
#   select(condition, batch, trial, prediction, prob, fitted=transformed)

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
out.multinom = optim(par=0, hazfit, method="L-BFGS-B", data=multinom_preds)
model_fits = rbind(model_fits, data.frame(model='multinom',nll=out.multinom$value,
                                          haz=convert_haz(out.multinom$par,2),par=NA))
df.mm = hazdata(multinom_preds, 0.0500) %>%
   select(condition, batch, trial, prediction, prob, fitted=transformed)


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
out.gp = optim(par=0, hazfit, method="L-BFGS-B", data=gp_ppt)
model_fits = rbind(model_fits, data.frame(model='gpreg',nll=out.gp$value,
                                          haz=convert_haz(out.gp$par,2),par=NA))
# df.gpr = hazdata(gp_ppt, 0.0300) %>%
#   select(condition, batch, trial, prediction, prob, fitted=transformed)

## Random baseline
model_fits = rbind(model_fits, data.frame(model='baseline',nll=-570*16*log(1/17),haz=NA,par=NA))

save(df.sim, df.gpr, df.lm, df.mm, file='../data/alter_fitted.Rdata')

#### Overall BIC ####
model_fits = model_fits %>%
  mutate(n_par=case_when(model=='AGR'~2,
                         model=='PCFGR'~2,
                         model=='similarity'~4,
                         model=='baseline'~0,
                         TRUE~1)) %>%
  mutate(BIC=n_par*log(570)+2*nll) %>%
  arrange(BIC) %>%
  mutate(model=case_when(model=='PCFG'~'RR',
                         model=='PCFGR'~'RRR',
                         model=='gpreg'~'GpReg',
                         model=='lm'~'LinReg',
                         model=='similarity'~'Similarity',
                         model=='multinom'~'Multinom',
                         model=='baseline'~'Baseline',
                         TRUE ~ model))

## Save
write.csv(model_fits, "../data/fits.csv", row.names=FALSE)


#### Plots #### 

## LL improvement
model_improvs = read.csv("../data/fits.csv") %>%
  filter(model!='Baseline') %>%
  mutate(improv=25838.91-nll)
ggplot(model_improvs, aes(x=reorder(model,-improv),y=improv)) +
  geom_bar(stat='identity', fill='black') +
  geom_text(aes(label = paste0('+',round(improv))), vjust=-.2, size=5) +
  theme_bw() +
  labs(x='', y='LL improv.') +
  theme(text = element_text(size = 20)) 

ggplot(model_improvs, aes(x=reorder(model,-improv),y=improv, fill=improv)) +
  geom_bar(stat='identity') +
  geom_text(aes(label = paste0('+',round(improv))), vjust=-.2, size=5) +
  theme_bw() +
  scale_fill_gradient2(high='dodgerblue4') +
  labs(x='', y='LL improv.') +
  theme(text = element_text(size = 20), legend.position = 'none',
        panel.grid.major = element_blank(), panel.grid.minor = element_blank()) 



#### Get all fitted data #### 
















