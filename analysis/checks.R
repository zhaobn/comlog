
library(dplyr)

# Try linear regression as an alternative model
load('../data/raw/exp_1_raw.rdata')
df.tw = df.tw[-c(2)]
learn_data = df.tw %>%
  filter(ix==max(ix), phase=='learn') %>%
  mutate(
    stripe=as.numeric(substr(agent, 2, 2)),
    dot=as.numeric(substr(agent, 4, 4)),
    block=as.numeric(substr(recipient, 6, 6)),
    L=as.numeric(substr(result, 6, 6))
  ) %>%
  select(trial, stripe, dot, block, result=L)

lm(result~stripe+dot+block, data=learn_data)  

lm(result~stripe+dot+block+stripe*dot+stripe*block+dot*block, data=learn_data)  


# Combine Experiment 3 with extra batch data
df.sw.exp3 = df.sw
df.tw.exp3 = df.tw

df.sw.all = rbind(df.sw.exp3, df.sw)
df.tw.all = rbind(df.tw.exp3, df.tw)

df.sw = df.sw.all
df.tw = df.tw.all
save(df.sw, df.tw, file='../data/exp_3_cleaned.rdata')
