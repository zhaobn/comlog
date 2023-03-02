
library(tidyverse)

# Load data

gpt3_data = read_csv('converted.csv')[,-c(1,2)]
answers = read_csv('../data/tasks/answers.csv')[,-1]
ppt_data = read_csv('../data/osf/trials.csv')

tasks = gpt3_data %>%
  select(exp_id, condition, phase, trial=task) %>%
  unique()

gpt3_extended = data.frame()
for (i in 1:nrow(tasks)) {
  task_data = tasks[i,]
  task_extended = bind_rows(replicate(17, task_data, simplify = FALSE))
  task_extended['prediction'] = seq(0,16)
  
  gpt_preds = gpt3_data %>%
    filter(exp_id==task_data[['exp_id']], condition==task_data[['condition']], phase==task_data[['phase']], task==task_data[['trial']]) %>%
    select(exp_id, condition, phase, trial=task, prediction=num, prob)
  
  residue_p = (1-sum(gpt_preds$prob))/(17-nrow(gpt_preds))
  
  task_full = task_extended %>%
    left_join(gpt_preds, by=c('exp_id', 'condition', 'phase', 'trial', 'prediction')) %>%
    mutate(prob=ifelse(is.na(prob), residue_p, prob))
  
  gpt3_extended = rbind(gpt3_extended, task_full)
}

df.gpt3 = gpt3_extended
save(df.gpt3, file='gpt3_data.rdata')


# Stats
accs_data = answers %>% select(exp_id, condition, trial, gt)
accs_gpt = df.gpt3 %>%
  left_join(accs_data, by=c('exp_id', 'condition', 'trial')) %>%
  mutate(gt=gt==prediction)

accs_gpt %>%
  group_by(condition, phase) %>%
  summarise(acc=sum(prob*gt)/sum(prob))

sum(accs_gpt$prob*accs_gpt$gt)/sum(accs_gpt$prob)





















