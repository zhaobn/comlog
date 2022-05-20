
library(dplyr)

load('../data/all_cleaned.Rdata')

#### Get task file for each experiment ####
save_task <- function(eid) {
  ## Read task
  task_init = read.csv(paste0('../data/tasks/before_reorder/exp_',as.character(eid),'.csv')) %>% select(-X)
  gen_init = task_init %>%
    filter(batch=='gen') %>%
    select(condition, tid=trial, stripe, dot, block)
  
  ## Order gen trials in order to collapse for feature counter-balancing trials
  gen_ordered = df.tw %>%
    filter(exp_id==eid) %>%
    select(condition, trial, stripe, dot, block) %>%
    unique()
  gen_ordering = gen_init %>%
    left_join(gen_ordered, by=c('condition','stripe','dot','block')) %>%
    select(condition, trial, stripe, dot, block) %>%
    arrange(condition, trial)
  
  ## Include ground-truth (gt) and alternative (alt) answers for gen trials
  if (eid %% 2 == 1) {
    gen_extended = gen_ordering %>%
      mutate(gt=stripe*block-dot, alt=stripe*(block-dot))
  } else {
    gen_extended = gen_ordering %>%
      mutate(gt=dot*block-stripe, alt=dot*(block-stripe))
  }
  gen_extended = gen_extended %>%
    mutate(gt=ifelse(gt<0, 0, gt), alt=ifelse(alt<0, 0, alt))
  
  # Combine with learn tasks, formatting
  learn_task=task_init %>%
    filter(batch!='gen') %>%
    mutate(gt=0, alt=0)
  gen_extended = gen_extended %>%
    mutate(batch='gen', result_block=0) %>%
    select(names(learn_task))
  
  task_ordered = rbind(learn_task, gen_extended) %>%
    arrange(condition, batch, trial)
  
  # Save to csv
  write.csv(task_ordered, file=paste0('../data/tasks/exp_',as.character(eid),'.csv'))
  
}


for (i in seq(4)) {
  save_task(i)
}



#### Re-order model preds ####












