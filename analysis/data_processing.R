

df.tw = df.tw %>%
  mutate(exp=as.numeric(substr(exp, 5,6)))

gen_tasks = df.tw %>%
  select(exp, condition, trial, stripe, dot, block) %>%
  unique()
gen_tasks = gen_tasks %>%
  mutate(
    gt=ifelse(exp%%2==1, stripe*block-dot, dot*block-stripe), 
    alt=ifelse(exp%%2==1, stripe*(block-dot), dot*(block-stripe))
  ) %>%
  mutate(gt=ifelse(gt<0, 0, gt), alt=ifelse(alt<0, 0, alt))

test = df.tw %>%
  left_join(gen_tasks, by=c('exp', 'condition', 'trial', 'stripe', 'dot', 'block'))
