
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)

load('../data/exp_1_cleaned.rdata')
read.csv('../data/')

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
construct_a = read.csv('../data/model_preds/exp_1/construct_preds_a.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='construct', batch='A') %>%
  select(condition, batch, trial, pred, prob)
construct_b = read.csv('../data/model_preds/exp_1/construct_preds_b.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='construct', batch='B') %>%
  select(condition, batch, trial, pred, prob)

combine_a = read.csv('../data/model_preds/exp_1/combine_preds_a.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='combine', batch='A') %>%
  select(condition, batch, trial, pred, prob)
combine_b = read.csv('../data/model_preds/exp_1/combine_preds_b.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='combine', batch='B') %>%
  select(condition, batch, trial, pred, prob)

decon_a = read.csv('../data/model_preds/exp_1/prior_preds.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='decon', batch='A') %>%
  select(condition, batch, trial, pred, prob)
decon_b = read.csv('../data/model_preds/exp_1/prior_preds.csv') %>%
  select(pred=terms, starts_with('prob')) %>%
  gather('trial','prob',-pred) %>%
  mutate(trial=as.numeric(substr(trial, 6, 7)), condition='decon', batch='B') %>%
  select(condition, batch, trial, pred, prob)

model_preds = rbind(
  construct_a, construct_b, combine_a, combine_b, decon_a, decon_b
)

tasks = df.tw %>%
  mutate(answer=stripe*block-dot) %>%
  mutate(answer=if_else(answer<0, 0, answer)) %>%
  select(condition, batch, trial, answer) %>%
  unique()

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
  geom_hline(yintercept=0.25, linetype="dashed", color="grey50", size=1) +
  geom_point(aes(y=ARC), stat="identity", shape=6, color='red', size=3, stroke=1.5)+
  facet_grid(~condition) +
  labs(x='', y='') +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white")
  )

# try to fit a softmax
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
# 101*16*log(1/20) # -4841.103
out<-optim(par=6, fn=fit_ll, data=to_fit, method='Brent', lower=0, upper=100)
out$par #2.523922
out$value #6168.963

# Have a look at acc after softmax
model_preds_sfed = fit_ll(2.52, to_fit, 'raw')
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















