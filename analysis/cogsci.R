
library(dplyr)
library(bruceR)
library(ggplot2)
library(ggpubr)


# Basics
mean(df.sw$age)
sd(df.sw$age)

# Bonus
bonus = labels %>%
  select(ix, match_a, match_b) %>%
  mutate(match_a=if_else(match_a>0, 1, 0), match_b=if_else(match_b>0, 1, 0)) %>%
  left_join(df.sw, by='ix') %>%
  select(ix, correct, match_a, match_b) %>%
  mutate(total_bonus=correct*0.02+(match_a+match_b)*0.2)
mean(bonus$total_bonus)
sd(bonus$total_bonus)

# Batch B ground truth rule
labels %>%
  select(ix, condition, rule_cat_b) %>%
  mutate(gt=as.numeric(rule_cat_b=='ground_truth')) %>%
  group_by(condition) %>%
  summarise(gt=sum(gt), n=n(), gt_perc=round(sum(gt)*100/n(),2))


# Gen acc
df.tw %>%
  filter(batch=='A') %>%
  # group_by(condition) %>%
  summarise(correct=sum(correct), n=n(), acc=round(sum(correct)*100/n(),2))
df.tw %>%
  filter(batch=='B') %>%
  group_by(condition) %>%
  summarise(correct=sum(correct), n=n(), acc=round(sum(correct)*100/n(),2))

# Gen acc between con and decon
df.tw %>%
  filter(batch=='B', condition!='combine') %>%
  select(ix, trial, condition, correct)
t.test(filter(df.tw, condition=='construct') %>% pull(correct),
       filter(df.tw, condition=='decon') %>% pull(correct))
# On taskwise??
task_acc = df.tw %>%
  filter(batch=='B') %>%
  select(ix, trial, condition, correct) %>%
  group_by(condition, trial) %>%
  summarise(acc=sum(correct)/n())
t.test(filter(task_acc, condition=='construct') %>% pull(acc),
       filter(task_acc, condition=='decon') %>% pull(acc), paired = TRUE, alt='greater')
t.test(filter(task_acc, condition=='construct') %>% pull(acc),
       filter(task_acc, condition=='combine') %>% pull(acc), paired = TRUE, alt='greater')

# ANOVAs
aov(acc ~ condition, data=task_acc) %>% summary()

task_acc_manova = df.tw %>%
  group_by(condition, batch, trial) %>%
  summarise(acc=round(sum(correct)/n(),2)) %>%
  spread(batch, acc) %>%
  select(condition, trial, acc_a=A, acc_b=B)

MANOVA(
  data=task_acc_manova,
  dvs="acc_a:acc_b", 
  dvs.pattern = "acc_(.)",
  between='condition', 
  within='acc_'
) %>%
  # EMMEANS('match', by='condition') %>%
  EMMEANS('condition')

# ANOVAs
self_report_match = labels %>%
  select(ix, condition, match_a, match_b) %>%
  rename(match1=match_a, match2=match_b)
aov(match2 ~ condition, data=self_report_match) %>% summary()
aov(correct ~ condition, data=filter(df.tw, batch=='B')) %>% summary()

# Try raw acc data
task_raw_manova = df.tw %>%
  select(ix, condition, batch, trial, correct) %>%
  spread(batch, correct) %>%
  select(condition, trial, acc_a=A, acc_b=B)

MANOVA(
  data=task_acc_manova,
  dvs="acc_a:acc_b", 
  dvs.pattern = "acc_(.)",
  between='condition', 
  within='acc_'
) %>%
  # EMMEANS('match', by='condition') %>%
  EMMEANS('condition')


# Garden-pathing
gardening = labels %>%
  mutate(is_mult=if_else(
    (condition=='decon'&rule_cat_b=='mult')|(condition!='decon'&rule_cat_a=='mult'), 1, 0
  )) %>%
  select(ix, condition, rule_cat_a, rule_cat_b, is_mult)

gardening %>%
  group_by(condition) %>%
  summarise(sum(is_mult)/n())

aov(is_mult ~ condition, data=gardening) %>% summary()
t.test(
  gardening %>% filter(condition=='construct') %>% pull(is_mult),
  gardening %>% filter(condition=='decon') %>% pull(is_mult), alt='greater'
)
t.test(
  gardening %>% filter(condition=='combine') %>% pull(is_mult),
  gardening %>% filter(condition=='decon') %>% pull(is_mult)
)


# Certainty
df.sw %>%
  group_by(condition) %>%
  summarise(sum(certainty_a)/n(), sd(certainty_a))
df.sw %>%
  group_by(condition) %>%
  summarise(sum(certainty_b)/n(), sd(certainty_b))

MANOVA(
  data=select(df.sw, ix, condition, certainty_a, certainty_b),
  dvs="certainty_a:certainty_b", 
  dvs.pattern = "certainty_(.)",
  between='condition', 
  within='certainty_'
) %>%
  # EMMEANS('match', by='condition') %>%
  EMMEANS('condition')


# Labels
labels %>%
  filter(condition!='decon', rule_cat_a=='mult') %>%
  select(ix, condition, rule_cat_b) %>%
  mutate(is_mult=as.numeric(rule_cat_b=='ground_truth')) %>%
  group_by(condition) %>%
  summarise(is_mult=sum(is_mult), n=n(), rate=round(sum(is_mult)*100/n(),2))

labels %>%
  filter(condition=='decon') %>%
  select(ix, rule_cat_b) %>%
  mutate(is_mult=as.numeric(rule_cat_b=='mult')) %>%
  summarise(is_mult=sum(is_mult), n=n(), rate=round(sum(is_mult)*100/n(),2))

labels %>%
  filter(condition=='construct') %>%
  summarise(sum(rule_cat_a=='mult')/n())


# Plots
report_acc_strict = labels %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, correct, match_a, match_b) %>%
  mutate(phase=toupper(substr(phase,7,7))) %>%
  mutate(correct=if_else(correct<1, 0, 1)) %>%
  group_by(condition, phase) %>%
  summarise(acc=sum(correct)/n()) %>%
  ggplot(aes(x=phase, y=acc, group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(color=condition, shape=condition), size=3.5) +
  labs(x='', y='', title='Rule acc.') +
  # ylim(0,0.75) +
  theme_bw()+  theme(text = element_text(size = 15))

pred_acc = df.tw %>%
  group_by(batch, condition) %>%
  summarise(acc=sum(correct)/n()) %>%
  ggplot(aes(x=batch,y=acc,group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(color=condition, shape=condition), size=3.5) +
  labs(x='', y='', title='Pred. acc.') +
  # ylim(0,0.75) +
  theme_bw() +  theme(text = element_text(size = 15))


sum_phase=df.sw %>%
  mutate(len_a=str_length(input_a), len_b=str_length(input_b)) %>%
  group_by(condition) %>%
  summarise(certainty_a=mean(certainty_a), certainty_b=mean(certainty_b),
            input_a_length=mean(len_a), input_b_length=mean(len_b))
cert <- sum_phase %>%
  gather(measure, value, certainty_a, certainty_b, input_a_length, input_b_length) %>%
  filter(substr(measure,1,1)=='c') %>%
  mutate(measure=toupper(substr(measure, 11, 11))) %>%
  ggplot(aes(x=measure,y=value,group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(color=condition, shape=condition), size=3.5) +
  labs(x='', y='', title='Certainty') +
  theme_bw() +  theme(text = element_text(size = 15))
len <- sum_phase %>%
  gather(measure, value, certainty_a, certainty_b, input_a_length, input_b_length) %>%
  filter(substr(measure,1,1)=='i') %>%
  mutate(measure=toupper(substr(measure, 7, 7))) %>%
  ggplot(aes(x=measure,y=value,group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(color=condition, shape=condition), size=3.5) +
  labs(x='', y='', title='Input length (nchar)') +
  theme_bw() +
  theme(text = element_text(size = 15))


ggarrange(report_acc_strict, pred_acc, cert, len,
          # labels = c("A", "B", "C"),
          ncol = 2, nrow = 2,
          
          common.legend = TRUE, legend="bottom")


# Output data

labels_output = labels %>%
  select(ix, condition, input_a, label_a=rule_cat_a, input_b, label_b=rule_cat_b, feedback)
write.csv(labels_output, file='../data/cogsci.csv')
















