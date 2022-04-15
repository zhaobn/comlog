
library(dplyr)
library(nnet)

normalize<-function(vec) {
  return (vec/sum(vec))
}

#### Linear regressions ####
task = read.csv('../../data/tasks/exp_1.csv') %>% select(-X)

lg_preds = function(cond, bt) {
  train_data = task %>% filter(condition==cond, batch==bt)
  lg_model = lm(result_block~stripe+dot+block, data=train_data)
  
  all_terms = data.frame(terms=c(0, seq(16)))
  for (tid in 1:8) {
    gen_data = task %>% filter(batch=='gen', condition==cond, trial==tid) %>% select(-result_block)
    gen_pred = round(predict(lg_model, gen_data))
    colname=paste0('prob_', tid)
    all_terms[,colname]=0
    all_terms[all_terms$terms==gen_pred,colname]=1
  }

  return(all_terms)
  
}


lg_preds('construct', 'B')


#### Multinomial logistic regression ####
experi='exp_2'
task_data = read.csv(paste0('../../data/tasks/', experi, '.csv')) %>% select(-X)

for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    # Get training data
    train_data = task_data %>%
      filter(condition==cond, batch!='gen') %>%
      mutate(result_block=as.factor(as.character(result_block)))
    train_data = if (toupper(phase)=='A') filter(train_data, batch=='A') else train_data
    train_data$result_block=relevel(train_data$result_block, ref='0')
    
    # Fit multinom
    trained = multinom(result_block ~ stripe + dot + block, data = train_data)
    params = exp(coef(trained))
    
    # Get predictions
    result_df = data.frame(term=c(0, seq(16))) %>% mutate(term=as.character(term))
    for (tid in seq(8)) {
      all_terms = data.frame(term=c(0, seq(16))) %>% mutate(term=as.character(term))
      pcol=paste0('prob_', tid)
      
      gen_data = task_data %>% filter(batch=='gen', condition==cond, trial==tid) %>% select(-result_block)
      pbs = predict(trained, type="probs", newdata=gen_data)
      if (length(pbs)>1) {
        pb_classes = names(pbs)
      } else {
        pb_classes = predict(trained, type="class", newdata=gen_data)
      }
      pb_df = data.frame(term=pb_classes, prob=pbs)
      
      preds = all_terms %>%
        left_join(pb_df, by='term') %>%
        mutate(prob=if_else(is.na(prob), 0, prob))
      colnames(preds) = c('term', pcol)
      
      result_df = result_df %>% left_join(preds, by='term')
    }
    write.csv(result_df, file=paste0('multinom_preds/', experi, '/', cond, '_preds_', tolower(phase), '.csv'))
  }
}











