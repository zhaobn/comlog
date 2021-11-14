
library(dplyr)
library(googlesheets4)
rm(list=ls())

load('../data/raw/exp_2_raw.rdata')

# Output to googlesheet to bonus participants
# When bonus-ing, select prolific_id column
# When publishing data, remove the prolific_id column
to_sheet = df.sw %>% 
  select(ix, condition, task.input.a_input, task.input.b_input, feedback, correct)
write.csv(to_sheet, file='../data/responses/exp_2_responses.csv')

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
  mutate(condition=case_when(condition=='comp_const'~'combine', 
                             condition=='comp_mult'~'construct', 
                             condition=='comp_mult_reverse'~'decon'))

# df.sw[144,'age'] = 33
# df.sw[35,'age'] = 31


#### Transform trial data ####
colnames(df.tw.raw)<-c('ix', 'id', 'batch', 'phase', 'trial', 'tid', 'agent', 'agent_color', 'recipient', 'result', 'selection', 'correct')
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
  select(ix, condition, batch, trial, stripe, dot, block, prediction, correct) %>%
  arrange(ix, condition, batch, trial)

df.tw = trial_data
save(df.sw, df.tw, file='../data/exp_2_cleaned.rdata')

# Label data
labels = read_sheet("https://docs.google.com/spreadsheets/d/1xmfK-JrVznHkPfKPoicelXOW5Mj252G2TtY6O9PP2tM/")
labels = labels  %>%
  mutate(condition=case_when(condition=='comp_const'~'combine', 
                             condition=='comp_mult'~'construct', 
                             condition=='comp_mult_reverse'~'decon'))
labels = labels %>% select(-bonus)
labels = labels %>% 
  rename(
    input_a=task.input.a_input, match_a=a_correct, rule_a=a_rule,
    input_b=task.input.b_input, match_b=b_correct, rule_b=b_rule,
  ) %>%
  select(
    'ix', 'condition', 
    'input_a', 'match_a', 'match_a', 'rule_a',
    'input_b', 'match_b', 'match_b', 'rule_b',
    'local_change', 'feedback')
save(labels, file='../data/exp_2_coded.Rdata')


# Add coarse rule cat
labels = labels %>% 
  mutate(rule_cat_a=case_when(
    rule_a %in% c('incompatible', 'not_sure', 'random') ~ 'uncertain',
    rule_a %in% c('relative', 'position', 'parity', 'nominal', 'description', 
                     'increase', 'decrease', 'mix', 'reverse') ~ 'complex',
    TRUE ~ rule_a
  )) %>%
  mutate(rule_cat_b=case_when(
    rule_b %in% c('incompatible', 'not_sure', 'random') ~ 'uncertain',
    rule_b %in% c('relative', 'position', 'parity', 'nominal', 'description', 
                       'increase', 'decrease', 'mix', 'reverse') ~ 'complex',
    TRUE ~ rule_b
  ))
save(labels, file='../data/exp_2_coded.Rdata')









