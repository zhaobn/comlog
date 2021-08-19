
library(ggridges)
library(ggplot2)
library(dplyr)
library(tidyr)
library(forcats)

rm(list=ls())

load('data/pilot_1_cleaned.rdata')

# Plot raws
answers = df.tw %>%
  group_by(trial) %>%
  summarise(stripe=max(stripe), dot=max(dot), block=max(block)) %>%
  mutate(gtruth=stripe*block-dot) %>%
  mutate(prediction=if_else(gtruth<0, 0, gtruth)) %>%
  mutate(trial=as.factor(as.character(trial)))

answers$batch='A'
aa = answers
bb = aa
bb$batch = 'B'
answers = rbind(aa, bb)

df.tw %>%
  mutate(trial=as.factor(as.character(trial))) %>%
  ggplot( aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6) + # stat="binline", bins=20
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(legend.position = 'none')


df.tw %>%
  mutate(trial=as.factor(as.character(trial))) %>%
  ggplot( aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6, stat="binline", bins=20) +
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(legend.position = 'none')


# Plot model preds
preds.combine = read.csv('preds/combine_preds_a.csv')
preds.combine = preds.combine %>%
  filter(substr(terms, 1, 11)=='Stone(S0,O0') %>%
  select(terms, starts_with('prob')) %>%
  gather(trial, value, starts_with('prob')) %>%
  mutate(terms=as.character(terms),
         trial=as.character(trial)) %>%
  mutate(blocks=as.numeric(substr(terms, 14, nchar(terms)-1)),
         trial=as.numeric(substr(trial, 6, nchar(trial)))) %>%
  select(trial, prediction=blocks, prob=value) %>%
  arrange(trial, prediction)

preds.combine %>%
  filter(prob>0) %>%
  mutate(trial=as.factor(as.character(trial))) %>%
  ggplot( aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6, stat="binline", bins=20) +
  scale_x_discrete(limits=factor(c(0,seq(9)))) +
  scale_y_discrete(limits=rev) +
  theme_bw()










