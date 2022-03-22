
library(dplyr)

normalize<-function(vec) {
  return (vec/sum(vec))
}

#### Experiment 1 ####
task = read.csv('../../data/tasks/exp_1.csv') %>% select(-X)

lg_preds = function(cond, bt) {
  train_data = task %>% filter(condition==cond, batch==bt)
  lg_model = lm(result_block~stripe+dot+block, data=train_data)
  
  all_terms = data.frame(terms=c(0, seq(16)))
  for (ti in 1:8) {
    gen_data = task %>% filter(batch=='gen', condition==cond, trial==tid) %>% select(-result_block)
    gen_pred = round(predict(lg_model, gen_data))
  }
  
  colname=paste0('prob_', tid)
  all_terms[,colname]=0
  all_terms[all_terms$terms==gen_pred,colname]=1
  
  return(all_terms)
  
}


