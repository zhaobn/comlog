
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)

#### Plots for Experiment 1 ####
load('../data/exp_1_cleaned.rdata')
tasks = df.tw %>%
  mutate(answer=stripe*block-dot) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  select(condition, batch, trial, answer) %>%
  unique()

# Plot gen accuracy people
acc_data = df.tw %>%
  mutate(answer=stripe*block-dot) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  mutate(acc=prediction==answer) %>%
  group_by(condition, batch) %>%
  summarise(n=n(), acc=sum(acc), accuracy=sum(acc)/n()) %>%
  mutate(condition=factor(condition, levels=c('construct','combine','decon')))

ggplot(acc_data, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# What's the accuracy if no change
no_change_acc = df.tw %>%
  mutate(answer=stripe*block-dot) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  mutate(acc=block==answer) %>%
  group_by(condition, batch) %>%
  summarise(n=n(), acc=sum(acc), accuracy=sum(acc)/n())

ggplot(acc_data, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.25, linetype="dashed", color = "red", size=1) +
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )


# Process model predictions for accuracy measure
read_data = function(path_prefix, cond, phase) {
  data = read.csv(paste0(path_prefix, cond, '_preds_', phase, '.csv')) %>%
    select(pred=terms, starts_with('prob')) %>%
    gather('trial','prob',-pred) %>%
    mutate(trial=as.numeric(substr(trial, 6, 7)), condition=cond, batch=toupper(phase)) %>%
    select(condition, batch, trial, pred, prob)
  return(data)
}

file_path = '../python/pcfgs/data/exp_1/' #'../data/model_preds/exp_1/'
model_preds = read_data(file_path, 'construct', 'a') 
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds = rbind(model_preds, read_data(file_path, cond, phase))
    }
  }
}
model_preds = model_preds %>% mutate(prob=round(prob, 4)) 
 
model_acc = model_preds %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=prob*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(prob), n_acc=sum(total_correct), acc=sum(total_correct)/sum(prob)) %>%
  select(condition, batch, ARC=acc)

acc_data = acc_data %>%
  left_join(model_acc, by=c('condition', 'batch'))
  
ggplot(acc_data, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.06, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(y=ARC), stat="identity", shape=6, color='red', size=3, stroke=1.5)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Fit a softmax
all_preds = model_preds %>%
  select(condition, batch, trial, pred)

to_fit = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds, by=c('condition', 'batch', 'trial', 'pred'))

softmax<-function(vec, base=0, type='') {
  if (type!='log') {
    v_exp<-exp(vec*base); sum<-sum(v_exp)
  } else {
    v_exp<-exp(log(vec)*base); sum<-sum(v_exp)
  }
  return(v_exp/sum)
}

fit_ll<-function(b, data, type='fit') {
  softed<-filter(data, condition=='combine', batch=='A', trial==1)%>%mutate(soft=softmax(prob, b))
  for (c in c('combine','construct','decon')) {
    for (h in c('A', 'B')) {
      for (i in 1:8) {
        if (!(c=='combine' & h=='A' & i==1)) {
          softed<-rbind(softed, 
                        filter(data, condition==c, batch==h, trial==i)%>%mutate(soft=softmax(prob, b)))
        }
      }
    }
  }
  if (type=='fit') {
    return(-sum(softed$n*log(softed$soft)))
  } else {
    return(softed)
  }
}
fit_ll(1, to_fit)
# 165*16*log(1/16) # -7319.634
-2*(-7319.634)

out<-optim(par=6, fn=fit_ll, data=to_fit, method='Brent', lower=0, upper=100)
out$par #2.523922
out$value #6168.963
log(165*16)-2*(-6169.963)


# Have a look at acc after softmax
model_preds_sfed = fit_ll(2.56, to_fit, 'raw')
model_acc_sfed = model_preds_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, ARC=acc)

acc_data_sfed = acc_data %>%
  left_join(model_acc_sfed, by=c('condition', 'batch'))

ggplot(acc_data_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(y=ARC), stat="identity", shape=2, color='red', size=3, stroke=1.5)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Slicing model (d=1)
model_preds_sd1 = read_data('../data/model_preds/exp_1/slice_d1/', 'construct', 'a')
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds_sd1 = rbind(model_preds_sd1, read_data('../data/model_preds/exp_1/slice_d1/', cond, phase))
    }
  }
}

all_preds_sd1 = model_preds_sd1 %>%
  select(condition, batch, trial, pred)

to_fit_sd1 = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds_sd1, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds_sd1, by=c('condition', 'batch', 'trial', 'pred'))

out<-optim(par=6, fn=fit_ll, data=to_fit_sd1, method='Brent', lower=0, upper=100)
out$par #2.792165
out$value #6738.768
log(165*16)-2*(-6738.768)


# Plot it
model_preds_sd1_sfed = fit_ll(2.79, to_fit_sd1, 'raw')
model_acc_sd1_sfed = model_preds_sd1_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, slice_d1=acc)

acc_data_sd1_sfed = acc_data_sfed %>%
  left_join(model_acc_sd1_sfed, by=c('condition', 'batch'))

model_accs = acc_data_sd1_sfed %>%
  select(condition, batch, ARC, slice_d1) %>%
  gather('model', 'acc', ARC, slice_d1)
  
  
ggplot(acc_data_sd1_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(x=batch, y=acc, color=model, shape=model), size=3, stroke=1.5, data=model_accs)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Slice d2 
model_preds_sd2 = read_data('../data/model_preds/exp_1/slice_d2/', 'construct', 'a')
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds_sd2 = rbind(model_preds_sd2, read_data('../data/model_preds/exp_1/slice_d2/', cond, phase))
    }
  }
}

all_preds_sd2 = model_preds_sd2 %>%
  select(condition, batch, trial, pred)

to_fit_sd2 = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds_sd2, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds_sd2, by=c('condition', 'batch', 'trial', 'pred'))

out<-optim(par=6, fn=fit_ll, data=to_fit_sd2, method='Brent', lower=0, upper=100)
out$par #2.842094
out$value #6285.46
log(165*16)-2*(-6285.46)

model_preds_sd2_sfed = fit_ll(2.84, to_fit_sd2, 'raw')
model_acc_sd2_sfed = model_preds_sd2_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, slice_d2=acc)

acc_data_sd2_sfed = acc_data_sd1_sfed %>%
  left_join(model_acc_sd2_sfed, by=c('condition', 'batch'))

model_accs = acc_data_sd2_sfed %>%
  select(condition, batch, ARC, slice_d1, slice_d2) %>%
  gather('model', 'acc', ARC, slice_d1, slice_d2) %>%
  mutate(model=case_when(
    model=='ARC'~'AG',
    model=='slice_d1'~'SO_d1',
    model=='slice_d2'~'SO_d2',
  ))


# Final plot for paper
ggplot(acc_data_sd2_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  # geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(x=batch, y=acc, color=model, shape=model), size=3, stroke=1.5, data=model_accs)+
  scale_shape_manual(values=c(2, 0, 1)) +
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

#### End of Plots for Experiment 1

#### Plots for Experiment 2 ####
load('../data/exp_2_cleaned.rdata')
tasks = df.tw %>%
  mutate(answer=dot*block-stripe) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  select(condition, batch, trial, answer) %>%
  unique()

# Plot gen accuracy people
acc_data = df.tw %>%
  mutate(answer=dot*block-stripe) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  mutate(acc=prediction==answer) %>%
  group_by(condition, batch) %>%
  summarise(n=n(), acc=sum(acc), accuracy=sum(acc)/n()) %>%
  mutate(condition=factor(condition, levels=c('construct','combine','decon')))

ggplot(acc_data, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )


# Process model predictions for accuracy measure
read_data = function(path_prefix, cond, phase) {
  data = read.csv(paste0(path_prefix, cond, '_preds_', phase, '.csv')) %>%
    select(pred=terms, starts_with('prob')) %>%
    gather('trial','prob',-pred) %>%
    mutate(trial=as.numeric(substr(trial, 6, 7)), condition=cond, batch=toupper(phase)) %>%
    select(condition, batch, trial, pred, prob)
  return(data)
}

file_path = '../python/pcfgs/data/exp_2/'
model_preds = read_data(file_path, 'construct', 'a') 
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds = rbind(model_preds, read_data(file_path, cond, phase))
    }
  }
}
model_preds = model_preds %>% mutate(prob=round(prob, 4)) 

model_acc = model_preds %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=prob*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(prob), n_acc=sum(total_correct), acc=sum(total_correct)/sum(prob)) %>%
  select(condition, batch, ARC=acc)

acc_data = acc_data %>%
  left_join(model_acc, by=c('condition', 'batch'))

ggplot(acc_data, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.06, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(y=ARC), stat="identity", shape=6, color='red', size=3, stroke=1.5)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Fit a softmax
all_preds = model_preds %>%
  select(condition, batch, trial, pred)

to_fit = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds, by=c('condition', 'batch', 'trial', 'pred'))

softmax<-function(vec, base=0, type='') {
  if (type!='log') {
    v_exp<-exp(vec*base); sum<-sum(v_exp)
  } else {
    v_exp<-exp(log(vec)*base); sum<-sum(v_exp)
  }
  return(v_exp/sum)
}

fit_ll<-function(b, data, type='fit') {
  softed<-filter(data, condition=='combine', batch=='A', trial==1)%>%mutate(soft=softmax(prob, b))
  for (c in c('combine','construct','decon')) {
    for (h in c('A', 'B')) {
      for (i in 1:8) {
        if (!(c=='combine' & h=='A' & i==1)) {
          softed<-rbind(softed, 
                        filter(data, condition==c, batch==h, trial==i)%>%mutate(soft=softmax(prob, b)))
        }
      }
    }
  }
  if (type=='fit') {
    return(-sum(softed$n*log(softed$soft)))
  } else {
    return(softed)
  }
}
fit_ll(1, to_fit)
# 165*16*log(1/16) # -7319.634
-2*(-7319.634)

out<-optim(par=6, fn=fit_ll, data=to_fit, method='Brent', lower=0, upper=100)
out$par #2.523922
out$value #6168.963
log(165*16)-2*(-6169.963)


# Have a look at acc after softmax
model_preds_sfed = fit_ll(2.56, to_fit, 'raw')
model_acc_sfed = model_preds_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, ARC=acc)

acc_data_sfed = acc_data %>%
  left_join(model_acc_sfed, by=c('condition', 'batch'))

ggplot(acc_data_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(y=ARC), stat="identity", shape=2, color='red', size=3, stroke=1.5)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Slicing model (d=1)
model_preds_sd1 = read_data('../data/model_preds/exp_1/slice_d1/', 'construct', 'a')
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds_sd1 = rbind(model_preds_sd1, read_data('../data/model_preds/exp_1/slice_d1/', cond, phase))
    }
  }
}

all_preds_sd1 = model_preds_sd1 %>%
  select(condition, batch, trial, pred)

to_fit_sd1 = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds_sd1, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds_sd1, by=c('condition', 'batch', 'trial', 'pred'))

out<-optim(par=6, fn=fit_ll, data=to_fit_sd1, method='Brent', lower=0, upper=100)
out$par #2.792165
out$value #6738.768
log(165*16)-2*(-6738.768)


# Plot it
model_preds_sd1_sfed = fit_ll(2.79, to_fit_sd1, 'raw')
model_acc_sd1_sfed = model_preds_sd1_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, slice_d1=acc)

acc_data_sd1_sfed = acc_data_sfed %>%
  left_join(model_acc_sd1_sfed, by=c('condition', 'batch'))

model_accs = acc_data_sd1_sfed %>%
  select(condition, batch, ARC, slice_d1) %>%
  gather('model', 'acc', ARC, slice_d1)


ggplot(acc_data_sd1_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(x=batch, y=acc, color=model, shape=model), size=3, stroke=1.5, data=model_accs)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# Slice d2 
model_preds_sd2 = read_data('../data/model_preds/exp_1/slice_d2/', 'construct', 'a')
for (cond in c('construct', 'combine', 'decon')) {
  for (phase in c('a', 'b')) {
    if (!(cond=='construct'&phase=='a')) {
      model_preds_sd2 = rbind(model_preds_sd2, read_data('../data/model_preds/exp_1/slice_d2/', cond, phase))
    }
  }
}

all_preds_sd2 = model_preds_sd2 %>%
  select(condition, batch, trial, pred)

to_fit_sd2 = df.tw %>% 
  count(condition, batch, trial, prediction) %>% 
  select(condition, batch, trial, pred=prediction, n) %>%
  full_join(all_preds_sd2, by=c('condition', 'batch', 'trial', 'pred')) %>%
  arrange(condition, batch, trial, pred) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  left_join(model_preds_sd2, by=c('condition', 'batch', 'trial', 'pred'))

out<-optim(par=6, fn=fit_ll, data=to_fit_sd2, method='Brent', lower=0, upper=100)
out$par #2.842094
out$value #6285.46
log(165*16)-2*(-6285.46)

model_preds_sd2_sfed = fit_ll(2.84, to_fit_sd2, 'raw')
model_acc_sd2_sfed = model_preds_sd2_sfed %>%
  left_join(tasks, by=c('condition', 'batch', 'trial')) %>%
  mutate(correct=pred==answer) %>%
  mutate(total_correct=soft*correct) %>%
  group_by(condition, batch) %>%
  summarise(n=sum(soft), n_acc=sum(total_correct), acc=sum(total_correct)/sum(soft)) %>%
  select(condition, batch, slice_d2=acc)

acc_data_sd2_sfed = acc_data_sd1_sfed %>%
  left_join(model_acc_sd2_sfed, by=c('condition', 'batch'))

model_accs = acc_data_sd2_sfed %>%
  select(condition, batch, ARC, slice_d1, slice_d2) %>%
  gather('model', 'acc', ARC, slice_d1, slice_d2) %>%
  mutate(model=case_when(
    model=='ARC'~'AG',
    model=='slice_d1'~'SO_d1',
    model=='slice_d2'~'SO_d2',
  ))


# Final plot for paper
ggplot(acc_data_sd2_sfed, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  # geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(x=batch, y=acc, color=model, shape=model), size=3, stroke=1.5, data=model_accs)+
  scale_shape_manual(values=c(2, 0, 1)) +
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

#### End of Plots for Experiment 2











