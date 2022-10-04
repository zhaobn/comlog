
library(tidyverse)

df.tw = read.csv('../data/osf/trials.csv')

model_data = read_csv('../data/osf/models.csv')
model_data_long = model_data %>%
  select(condition, phase, trial, prediction, n, starts_with('fitted_')) %>%
  gather('model', 'prob', -c(condition, phase, trial, prediction, n)) %>%
  mutate(model=substr(model, 8, nchar(model)), lp=log(prob))
rand_data = model_data_long %>%
  filter(model=='ag') %>%
  mutate(model='random', prob=1/17, lp=log(1/17))
model_data_long = rbind(model_data_long, rand_data)

#### Individual fits ####
ppts = df.tw %>% 
  pull(ix) %>%
  unique()

model_list = model_data_long %>%
  pull(model) %>%
  unique()

bic_ppt = function(pid) {
  ppt_data = df.tw %>% filter(ix==pid) %>% select(condition, phase, trial, prediction)
  ppt_cond = ppt_data$condition[1]
  n=nrow(ppt_data)
  
  model_bics = c()
  for (m in model_list) {
    m_data = model_data_long %>%
      filter(model==m, condition==ppt_cond) %>%
      right_join(ppt_data, by=c('condition', 'phase', 'trial', 'prediction'))
    nll=sum(m_data$lp)
    k=if (m %in% c('sim', 'gp')) 4 else if (m=='random') 0 else 1
    bic=k*log(n)-2*nll
    
    model_bics=c(model_bics, bic)
  }
  
  return(data.frame(ix=pid, model=model_list, bic=model_bics))
}

ind_fit = read.csv(text='ix,model,bic')
for (pt in ppts) {
  ind_fit = rbind(ind_fit, bic_ppt(pt))
}

# Pick best-fitting model for each participant
best_models = ind_fit %>% 
  group_by(ix) %>%
  summarise(bestModel=model[which.min(bic)])
  
# Which model wins the most number of participant
bm_stats = best_models %>% 
  count(bestModel) %>% 
  select(model=bestModel, ind=n)
  


#### Match / Hits ####
# Pick people's first choices
ppt_fc = model_data %>%
  select(condition, phase, trial, prediction, n) %>%
  group_by(condition, phase, trial) %>%
  summarise(choice=prediction[which.max(n)])

# Each model's first choices
md_fc = model_data_long %>%
  group_by(condition, phase, trial, model) %>%
  summarise(choice=prediction[which.max(prob)])


# How many matches?
match=c()
for (m in model_list) {
  m_data= md_fc %>% 
    filter(model==m) %>% 
    rename(m_choice=choice) %>%
    left_join(ppt_fc, by=c('condition', 'phase', 'trial')) %>%
    mutate(is_match=choice==m_choice)
  match=c(match, sum(m_data$is_match))
}
match_stats=data.frame(model=model_list, match=match, total=nrow(ppt_fc)) %>%
  mutate(perc=round(100*match/total, 2)) %>%
  rename(total_trials=total)


#### LL improve over random ####
model_lls = model_data %>%
  rename(fitted_random=rand) %>%
  select(condition, phase, trial, prediction, n, starts_with('fitted_')) %>%
  gather('model', 'prob', -c(condition, phase, trial, prediction, n)) %>%
  mutate(model=substr(model, 8, nchar(model)), lp=log(prob)) %>%
  group_by(model, condition) %>%
  summarise(nll=round(sum(lp*n)))
model_stats = model_lls %>%
  left_join(rand_baseline, by='condition') %>%
  mutate(improv=round(nll-rand_nll)) %>%
  select(model, condition, nll) %>%
  spread(condition, nll) %>%
  mutate(total=combine+construct+decon+flip) %>%
  arrange(-total)

rand_base = model_stats[model_stats$model=='random','total']
model_stats$delta=model_stats$total-rand_base[[1]]

model_stats = model_stats %>%
  left_join(bm_stats, by='model') %>%
  left_join(match_stats, by='model')

write_csv(model_stats, file='../data/model_stats.csv')









