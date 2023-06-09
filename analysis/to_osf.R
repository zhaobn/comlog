
library(tidyverse)
library(ggplot2)
library(ggpubr)
library(ggridges)

##### Check data and export to csv ##### 

load('../data/all_cleaned.Rdata')
load('../data/all_coded.Rdata')

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


##### Stats all ##### 

df.sw = read.csv('../data/osf/subjects.csv')
df.tw = read.csv('../data/osf/trials.csv')

# Demographics
df.sw %>% group_by(exp_id) %>%
  summarise(n=n(), sd(age), mean(age), sd(task_duration)/60000, mean(task_duration)/60000)

##### Experiments 1 and 2 generalization accuracy ##### 

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

t.test(
  exp_1and2 %>% filter(condition=='construct') %>% pull(is_groundTruth),
  exp_1and2 %>% filter(condition=='combine') %>% pull(is_groundTruth)
)


##### Experiments 1 and 2 coded self-reports ##### 

labels_1and2 = df.sw %>% 
  filter(exp_id < 3) %>%
  select(ix, condition, coded_a, coded_b) %>%
  gather('phase', 'coded', -c(ix, condition)) %>%
  mutate(phase=toupper(substr(phase, 7,8))) %>%
  count(condition, phase, coded)

# Add percentage
labels_total_1and2 = labels_1and2 %>%
  group_by(condition, phase) %>%
  summarise(total=sum(n))
labels_1and2 = labels_1and2 %>%
  left_join(labels_total_1and2, by=c('condition', 'phase')) %>%
  mutate(perc=n/total)

# Plot to see all percentage  
ggplot(labels_1and2, aes(x=phase, y=perc, fill=coded)) +
  geom_bar(position="fill", stat='identity') +
  facet_grid(~condition) +
  geom_text(aes(x=phase, label=paste0(round(perc*100,2),'%')), position = position_stack(vjust = 0.5)) +
  facet_grid(~condition)

# For tests reported in paper
label_checks_1and2 = df.sw %>% 
  filter(exp_id < 3) %>%
  mutate(is_gt = coded_b=='ground_truth',
         is_complex = coded_b=='complex',
         is_mult = ifelse(condition=='decon', coded_b=='mult', coded_a=='mult'))

# Phase II ground truth, construct vs. de-construct
t.test(
  label_checks_1and2 %>% filter(condition=='construct') %>% pull(is_gt),
  label_checks_1and2 %>% filter(condition=='decon') %>% pull(is_gt)
)

# Phase II complex guesses, construct vs. de-construct
t.test(
  label_checks_1and2 %>% filter(condition=='construct') %>% pull(is_complex),
  label_checks_1and2 %>% filter(condition=='decon') %>% pull(is_complex)
)

# Phase II complex guesses, combine vs. de-construct
t.test(
  label_checks_1and2 %>% filter(condition=='combine') %>% pull(is_complex),
  label_checks_1and2 %>% filter(condition=='decon') %>% pull(is_complex)
)

# Decon Phase I mult vs. construct Phase II mult
t.test(
  label_checks_1and2 %>% filter(condition=='construct') %>% pull(is_mult),
  label_checks_1and2 %>% filter(condition=='decon') %>% pull(is_mult)
)

# Decon Phase I mult vs. combine Phase II mult
t.test(
  label_checks_1and2 %>% filter(condition=='combine') %>% pull(is_mult),
  label_checks_1and2 %>% filter(condition=='decon') %>% pull(is_mult)
)

## Phase 1 self-report length
ph1_guess_length_1and2 = df.sw %>%
  filter(exp_id < 3) %>%
  select(ix, condition, report_a) %>%
  mutate(len_a=nchar(report_a))

ph1_guess_length_1and2 %>%
  group_by(condition) %>%
  summarise(mean=mean(len_a), sd=sd(len_a))

t.test(
  ph1_guess_length_1and2 %>% filter(condition=='construct') %>% pull(len_a),
  ph1_guess_length_1and2 %>% filter(condition=='decon') %>% pull(len_a)
)



##### Experiments 3 and 4 ##### 

## Generalization accuracy (match to ground truth)
exp_3and4 = df.tw %>% filter(exp_id > 2, phase == 'B')
exp_3and4 %>%
  group_by(condition, ix) %>%
  summarise(acc=sum(is_groundTruth)/n()) %>%
  group_by(condition) %>%
  summarise(sd(acc), mean(acc))

t.test(
  exp_3and4 %>% filter(condition=='combine') %>% pull(is_groundTruth),
  exp_3and4 %>% filter(condition=='flip') %>% pull(is_groundTruth)
)

## Self-reports
labels_3and4 = df.sw %>% 
  filter(exp_id > 2) %>%
  mutate(is_gt=coded_b=='ground_truth')

labels_3and4 %>%
  group_by(condition) %>%
  summarise(is_gt=sum(is_gt), n=n()) %>%
  mutate(perc=round(100*is_gt/n, 2))

t.test(
  labels_3and4 %>% filter(condition=='combine') %>% pull(is_gt),
  labels_3and4 %>% filter(condition=='flip') %>% pull(is_gt)
)

## Compare alternative with ground truth

# Compute alternative answer
alt_exp3and4 = df.tw %>%
  filter(exp_id>2) %>%
  mutate(alt_answer=ifelse(exp_id==3, stripe*(segment-dot), dot*(segment-stripe))) %>%
  mutate(alt_answer=ifelse(alt_answer<0, 0, alt_answer)) %>%
  mutate(is_alt=as.numeric(prediction==alt_answer))

alt_exp3and4 %>%
  filter(phase=='B', condition=='flip') %>%
  group_by(condition, ix) %>%
  summarise(alt_acc=sum(is_alt)/n(), gt_acc=sum(is_groundTruth)/n()) %>%
  group_by(condition) %>%
  summarise(sd(alt_acc), mean(alt_acc), sd(gt_acc), mean(gt_acc))


labels_3and4 %>%
  count(coded_b) %>%
  mutate(perc=round(100*n/nrow(labels_3and4),2))

chisq.test(c(1, 13, 38), p=rep(1/3, 3))



##### Model plots ##### 

model_data = read_csv('../data/osf/models.csv')

## LL improvement
model_lls = model_data %>%
  select(condition, phase, trial, prediction, n, starts_with('fitted_')) %>%
  gather('model', 'prob', -c(condition, phase, trial, prediction, n)) %>%
  mutate(model=substr(model, 8, nchar(model)), lp=log(prob)) %>%
  group_by(model, condition) %>%
  summarise(nll=sum(lp*n))

# random baseline
rand_baseline = model_data %>%
  group_by(condition) %>%
  summarise(n=sum(n)) %>%
  mutate(rand_nll=n*log(1/17))
model_ll_improv = model_lls %>%
  left_join(rand_baseline, by='condition') %>%
  mutate(improv=round(nll-rand_nll))

# plot
model_ll_improv %>%
  mutate(condition=ifelse(condition=='decon', 'de-construct', condition)) %>%
  mutate(condition=factor(condition, levels=c("construct", 'de-construct', 'combine', 'flip'))) %>%
  ggplot(aes(x=reorder(model, -nll), y=improv, fill=condition)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(
    aes(label = paste0('+', after_stat(y)), group = model), 
    stat = 'summary', fun = sum, vjust = -1
  ) +
  theme_bw() +
  labs(x='', y='') +
  scale_fill_brewer(palette="Blues", direction=-1) +
  theme(legend.title=element_blank(),
        legend.position=c(.75,.9),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 20),
        axis.text.x = element_text(angle = 45, vjust = 0.5, hjust=.5))


## Accuracy fits
answers = df.tw %>%
  filter(exp_id%%2==1) %>%
  select(condition, phase, trial, stripe, dot, segment) %>%
  unique() %>%
  mutate(groundTruth=stripe*segment-dot) %>%
  mutate(groundTruth=ifelse(groundTruth<0, 0, groundTruth))
all_answers = expand.grid(
    condition=c('construct', 'decon', 'combine', 'flip'),
    phase=c('A', 'B'),
    trial=seq(8),
    prediction=seq(0,16), stringsAsFactors = FALSE) %>%
  arrange(condition, phase, trial, prediction) %>%
  left_join(answers, by=c('condition', 'phase', 'trial')) %>%
  mutate(is_groundTruth=as.numeric(prediction==groundTruth)) %>%
  select(-groundTruth)


model_accs = model_data %>%
  select(condition, phase, trial, prediction, n, starts_with('fitted_')) %>%
  gather('model', 'prob', -c(condition, phase, trial, prediction, n)) %>%
  mutate(model=substr(model, 8, nchar(model))) %>%
  left_join(all_answers, by=c('condition', 'phase', 'trial', 'prediction')) %>%
  group_by(model, phase, condition) %>%
  summarise(acc=sum(prob*is_groundTruth)/8, ppt_acc=sum(n*is_groundTruth)/sum(n))

ggplot(model_accs, aes(x=acc, y=ppt_acc)) +
  geom_point() +
  geom_smooth(method='lm', formula= y~x, fill = "lightgray") +
  stat_cor(aes(label = ..r.label..), label.x = .09, label.y = .54) + # x 36
  facet_wrap(~model, nrow=1) +
  labs(x='model', y='people') +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position=c(.07,.87),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 20))


## Detailed accuracy fits
ppt_stats = df.tw %>%
  group_by(condition, phase) %>%
  summarise(se=sd(is_groundTruth)/sqrt(n()), ppt_acc=sum(is_groundTruth)/n())

bayesian_models = model_accs %>%
  filter(model %in% c('ag', 'agr', 'rr'))

ggplot(ppt_stats, aes(x=phase, y=ppt_acc)) +
  geom_bar(stat='identity', fill='black') +
  geom_errorbar(aes(ymin=ppt_acc-se, ymax=ppt_acc+se), width=.2, color='#116466')+
  geom_point(
    data=bayesian_models,
    aes(x=phase, y=acc, shape=model, color=model), 
    position = position_jitterdodge(jitter.width = 0.5, jitter.height = 0.05, dodge.width = 0.05),
    size=5, stroke=1.5) +
  scale_shape_manual(values=c(16, 17, 15)) +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5")) +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x*100, '%')) +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position = 'right',
        #legend.position=c(.9,.9),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 25)) +
  facet_grid(~condition)


##### Rainbow plot ####
cond_levels = c('construct', 'decon', 'combine', 'flip')

answers_t = all_answers %>%
  filter(is_groundTruth==1) %>%
  mutate(trial=as.factor(as.character(trial)),
         condition=factor(condition, levels=cond_levels),
         phase=ifelse(phase=='A','I','II')) %>%
  select(condition, phase, trial, prediction)

df.agr = model_data %>%
  select(condition, phase, trial, prediction, n, fitted_agr) %>%
  mutate(
    trial=as.factor(as.character(trial)),
    condition=factor(condition, level=cond_levels),
    phase=ifelse(phase=='A','I','II')
  )

df.tw %>%
  mutate(
    trial=as.factor(as.character(trial)),
    condition=factor(condition, level=cond_levels),
    phase=ifelse(phase=='A','I','II')
  ) %>%
  ggplot(aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6, stat="binline", bins=20, scale=0.95) +
  geom_point(data=answers_t) +
  geom_density_ridges(data=df.agr, aes(height=fitted_agr), stat="identity", alpha=0.4, scale=0.95) +
  #geom_density_ridges(data=df.gpr, aes(height=prob), stat="identity", alpha=0.4, scale=0.95) +
  #scale_x_discrete(limits=c(0,seq(max(df.agr$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(phase~condition) +
  theme_bw() +
  labs(x='result segment prediction', y='generalization task') +
  theme(
    legend.position = 'none',
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
  )


##### Update new labels ##### 
subjects_data = read.csv('../data/osf/subjects.csv')
load('../data/responses/recoded.Rda')

r_labels = df.labels %>% select(ix, a_code, b_code)
subjects_data_copy = subjects_data %>%
  select(exp_id, ix, condition, task_duration, age, sex, report_a, report_b) %>%
  left_join(r_labels, by='ix') %>%
  select(exp_id, ix, condition, task_duration, age, sex, report_a, coded_a=a_code, report_b, coded_b=b_code)
write_csv(subjects_data_copy, '../data/osf/subjects.csv')


# Rename code
subjects_data = subjects_data %>%
  mutate(coded_a=ifelse(coded_a=='gt', 'ground_truth', coded_a), 
         coded_b=ifelse(coded_b=='gt', 'ground_truth', coded_b))
write_csv(subjects_data, '../data/osf/subjects.csv')




