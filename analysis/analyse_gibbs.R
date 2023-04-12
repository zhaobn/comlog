
library(dplyr)
library(tidyr)

load('../data/all_cleaned.Rdata')
ppt_data = df.tw %>% count(condition, batch, trial, prediction)


sigmoid = function(x) return(1/(1+exp(-x)))
NCHUNK=17
hazdata = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(data)
}
hazfit = function(data, par) {
  data$transformed = sigmoid(par)/NCHUNK+(1-sigmoid(par))*data$prob
  data$ll = log(data$transformed)*data$n
  return(-sum(data$ll))
}

conditions = c('construct','combine','decon','flip')
batches = c('a','b')
#runs = c('', '_allframes', '_d2')
local_path_prefix = '../python' # '' for server




#### Overall fits #### 

fit_pred = function(run_name, iter) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0(local_path_prefix, '/sims/data',run_name,'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add ppt data
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  out = optim(par=0, hazfit, method="L-BFGS-B", data=model_ppt)
  
  model_name = run_name
  if (nchar(model_name) < 1) {
    model_name = 'd1'
  } else {
    model_name = substr(model_name, 2, nchar(model_name))
  }
  
  # Return
  return (list(run=toupper(model_name), iter=iter, fit=out$value, param=out$par))
}



# fit_results = read.csv(text='run,iter,fit,param')
# fit_results = read.csv('params/fit_results.csv') %>% select(-X)

iters = c(seq(10),2**seq(4,10),seq(11,15)*100, seq(20, 50, 5)*100)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('',i)))
}


iters = 2**seq(9)
fit_results = read.csv('params/fit_results.csv') %>% select(-X)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('_allframes',i)))
}


iters = seq(10)
fit_results = read.csv('params/fit_results.csv') %>% select(-X)
for (i in iters) {
  fit_results = rbind(fit_results,data.frame(fit_pred('_d2',i)))
}

write.csv(fit_results, 'params/fit_results.csv')




#### Cross validation #### 

cross_fit = function(run_name, iter, cond_name) {
  # Get model data
  model_data = read.csv(text='condition,batch,trial,prediction,prob')
  for (cond in conditions) {
    for (batch in batches) {
      model_raw=read.csv(paste0(local_path_prefix, '/sims/data',run_name,'/process_',iter,'/',cond,'_preds_',tolower(batch),'.csv'))
      model_raw = model_raw %>%
        select(term=terms, starts_with('prob')) %>%
        gather('trial', 'prob', -term) %>%
        mutate(trial=as.numeric(substr(trial, 6, nchar(trial))), 
               prediction=term, condition=cond, batch=toupper(batch)) %>%
        select(condition, batch, trial, prediction, prob)
      
      model_data = rbind(model_data, model_raw)
    }
  }
  
  # Add ppt data
  model_ppt=model_data %>%
    left_join(ppt_data, by=c('condition', 'batch', 'trial', 'prediction')) %>%
    mutate(n=ifelse(is.na(n),0, n)) %>%
    arrange(condition, batch, trial, prediction)
  
  # Fit
  training_set = model_ppt[!(model_ppt$condition==cond_name),]
  test_set = model_ppt[model_ppt$condition==cond_name,]
  
  out = optim(par=0, hazfit, method="L-BFGS-B", data=training_set)
  fitted = hazdata(test_set, out$par)
  
  model_name = run_name
  if (nchar(model_name) < 1) {
    model_name = 'd1'
  } else {
    model_name = substr(model_name, 2, nchar(model_name))
  }
  
  # Return
  return (list(run=toupper(model_name), iter=iter, condition=cond_name, cfit=sum(fitted$ll)))
}


crossv_results = read.csv(text='run,iter,condition,cfit')
# fit_results = read.csv('params/fit_results.csv') %>% select(-X)

iters = c(seq(10),2**seq(4,10),seq(11,15)*100, seq(20, 50, 5)*100)
for (i in iters) {
  for (c in conditions) {
    crossv_results = rbind(crossv_results,data.frame(cross_fit('',i, c)))
  }
}
write.csv(crossv_results, file = 'params/cross_results.csv')






