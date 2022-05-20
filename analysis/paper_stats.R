
library(dplyr)
library(tidyr)

#### Curriculum-order effects ####
cur_accs = df.tw %>% 
  filter(exp_id<3, condition %in% c('construct', 'decon'), batch=='B') %>%
  mutate(acc=(prediction==gt))

cur_accs %>% 
  group_by(condition) %>%
  summarise(acc=sum(acc), n=n(), acc_perc=round(100*(sum(acc)/n()),2))

t.test(
  cur_accs %>% filter(condition=='construct') %>% pull(acc),
  cur_accs %>% filter(condition=='decon') %>% pull(acc)
)


cur_labs = labels %>%
  filter(exp %in% c('exp_1', 'exp_2'), condition %in% c('construct', 'decon')) %>%
  mutate(got_gt=(rule_b=='ground_truth')) 

cur_labs %>%
  group_by(condition) %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))


t.test(
  cur_labs %>% filter(condition=='construct') %>% pull(got_gt),
  cur_labs %>% filter(condition=='decon') %>% pull(got_gt)
)

cur_labs %>%
  filter(rule_a=='mult') %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))



#### Compositions ####
comp_accs = test %>% 
  filter(exp<3, condition %in% c('construct', 'combine'), batch=='B') %>%
  mutate(acc=(prediction==gt))

comp_accs %>% 
  group_by(condition) %>%
  summarise(acc=sum(acc), n=n(), acc_perc=round(100*(sum(acc)/n()),2))

t.test(
  comp_accs %>% filter(condition=='construct') %>% pull(acc),
  comp_accs %>% filter(condition=='combine') %>% pull(acc)
)


comp_labs = labels %>%
  filter(exp %in% c('exp_1', 'exp_2'), condition %in% c('construct', 'combine')) %>%
  mutate(got_gt=(rule_b=='ground_truth')) 

comp_labs %>%
  group_by(condition) %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))

t.test(
  comp_labs %>% filter(condition=='construct') %>% pull(got_gt),
  comp_labs %>% filter(condition=='combine') %>% pull(got_gt)
)

comp_labs %>%
  filter(rule_a=='mult') %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))

labels %>%
  filter(exp %in% c('exp_1', 'exp_2'), condition %in% c('construct', 'combine')) %>%
  mutate(got_gt=(rule_b=='alt')) %>%
  group_by(condition) %>%
  summarise(got_gt=sum(got_gt), n=n(), gt_perc=round(100*(sum(got_gt)/n()),2))


#### Compositions ####
# Code the rules according to generalization predictions
forms_data = test %>%
  filter(exp>2, batch=='B') %>%
  group_by(condition, ix) %>%
  summarise(n=n(), gt=sum(prediction==gt), alt=sum(prediction==alt)) %>%
  mutate(is_gt=(gt>6), is_alt=(alt>6))

forms_data %>%
  group_by(condition) %>%
  summarise(n=n(), is_gt=sum(is_gt), is_alt=sum(is_alt), 
            gt_perc=round(100*sum(is_gt)/n(),2), alt_perc=round(100*sum(is_alt)/n(),2))

t.test(
  forms_data %>% filter(condition=='combine') %>% pull(is_gt),
  forms_data %>% filter(condition=='flip') %>% pull(is_gt),
)

#### Garden path ####
labels = labels %>%
  mutate(rule_cat_b=ifelse(rule_cat_b=='comp', 'complex', rule_cat_b))

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='construct') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='combine') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
  labels %>% filter(condition=='flip') %>% mutate(is_complex=rule_cat_b=='complex') %>% pull(is_complex),
)

labels %>%
  filter(condition=='decon') %>%
  mutate(is_a_complex=rule_cat_a=='complex') %>%
  summarise(n(), sum(is_a_complex), perc=100*sum(is_a_complex)/n())

labels %>%
  mutate(is_mult=ifelse(condition %in% c('combine', 'construct'), rule_cat_a=='mult', rule_cat_b=='mult')) %>%
  group_by(condition) %>%
  summarise(n(), sum(is_mult), perc=100*sum(is_mult)/n())

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_mult=rule_cat_b=='mult') %>% pull(is_mult),
  labels %>% filter(condition=='construct') %>% mutate(is_mult=rule_cat_a=='mult') %>% pull(is_mult),
)

t.test(
  labels %>% filter(condition=='decon') %>% mutate(is_mult=rule_cat_b=='mult') %>% pull(is_mult),
  labels %>% filter(condition=='combine') %>% mutate(is_mult=rule_cat_a=='mult') %>% pull(is_mult),
)

#### GD ####
labels %>%
  filter(condition %in% c('construct', 'combine')) %>%
  mutate(is_add=rule_cat_a=='add_2') %>%
  group_by(condition) %>%
  summarise(n=n(), is_add=sum(is_add), is_add_perc=round(100*sum(is_add)/n(),2))












