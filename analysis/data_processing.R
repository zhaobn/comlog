
library(dplyr)
library(tidyr)

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

#### Fix exp 4 names ####
exp4 = filter(df.tw, exp_id==4)
others = filter(df.tw, exp_id!=4)
exp4 = exp4 %>%
  mutate(batch=ifelse(batch=='alice','A','B'))
df.tw = rbind(others, exp4)
save(df.sw, df.tw, file = '../data/all_cleaned.Rdata')

#### Get all task answers into a single csv ####
answer_cols = c('exp_id','condition','trial','stripe','dot','block','gt','alt')
answer_df = data.frame(matrix(ncol=length(answer_cols), nrow = 0))
colnames(answer_df) <- answer_cols

for (eid in seq(4)) {
  expdata=read.csv(paste0('../data/tasks/exp_',eid,'.csv')) %>%
    filter(batch=='gen') %>%
    mutate(exp_id=eid) %>%
    select(exp_id,condition,trial,stripe,dot,block,gt,alt)
  answer_df = rbind(answer_df, expdata)
}

write.csv(answer_df, file='../data/tasks/answers.csv')



#### Re-order model preds ####
# Read python run orders
py_gen_s = read.csv('../python/for_exp/s_gen.csv') %>% select(-c('condition', 'batch', 'X'))
py_gen_d = read.csv('../python/for_exp/d_gen.csv') %>% select(-c('condition', 'batch', 'X'))

# Read mturk orders
mturk_gen_s = read.csv('../data/tasks/exp_1.csv') %>%
  filter(condition=='construct', batch=='gen') %>%
  select(trial, stripe, dot, block) %>%
  unique()
mturk_gen_d = read.csv('../data/tasks/exp_2.csv') %>%
  filter(condition=='construct', batch=='gen') %>%
  select(trial, stripe, dot, block) %>%
  unique()

# Use mturk trial id for python runs
py_gen_s_extra = py_gen_s %>% left_join(mturk_gen_s, by=c('stripe','dot','block')) 
py_gen_d_extra = py_gen_d %>% left_join(mturk_gen_d, by=c('stripe','dot','block')) 

# Re-order python run results 
reorder_preds = function(read_path, mname, exp_id, cond, batch) {
  
  # Read model input
  mruns = read.csv(read_path) %>% select(-X)
  mruns = mruns %>%
    select(terms, starts_with('prob_')) %>%
    gather('tid', 'prob', -terms) %>%
    mutate(tid=as.numeric(substr(tid,6,nchar(tid))))
  
  # Prep ordering
  if (exp_id%%2==1) {
    ordering = py_gen_s_extra %>%
      mutate(tid=pyid+1) %>%
      select(tid, trial)
  } else {
    ordering = py_gen_d_extra %>%
      mutate(tid=pyid+1) %>%
      select(tid, trial) 
  }
  
  # Get ordered preds
  mruns_ordered = mruns %>%
    left_join(ordering, by='tid') %>%
    select(terms, trial, prob) %>%
    spread(trial, prob)
  colnames(mruns_ordered) = c('terms', paste0('prob_',seq(8)))
  
  # save
  write.csv(mruns_ordered, 
            file=paste0('../model_data/',mname,'/exp_',as.character(exp_id),'/',cond,'_preds_',tolower(batch),'.csv'))
}

# Reorder AG model preds
reorder_preds('../data/model_preds/stripes/construct_preds_a.csv', 'ag', 1, 'construct', 'a')
reorder_preds('../data/model_preds/stripes/construct_preds_b.csv', 'ag', 1, 'construct', 'b')
reorder_preds('../data/model_preds/stripes/combine_preds_a.csv', 'ag', 1, 'combine', 'a')
reorder_preds('../data/model_preds/stripes/combine_preds_b.csv', 'ag', 1, 'combine', 'b')
reorder_preds('../data/model_preds/stripes/preds.csv', 'ag', 1, 'decon', 'a')
reorder_preds('../data/model_preds/stripes/preds.csv', 'ag', 1, 'decon', 'b')

reorder_preds('../data/model_preds/spots/construct_preds_a.csv', 'ag', 2, 'construct', 'a')
reorder_preds('../data/model_preds/spots/construct_preds_b.csv', 'ag', 2, 'construct', 'b')
reorder_preds('../data/model_preds/spots/combine_preds_a.csv', 'ag', 2, 'combine', 'a')
reorder_preds('../data/model_preds/spots/combine_preds_b.csv', 'ag', 2, 'combine', 'b')
reorder_preds('../data/model_preds/spots/preds.csv', 'ag', 2, 'decon', 'a')
reorder_preds('../data/model_preds/spots/preds.csv', 'ag', 2, 'decon', 'b')

reorder_preds('../data/model_preds/stripes/combine_preds_a.csv', 'ag', 3, 'combine', 'a')
reorder_preds('../data/model_preds/stripes/combine_preds_b.csv', 'ag', 3, 'combine', 'b')
reorder_preds('../data/model_preds/stripes/flip_preds_a.csv', 'ag', 3, 'flip', 'a')
reorder_preds('../data/model_preds/stripes/flip_preds_b.csv', 'ag', 3, 'flip', 'b')

reorder_preds('../data/model_preds/spots/combine_preds_a.csv', 'ag', 4, 'combine', 'a')
reorder_preds('../data/model_preds/spots/combine_preds_b.csv', 'ag', 4, 'combine', 'b')
reorder_preds('../data/model_preds/spots/flip_preds_a.csv', 'ag', 4, 'flip', 'a')
reorder_preds('../data/model_preds/spots/flip_preds_b.csv', 'ag', 4, 'flip', 'b')

# Reorder PCFG model preds
for (eid in seq(4)) {
  if (eid<3) {
    conds = c('combine', 'construct', 'decon')
  } else {
    conds = c('combine', 'flip')
  }
  for (cond in conds) {
    for (batch in c('a', 'b')) {
      data_path=paste0('../python/pcfgs/data_perbatch/exp_',as.character(eid),'/',cond,'_preds_',batch,'.csv')
      reorder_preds(data_path, 'pcfg', eid, cond, batch)
    }
  }
}





