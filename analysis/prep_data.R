
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
         certainty_b=as.numeric(as.character(certainty_b)))
df.sw[3,'age'] = 42


colnames(df.tw.raw)<-c('ix', 'id', 'batch', 'phase', 'trial', 'tid', 'agent', 'agent_color', 'recipient', 'result', 'selection', 'correct')
df.tw = df.tw.raw %>%
  mutate(batch=ifelse(batch=='alice', 'A', 'B')) %>%
  filter(phase=='gen') %>%
  select(ix, batch, trial, tid, agent, recipient, result, selection, correct)

conditions = df.sw %>% select(ix, condition) 
df.tw = df.tw %>%
  left_join(conditions, by='ix')

save(df.sw, df.tw, file='data/pilot_1_cleaned.rdata')


