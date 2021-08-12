
library(dplyr)
rm(list=ls())

load('data/pilot_1.rdata')

# Output to googlesheet to bonus participants
to_sheet = df.sw %>%
  select(ix, prolific_id, condition, task.input.a_input, task.input.b_input, feedback, correct)
write.csv(to_sheet, file='data/pilot_1_responses.csv')

# Clean up for analysis