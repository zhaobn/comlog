
library(dplyr)
rm(list=ls())

load('data/pilot_1_raw.rdata')

# Output to googlesheet to bonus participants
to_sheet = df.sw %>%
  select(ix, prolific_id, condition, task.input.a_input, task.input.b_input, feedback, correct)
write.csv(to_sheet, file='data/pilot_1_responses.csv')

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
                             condition=='comp_mult_reverse'~'discern'))
df.sw[3,'age'] = 42

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
         prediction=as.numeric(substr(selection, 6, 6)),
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
save(df.sw, df.tw, file='data/pilot_1_cleaned.rdata')

# Aggregate










