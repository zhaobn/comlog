
library(tidyverse)

##### Check data and export to csv ##### 

load('../data/all_cleaned.Rdata')
load('../data/all_coded.Rdata')


# Drop when done: fix label data #
load('../data/raw/exp_1_raw.Rdata')
lb1 = df.sw %>% 
  mutate(exp_id = 1, 
         condition=case_when(
           condition=='comp_mult' ~ 'construct',
          condition=='comp_const' ~ 'combine',
          condition=='comp_mult_reverse' ~ 'decon'
         )) %>%
  select(exp_id, ix, condition, input_a=task.input.a_input, input_b=task.input.b_input)

load('../data/raw/exp_2_raw.Rdata')
lb2 = df.sw %>% 
  mutate(exp_id = 2, 
         condition=case_when(
           condition=='comp_mult' ~ 'construct',
           condition=='comp_const' ~ 'combine',
           condition=='comp_mult_reverse' ~ 'decon'
         )) %>%
  select(exp_id, ix, condition, input_a=task.input.a_input, input_b=task.input.b_input)


load('../data/raw/exp_3_raw.Rdata')
lb3 = df.sw %>% 
  mutate(exp_id = 3, 
         condition=case_when(
           condition=='mult' ~ 'combine',
           condition=='sub' ~ 'flip',
         )) %>%
  select(exp_id, ix, condition, input_a=task.input.a_input, input_b=task.input.b_input)

load('../data/raw/exp_4_raw.Rdata')
lb4 = df.sw %>% 
  mutate(exp_id = 4, 
         condition=case_when(
           condition=='mult' ~ 'combine',
           condition=='sub' ~ 'flip',
         )) %>%
  select(exp_id, ix, condition, input_a=task.input.a_input, input_b=task.input.b_input)



# Subject data + labels
subj = df.sw %>% 
  select(exp_id, ix, condition, task_duration, age, sex)
labl = labels %>%
  mutate(exp_id=as.numeric(substr(exp, 5, nchar(exp))), ix=as.numeric(ix)) %>%
  select(exp_id, ix, condition, report_a=input_a, coded_a=rule_cat_a, report_b=input_b, coded_b=rule_cat_b)

subj_export = subj %>%
  left_join(labl, by=c('exp_id', 'ix', 'condition'))
write_csv(subj_export, file='../data/osf/subjects.csv')

# Fix missing input_a
subj = read_csv('../data/osf/subjects.csv')
to_select = colnames(subj)

subj = read_csv('../data/osf/subjects.csv') %>% select(-report_a)
input_a = df.sw %>% select(ix, report_a=input_a)
subj = subj %>%
  left_join(input_a, by='ix') %>%
  select(to_select)
write_csv(subj, file='../data/osf/subjects.csv')

# Trial data
answers = read.csv('../data/tasks/answers.csv') %>% select(-X)
trl = df.tw %>%
  left_join(answers, by=c('exp_id', 'condition', 'trial', 'stripe', 'dot', 'block')) %>%
  mutate(is_groundTruth = as.numeric(prediction==gt)) %>%
  select(exp_id, ix, condition, phase=batch, trial, stripe, dot, segment=block, prediction, is_groundTruth) 
write_csv(trl, file='../data/osf/trials.csv')

# Fitted models
load('../data/fitted_models.Rdata')
load('../data/alter_fitted.Rdata')

by_cols = c('condition', 'batch', 'trial', 'prediction')
mdl = df.ag %>% select(c(by_cols, 'n'))
mdl = mdl %>%
  left_join(select(df.ag, condition, batch, trial, prediction, raw_ag=prob, fitted_ag=fitted), by=by_cols) %>%
  left_join(select(df.agr, condition, batch, trial, prediction, raw_agr=prob, fitted_agr=fitted), by=by_cols) %>%
  left_join(select(df.rr, condition, batch, trial, prediction, raw_rr=prob, fitted_rr=fitted), by=by_cols) %>%
  left_join(select(df.sim, condition, batch, trial, prediction, raw_sim=prob, fitted_sim=fitted), by=by_cols) %>%
  left_join(select(df.gp, condition, batch, trial, prediction, raw_gp=prob, fitted_gp=fitted), by=by_cols) %>%
  left_join(select(df.mm, condition, batch, trial, prediction, raw_mm=prob, fitted_mm=fitted), by=by_cols) %>%
  left_join(select(df.lm, condition, batch, trial, prediction, raw_lm=prob, fitted_lm=fitted), by=by_cols) %>%
  mutate(rand=1/17) %>%
  rename(phase=batch)
write_csv(mdl, file='../data/osf/models.csv')

########## 

##### Stats ##### 

df.sw = read.csv('../data/osf/subjects.csv')
df.tw = read.csv('../data/osf/trials.csv')

# Demographics
df.sw %>% group_by(exp_id) %>%
  summarise(n=n(), sd(age), mean(age), sd(task_duration)/60000, mean(task_duration)/60000)

# Experiments 1 and 2, final accuracy
exp_1and2 = df.tw %>% filter(exp_id < 3, phase == 'B')
exp_1and2 %>%
  group_by(condition, ix) %>%
  summarise(acc=sum(is_groundTruth)/n()) %>%
  group_by(condition) %>%
  summarise(sd(acc), mean(acc))

t.test(
  exp_1and2 %>% filter(condition=='construct') %>% pull(is_groundTruth),
  exp_1and2 %>% filter(condition=='decon') %>% pull(is_groundTruth)
)

# Experiments 1 and 2, final self-reports
labels_1and2 = df.sw %>% 
  filter(exp_id < 3) %>%
  select(ix, condition, coded_a, coded_b)

# Accuracy tests


##########  

##### Plots ##### 

##########  


