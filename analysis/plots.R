
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
  geom_density_ridges(alpha=0.6, stat="binline", bins=20, scale=0.95) +
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(legend.position = 'none')


# Plot all model preds
model.preds = data.frame(condition=character(0), phase=character(0), trial=numeric(0), prediction=numeric(0), value=numeric(0))
for (cond in c('construct', 'combine', 'discern')) {
  for (ph in c('a', 'b')) {
    preds = read.csv(paste0('preds/', cond, '_preds_', ph, '.csv'))
    preds_fmt = preds %>%
      select(terms, starts_with('prob')) %>%
      gather(trial, value, starts_with('prob')) %>%
      mutate(
        condition=cond,
        terms=terms,
        trial=as.numeric(substr(trial, 6, nchar(trial))),
        batch=toupper(ph)) %>%
      select(condition, batch, trial, prediction=terms, value)
    model.preds = rbind(model.preds, preds_fmt)
  }
}
model.preds = model.preds %>% mutate(trial=as.factor(as.character(trial))) 

model.answers = answers %>%
  mutate(prediction=prediction+1, value=0)

model.preds %>%
  ggplot(aes(y=trial, x=prediction, height=value, fill=trial)) +
  geom_density_ridges(stat="identity", alpha=0.6) +
  geom_point(data=model.answers) +
  scale_x_discrete(limits=factor(c(0,seq(9)))) +
  scale_y_discrete(limits=rev) +
  theme_bw() +
  theme(legend.position = 'none') +
  facet_wrap(batch~condition)
  

# Plot together
df.tw %>%
  mutate(trial=as.factor(as.character(trial))) %>%
  ggplot( aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6, stat="binline", bins=20, scale=0.95) +
  geom_point(data=answers) +
  geom_density_ridges(data=model.preds, aes(height=value), stat="identity", alpha=0.4, scale=0.95) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(legend.position = 'none')






