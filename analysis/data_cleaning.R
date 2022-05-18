
library(dplyr)
library(googlesheets4)
rm(list=ls())


load('../data/raw/exp_2_raw.rdata')

# Output to googlesheet to bonus participants
# When bonus-ing, select prolific_id column
# When publishing data, remove the prolific_id column
to_sheet = df.sw %>% 
  select(ix, prolific_id, condition, task.input.a_input, task.input.b_input, feedback, correct)
write.csv(to_sheet, file='../data/responses/exp_4_responses.csv')

# Clean up for analysis
df.sw.raw = df.sw
df.tw.raw = df.tw

df.sw = df.sw.raw %>%
  mutate(input_a = task.input.a_input, input_b = task.input.b_input,
         certainty_a = task.input.a_certainty, certainty_b = task.input.b_certainty) %>%
  select(ix, condition, date, time, instructions_duration, task_duration, 
         age, sex, engagement, difficulty,
         input_a, certainty_a, input_b, certainty_b, feedback,
         correct) %>%
  mutate(condition=as.character(condition),
         age=as.numeric(as.character(age)),
         engagement=as.numeric(as.character(engagement)),
         difficulty=as.numeric(as.character(difficulty)),
         certainty_a=as.numeric(as.character(certainty_a)),
         certainty_b=as.numeric(as.character(certainty_b))) %>%
  mutate(condition=case_when(
    condition=='comp_mult' ~ 'construct',
    condition=='comp_const' ~ 'combine',
    condition=='comp_mult_reverse' ~ 'decon',
  ))

# df.sw[144,'age'] = 33
# df.sw[35,'age'] = 31
# df.sw = df.sw %>% mutate(condition='flip') # for the pilot

#### Transform trial data ####
colnames(df.tw.raw)<-c('ix', 'id', 'batch', 'phase', 'trial', 'tid', 'agent', 'color', 'recipient', 'result', 'selection', 'correct')
df.tw = df.tw.raw %>%
  mutate(batch=ifelse(batch=='alice', 'A', 'B')) %>%
  filter(phase=='gen') %>%
  select(ix, batch, trial, tid, agent, recipient, result, selection, correct)

# Add conditions
conditions = df.sw %>% select(ix, condition) 
df.tw = df.tw %>%
  left_join(conditions, by='ix')

# Extract key feature values
trial_data = df.tw %>%
  mutate(exp_trial=trial,
         tid=as.character(tid),
         tid=as.numeric(substr(tid,2, nchar(tid))),
         stripe=as.numeric(substr(agent, 2, 2)),
         dot=as.numeric(substr(agent, 4, 4)),
         block=as.numeric(substr(recipient, 6, 6)),
         prediction=as.numeric(substr(selection, 6, nchar(selection)-1))
  ) %>%
  select(ix, condition, batch, tid, stripe, dot, block, prediction, correct)

# Re-order trials
trial_lookup = data.frame(tid=sort(unique(trial_data$tid)))
trial_lookup$trial=seq(nrow(trial_lookup))

trial_data = trial_data %>%
  left_join(trial_lookup, by='tid')

trial_data = trial_data %>%
  select(ix, condition, batch, trial, stripe, dot, block, prediction) %>%
  arrange(ix, condition, batch, trial)

df.tw = trial_data
save(df.sw, df.tw, file='../data/exp_2_cleaned.rdata')

# Label data
labels = read_sheet("https://docs.google.com/spreadsheets/d/1xmfK-JrVznHkPfKPoicelXOW5Mj252G2TtY6O9PP2tM/")
labels = labels %>%
  mutate(condition=case_when(condition=='mult'~'combine',
                             condition=='sub'~'flip',
                             TRUE ~ condition)) %>%
  select(-prolific_id, -bonus) %>% 
  rename(
    input_a=task.input.a_input, match_a=a_correct, rule_a=a_rule,
    input_b=task.input.b_input, match_b=b_correct, rule_b=b_rule,
  ) %>%
  select(
    'ix', 'condition', 
    'input_a', 'match_a', 'match_a', 'rule_a',
    'input_b', 'match_b', 'match_b', 'rule_b',
    'local_change', 'feedback')
save(labels, file='../data/exp_4_coded.Rdata')


# Add coarse rule cat
labels = labels %>% 
  mutate(rule_cat_a=case_when(
    rule_a %in% c('incompatible', 'not_sure', 'random', 'no_effect', 'uncertain', 'NA') ~ 'uncertain',
    rule_a %in% c('relative', 'position', 'parity', 'nominal', 'description', 
                     'increase', 'decrease', 'mix', 'reverse', 'double', 'parit') ~ 'complex',
    TRUE ~ rule_a
  )) %>%
  mutate(rule_cat_b=case_when(
    rule_b %in% c('incompatible', 'not_sure', 'random', 'no_effect', 'uncertain', 'NA') ~ 'uncertain',
    rule_b %in% c('relative', 'position', 'parity', 'nominal', 'description', 
                       'increase', 'decrease', 'mix', 'reverse', 'double', 'parit') ~ 'complex',
    TRUE ~ rule_b
  ))
save(labels, file='../data/exp_4_coded.Rdata')



# Pull all experimental data together
load('../data/exp_1_cleaned.rdata')
load('../data/exp_1_coded.Rdata')

sw_colnames = all_of(colnames(df.sw))
tw_colnames = all_of(c('ix', 'condition', 'batch', 'trial', 'stripe', 'dot', 'block', 'prediction'))
label_colnames = all_of(colnames(labels))

df.sw.exp1 = df.sw %>% mutate(exp='exp_1') %>% select(c('exp', sw_colnames))
df.tw.exp1 = df.tw %>% mutate(exp='exp_1') %>% select(c('exp', tw_colnames))
labels.exp1 = labels %>% mutate(exp='exp_1') %>% select(c('exp', label_colnames))


load('../data/exp_2_cleaned.rdata')
load('../data/exp_2_coded.Rdata')
df.sw.exp2 = df.sw %>% mutate(exp='exp_2') %>% select(c('exp', sw_colnames))
df.tw.exp2 = df.tw %>% mutate(exp='exp_2') %>% select(c('exp', tw_colnames))
labels.exp2 = labels %>% mutate(exp='exp_2') %>% select(c('exp', label_colnames))


load('../data/exp_3_cleaned.rdata')
load('../data/exp_3_coded.Rdata')
df.sw.exp3 = df.sw %>% mutate(exp='exp_3') %>% select(c('exp', sw_colnames))
df.tw.exp3 = df.tw %>% mutate(exp='exp_3') %>% select(c('exp', tw_colnames))
labels.exp3 = labels %>% mutate(exp='exp_3') %>% select(c('exp', label_colnames))


load('../data/exp_4_cleaned.rdata')
load('../data/exp_4_coded.Rdata')
df.sw.exp4 = df.sw %>% mutate(exp='exp_4') %>% select(c('exp', sw_colnames))
df.tw.exp4 = df.tw %>% mutate(exp='exp_4') %>% select(c('exp', tw_colnames))
labels.exp4 = labels %>% mutate(exp='exp_4') %>% select(c('exp', label_colnames))


df.sw = rbind(df.sw.exp1, df.sw.exp2, df.sw.exp3, df.sw.exp4)
df.tw = rbind(df.tw.exp1, df.tw.exp2, df.tw.exp3, df.tw.exp4)
labels = rbind(labels.exp1, labels.exp2, labels.exp3, labels.exp4)

save(df.sw, df.tw, file='../data/all_cleaned.Rdata')
save(labels, file='../data/all_coded.Rdata')

# Get learning data as csv
load('../data/raw/exp_4_raw.rdata')
#colnames(df.tw)<-c('ix', 'id', 'batch', 'phase', 'trial', 'tid', 'agent', 'color', 'recipient', 'result', 'selection', 'correct')
colnames(df.tw)<-c('ix', 'id', 'batch', 'phase', 'trial', 'tid', 'agent', 'color', 'recipient', 'result', 'alter', 'selection', 'correct', 'gtCorrect')
save(df.sw, df.tw, file='../data/raw/exp_4_raw.rdata')

conditions = df.sw %>% select(ix, condition) %>%
  #mutate(condition=ifelse(condition=='comp_mult', 'construct', ifelse(condition=='comp_mult_reverse', 'decon', 'combine')))
  mutate(condition=ifelse(condition=='mult', 'combine', 'flip'))

df.tw = df.tw %>% left_join(conditions, by='ix')
ld = df.tw %>%
  filter(phase=='learn') %>%
  select(condition, phase, batch, trial, agent, recipient, result) %>%
  unique() %>%
  mutate(
    batch=ifelse(batch=='alice', 'A', 'B'),
    stripe=as.numeric(substr(agent, 2, 2)),
    dot=as.numeric(substr(agent, 4, 4)),
    block=as.numeric(substr(recipient, 6, 6)),
    result_block=ifelse(phase=='learn', as.numeric(substr(result, 6, nchar(result)-1)), block)) %>%
  select(condition, batch, trial, stripe, dot, block, result_block)

load('../data/exp_4_cleaned.rdata')
gd = df.tw %>% 
  mutate(batch='gen', result_block=0) %>%
  select(condition, batch, trial, stripe, dot, block, result_block) %>%
  unique()

tasks = rbind(ld, gd) %>% arrange(condition, batch, trial)
rownames(tasks) = NULL
write.csv(tasks, '../data/tasks/exp_4.csv')


#### Re-order gen trials ####
backup = df.tw

exp1 = df.tw %>% filter(exp=='exp_1')
exp2 = df.tw %>% filter(exp=='exp_2')
exp3 = df.tw %>% filter(exp=='exp_3')
exp4 = df.tw %>% filter(exp=='exp_4')

exp1_order = exp1 %>%
  select(condition, trial, stripe, dot, block) %>%
  unique() %>%
  rename(exp1_tid=trial)

exp2_preordered = exp2 %>%
  select(condition, trial, stripe, dot, block) %>%
  unique()
names(exp2_preordered)=c('condition','trial','exp2_stripe','exp2_dot','block')
exp2_ordered_id = exp2_preordered %>%
  mutate(stripe=exp2_dot, dot=exp2_stripe) %>%
  left_join(exp1_order, by=c('condition','stripe','dot','block')) %>%
  mutate(stripe=exp2_stripe, dot=exp2_dot, new_tid=exp1_tid) %>%
  select(condition, trial, new_tid)

exp2_data = exp2 %>%
  left_join(exp2_ordered_id, by=c('condition','trial')) %>%
  mutate(trial=new_tid) %>%
  select(-new_tid) %>%
  arrange(condition, ix, batch, trial)
exp1 = exp1 %>%
  arrange(condition, ix, batch, trial)


exp3_order = exp3 %>%
  select(condition, trial, stripe, dot, block) %>%
  unique() %>%
  rename(exp3_tid=trial)

exp4_preordered = exp4 %>%
  select(condition, trial, stripe, dot, block) %>%
  unique()
names(exp4_preordered)=c('condition','trial','exp4_stripe','exp4_dot','block')
exp4_ordered_id = exp4_preordered %>%
  mutate(stripe=exp4_dot, dot=exp4_stripe) %>%
  left_join(exp3_order, by=c('condition','stripe','dot','block')) %>%
  mutate(stripe=exp4_stripe, dot=exp4_dot, new_tid=exp3_tid) %>%
  select(condition, trial, new_tid)

exp4_data = exp4 %>%
  left_join(exp4_ordered_id, by=c('condition','trial')) %>%
  mutate(trial=new_tid) %>%
  select(-new_tid) %>%
  arrange(condition, ix, batch, trial)
exp3 = exp3 %>%
  arrange(condition, ix, batch, trial)

df.tw = rbind(exp1, exp2_data, exp3, exp4_data)
df.tw = df.tw %>%
  mutate(exp_id=as.numeric(substr(exp, 5, 6))) %>%
  select(exp_id, ix, condition, batch, trial, stripe, dot, block, prediction)
save(df.sw, df.tw, file='../data/all_cleaned.Rdata')


