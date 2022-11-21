
library(dplyr)
library(tidyr)

setwd("~/bramleylab/comlog/analysis")

load('../data/all_cleaned.Rdata')
load('../data/all_coded.Rdata')


#### Demographics #####
df.sw %>% filter(exp_id==2) %>%
  summarise(sd(age), mean(age), sd(task_duration)/60000, mean(task_duration)/60000)

df.sw %>% filter(exp_id==3) %>%
  summarise(sd(age), mean(age), sd(task_duration)/60000, mean(task_duration)/60000)

df.sw %>% filter(exp_id==3) %>%
  count(condition)

df.sw %>% filter(exp_id==4) %>%
  summarise(sd(age), mean(age), sd(task_duration)/60000, mean(task_duration)/60000)

#### Pre-processing #####
## add ground truth (gt) and alternative truths (alt) to data 
answers = read.csv('../data/tasks/answers.csv') %>% select(-X)
df.tw = df.tw %>%
  left_join(select(answers, exp_id, condition, trial, gt, alt), 
            by=c('exp_id', 'condition','trial'))


#### Curriculum-order effects ####
cur_accs = df.tw %>% 
  filter(exp_id<3, condition %in% c('construct', 'decon'), batch=='B') %>%
  mutate(acc=(prediction==gt))

cur_accs %>% 
  group_by(condition) %>%
  summarise(acc=sum(acc), n=n(), acc_perc=round(100*(sum(acc)/n()),2))

cur_accs %>% 
  group_by(condition, ix) %>%
  summarise(acc=sum(acc)/n()) %>%
  group_by(condition) %>%
  summarise(sd(acc))

t.test(
  cur_accs %>% filter(condition=='construct') %>% pull(acc),
  cur_accs %>% filter(condition=='decon') %>% pull(acc)
)

sd(c(cur_accs %>% filter(condition=='construct') %>% pull(acc),
     cur_accs %>% filter(condition=='decon') %>% pull(acc)))

(0.4474299-0.2660256)/0.4779371


cur_labs = labels %>%
  filter(exp %in% c('exp_1', 'exp_2'), condition %in% c('construct', 'decon')) %>%
  mutate(got_gt=(rule_cat_b=='ground_truth')) 

cur_labs %>%
  group_by(condition) %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))


t.test(
  cur_labs %>% filter(condition=='construct') %>% pull(got_gt),
  cur_labs %>% filter(condition=='decon') %>% pull(got_gt)
)

cur_labs %>%
  filter(rule_a=='mult') %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))

# combine vs construct
cur_accs = df.tw %>% 
  filter(exp_id<3, condition %in% c('construct', 'combine'), batch=='B') %>%
  mutate(acc=(prediction==gt))

cur_accs %>% 
  group_by(condition) %>%
  summarise(acc_perc=round(100*(sum(acc)/n()),2))

t.test(
  cur_accs %>% filter(condition=='construct') %>% pull(acc),
  cur_accs %>% filter(condition=='combine') %>% pull(acc)
)

df.tw %>% 
  filter(exp_id<3, condition %in% c('construct', 'combine'), batch=='B') %>%
  mutate(acc=(prediction==gt)) %>%
  group_by(condition, ix) %>%
  summarise(acc=sum(acc)/n()) %>%
  group_by(condition) %>%
  summarise(sd=round(sd(acc), 4), round(sum(acc)/n(), 4))


#### Local construction ####
labels %>%
  filter(condition=='combine') %>%
  count(rule_cat_b) %>%
  mutate(perc=100*n/sum(n))

chisq.test(c(0,7,59),p=rep(1/3, 3))


p1_length = labels %>%
  filter(exp %in% c('exp_1', 'exp_2'), condition %in% c('construct', 'decon')) %>%
  mutate(nchar_a=nchar(input_a), nchar_b=nchar(input_b)) %>%
  select(condition, ix, nchar_a, nchar_b)
  
p1_length %>%
  group_by(condition) %>%
  summarise(sd_a=sd(nchar_a), mean_a=round(sum(nchar_a)/n(),2),
            sd_b=sd(nchar_b), mean_b=round(sum(nchar_b)/n(),2))

t.test(
  p1_length %>% filter(condition=='construct') %>% pull(nchar_a),
  p1_length %>% filter(condition=='decon') %>% pull(nchar_a),
)

t.test(
  p1_length %>% filter(condition=='construct') %>% pull(nchar_b),
  p1_length %>% filter(condition=='decon') %>% pull(nchar_b)
)


#### Compositions ####
# use last two experiments
comp_accs = df.tw %>% 
  filter(exp_id>2, condition %in% c('combine', 'flip'), batch=='B') %>%
  mutate(acc=(prediction==gt))

comp_accs %>% 
  group_by(condition) %>%
  summarise(acc=sum(acc), n=n(), acc_perc=round(100*(sum(acc)/n()),2))

t.test(
  comp_accs %>% filter(condition=='combine') %>% pull(acc),
  comp_accs %>% filter(condition=='flip') %>% pull(acc)
)

# Compare flip with decon
comp_accs = df.tw %>% 
  filter(condition %in% c('decon', 'flip'), batch=='B') %>%
  mutate(acc=(prediction==gt))

comp_accs %>% 
  group_by(condition) %>%
  summarise(acc=sum(acc), n=n(), acc_perc=round(100*(sum(acc)/n()),2))

t.test(
  comp_accs %>% filter(condition=='decon') %>% pull(acc),
  comp_accs %>% filter(condition=='flip') %>% pull(acc)
)




comp_labs = labels %>%
  filter(condition %in% c('combine', 'flip')) %>%
  mutate(got_gt=(rule_cat_b=='ground_truth')) 

comp_labs %>%
  group_by(condition) %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))


t.test(
  comp_labs %>% filter(condition=='combine') %>% pull(got_gt),
  comp_labs %>% filter(condition=='flip') %>% pull(got_gt)
)


cur_labs %>%
  filter(rule_a=='mult') %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))


labels %>%
  filter(condition=='flip') %>%
  count(rule_cat_b) %>%
  mutate(perc=100*n/sum(n))


# Code the rules according to generalization predictions
forms_data = df.tw %>%
  filter(batch=='B') %>%
  group_by(condition, ix) %>%
  summarise(n=n(), gt=sum(prediction==gt), alt=sum(prediction==alt)) %>%
  mutate(is_gt=(gt>6), is_alt=(alt>6))

forms_data %>%
  group_by(condition) %>%
  summarise(n=n(), is_gt=sum(is_gt), is_alt=sum(is_alt), 
            gt_perc=round(100*sum(is_gt)/n(),2), alt_perc=round(100*sum(is_alt)/n(),2))

t.test(
  forms_data %>% filter(condition=='combine') %>% pull(is_gt),
  forms_data %>% filter(condition=='flip') %>% pull(is_gt),
)

#### Garden path ####
labels %>%
  filter(condition=='decon', rule_cat_a=='complex') %>%
  count(rule_cat_b) %>%
  mutate(perc=100*n/sum(n))


labels %>%
  filter(condition=='decon') %>%
  count(rule_cat_b) %>%
  mutate(perc=100*n/sum(n))

labels = labels %>%
  mutate(rule_cat_b=ifelse(rule_cat_b=='comp', 'complex', rule_cat_b))

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='construct') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='combine') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='flip') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

labels %>%
  filter(condition=='decon') %>%
  mutate(is_a_complex=rule_cat_a=='complex') %>%
  summarise(n(), sum(is_a_complex), perc=100*sum(is_a_complex)/n())

labels %>%
  mutate(is_mult=ifelse(condition %in% c('combine', 'construct'), rule_cat_a=='mult', rule_cat_b=='mult')) %>%
  group_by(condition) %>%
  summarise(n(), sum(is_mult), perc=100*sum(is_mult)/n())

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_mult=rule_cat_b=='mult') %>% pull(is_mult),
  labels %>% filter(condition=='construct') %>% mutate(is_mult=rule_cat_a=='mult') %>% pull(is_mult),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_mult=rule_cat_b=='mult') %>% pull(is_mult),
  labels %>% filter(condition=='combine') %>% mutate(is_mult=rule_cat_a=='mult') %>% pull(is_mult),
)

#### GD ####
labels %>%
  filter(condition %in% c('construct', 'combine')) %>%
  mutate(is_add=rule_cat_a=='add_2') %>%
  group_by(condition) %>%
  summarise(n=n(), is_add=sum(is_add), is_add_perc=round(100*sum(is_add)/n(),2))



#### Alternatives ####

df.tw %>%
  filter(exp_id>2, batch=='B') %>%
  mutate(alt_acc=prediction==alt) %>%
  group_by(condition, ix) %>%
  summarise(alt_acc=sum(alt_acc)/n()) %>%
  group_by(condition) %>%
  summarise(sd=sd(alt_acc), mean=sum(alt_acc)/n())


df.tw %>%
  filter(exp_id>2, batch=='B') %>%
  group_by(condition) %>%
  summarise(n()/16)

chisq.test(c(1,9,),p=rep(1/2, 2))

df.tw %>%
  filter(exp_id>2, batch=='B') %>%
  mutate(acc=prediction==gt) %>%
  group_by(condition, ix) %>%
  summarise(acc=sum(acc)/n()) %>%
  group_by(condition) %>%
  summarise(sd=sd(acc), mean=sum(acc)/n())


gt_accs = df.tw %>%
  filter(exp_id>2, batch=='B') %>%
  mutate(acc=prediction==gt)

t.test(
  gt_accs %>% filter(condition=='combine') %>% pull(acc),
  gt_accs %>% filter(condition=='flip') %>% pull(acc)
)



#### Two-way ANOVA ####
df.tw = read_csv('../data/osf/trials.csv')

collapse_1 = df.tw %>% 
  filter(exp_id < 3, phase=='B') %>%
  select(exp_id, condition, is_groundTruth) %>%
  mutate(exp_id=factor(exp_id), condition=factor(condition))

aov(is_groundTruth ~ exp_id + condition, data = collapse_1) %>%
  summary()

aov(is_groundTruth ~ exp_id + condition + exp_id:condition, data = collapse_1) %>%
  summary()

collapse_3 = df.tw %>% 
  filter(exp_id > 2, phase=='B') %>%
  select(exp_id, condition, is_groundTruth) %>%
  mutate(exp_id=factor(exp_id), condition=factor(condition))

aov(is_groundTruth ~ exp_id + condition, data = collapse_3) %>%
  summary()

aov(is_groundTruth ~ exp_id + condition + exp_id:condition, data = collapse_3) %>%
  summary()


#### GPT-3 ####
gpt3_preds = read.csv('../openai/gpt3-predictions.csv')

# translate number words
gpt3_preds = gpt3_preds %>%
  filter(!(prediction %in% c('none','all'))) %>%
  mutate(pred=case_when(
    prediction=='three'~'3',
    prediction=='four'~'4',
    prediction=='six'~'6',
    prediction=='nine'~'9',
    prediction=='one'~'1',
    prediction=='five'~'5',
    prediction=='two'~'2',
    prediction=='seven'~'7',
    prediction=='twelve'~'12',
    prediction=='eight'~'8',
    prediction=='zero'~'0',
  )) %>%
  mutate(pred=as.numeric(pred))

# Get all task and all selections
info = expand.grid(exp_id=seq(4),phase=seq(2),task=seq(8),pred=seq(0,16))
cond_info = answers %>% select(exp_id, condition) %>% unique()
info = info %>% full_join(cond_info, by='exp_id') %>%
  select(exp_id, condition, phase, task, pred) %>%
  arrange(exp_id, condition, phase, task, pred)

gpt3_full = info %>%
  left_join(gpt3_preds, by=c('exp_id','condition','phase','task','pred')) %>%
  select(exp_id, condition, phase, task, pred, prob) %>%
  replace_na(list(prob=0))

# Get residue probs for each task
gpt3_predicted = gpt3_full %>%
  filter(prob > 0) %>%
  group_by(exp_id, condition, phase, task) %>%
  summarise(total_prob=sum(prob), n=n()) %>%
  mutate(residue=1-total_prob, to_spread = 17-n) %>%
  mutate(res_prob=residue/to_spread)

gpt3_ready = gpt3_full %>% filter(prob > 0)
gpt3_rest = gpt3_full %>%
  filter(prob == 0) %>%
  left_join(gpt3_predicted, by=c('exp_id', 'condition', 'phase', 'task')) %>%
  select(exp_id, condition, phase, task, pred, prob=res_prob)
gpt3_filled = rbind(gpt3_ready, gpt3_rest) %>%
  select(exp_id, condition, phase, task, pred, prob) %>%
  arrange(exp_id, condition, phase, task, pred)

# Get NLL
ppt_data = df.tw %>%
  mutate(phase=ifelse(batch=='A',1,2), task=trial, pred=prediction) %>%
  select(exp_id, ix, condition, phase, task, pred) %>%
  group_by(exp_id, condition, phase, task, pred) %>%
  summarise(n=n())
gpt3_nll = gpt3_filled %>%
  left_join(ppt_data, by=c('exp_id', 'condition', 'phase', 'task', 'pred')) %>%
  mutate(n=ifelse(is.na(n), 0, n))

sum(log(gpt3_nll$prob)*gpt3_nll$n) 
log(1/17)*8*2*570









