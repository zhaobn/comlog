
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
  geom_density_ridges(alpha=0.6, stat="binline", bins=20, scale=0.95) +
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(legend.position = 'none')


# Plot model preds
preds.a = read.csv('preds/combine_preds_a.csv')
preds.a = preds.a %>%
  select(terms, starts_with('prob')) %>%
  gather(trial, value, starts_with('prob')) %>%
  mutate(terms=terms+1,
         trial=as.numeric(substr(trial, 6, nchar(trial))),
         phase='A') %>%
  select(phase, trial, prediction=terms, value) %>%
  arrange(trial, prediction)

preds.b = read.csv('preds/combine_preds_b.csv')
preds.b = preds.b %>%
  select(terms, starts_with('prob')) %>%
  gather(trial, value, starts_with('prob')) %>%
  mutate(terms=terms+1,
         trial=as.numeric(substr(trial, 6, nchar(trial))),
         phase='B') %>%
  select(phase, trial, prediction=terms, value) %>%
  arrange(trial, prediction)

preds.combine = rbind(preds.a, preds.b) %>%
  mutate(trial=as.factor(as.character(trial)))


preds.combine %>%
  ggplot( aes(y=trial, x=prediction, height=value, fill=trial)) +
  geom_density_ridges(stat="identity", alpha=0.6) +
  scale_x_discrete(limits=factor(c(0,seq(9)))) +
  scale_y_discrete(limits=rev) +
  theme_bw() +
  theme(legend.position = 'none') +
  facet_wrap(~phase)







# Not working for now
preds.combine %>%
  mutate(trial=as.factor(as.character(trial)), prob=value) %>%
  ggplot(aes(y=trial, x=prediction, height=stat(prob))) +
  geom_density_ridges(stat = "binline", bins = 20, scale = 0.95, draw_baseline = FALSE) +
  scale_x_discrete(limits=factor(c(0,seq(9)))) +
  scale_y_discrete(limits=rev) +
  theme_bw()




d <- data.frame(
  x = rep(1:5, 3),
  y = c(rep(0, 5), rep(1, 5), rep(2, 5)),
  height = c(0, 1, 3, 4, 0, 1, 2, 3, 5, 4, 0, 5, 4, 4, 1)
)
ggplot(d, aes(x, y, height = height, group = y)) + 
  geom_ridgeline(fill = "lightblue")

preds.combine %>%
  mutate(trial=as.factor(as.character(trial)), height=value) %>%
  ggplot( aes(x=prediction,y=trial, height=height, group=trial)) +
  geom_density_ridges(stat = "identity")

preds.combine = preds.combine %>%
  mutate(trial=as.factor(as.character(trial)), height=value)
ggplot(preds.combine, aes(x=prediction, y=trial, height=stat(value))) +
  geom_density_ridges(stat = "binline", bins = 20, scale = 0.95, draw_baseline = FALSE)




