
library(ggridges)
library(ggplot2)
library(dplyr)
library(tidyr)
library(forcats)

rm(list=ls())


#### Experiment 1 data plots ##############################

load('data/exp_1_cleaned.rdata')
load('data/exp_1_coded.Rdata')

# Plot fine-grained self-report match accuracy
labels_2 %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, match, match_a, match_b) %>%
  mutate(
    phase=toupper(substr(phase,7,7)),
    match=case_when(
      match==1 ~ 'perfect',
      match==.5 ~ 'half',
      match==0 ~ 'wrong'
    )) %>%
  mutate(match=factor(match, levels=c('perfect', 'half', 'wrong'))) %>%
  count(condition, phase, match) %>%
  ggplot(aes(x=phase, y=n, fill=match)) +
  geom_bar(stat='identity', color='black', position = position_dodge(preserve="single"), width = 0.7) +
  ylim(0, 60) +
  # scale_fill_manual(values=c('#999999'))
  facet_grid(~condition) +
  theme_bw()

# Plot fine-grained match acc per match type
labels_2 %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, match, match_a, match_b) %>%
  mutate(
    phase=toupper(substr(phase,7,7)),
    match=case_when(
      match==1 ~ 'perfect',
      match==.5 ~ 'half',
      match==0 ~ 'wrong'
    )) %>%
  mutate(
    condition=factor(condition, levels=c('construct', 'combine', 'discern')),
    match=factor(match, levels=c('perfect', 'half', 'wrong'))
  ) %>%
  count(condition, phase, match) %>%
  ggplot(aes(x=phase, y=n, fill=condition)) +
  geom_bar(stat='identity', color='black', position = position_dodge(preserve="single"), width = 0.7) +
  ylim(0, 60) +
  # scale_fill_manual(values=c('#999999'))
  facet_grid(~match) +
  theme_bw()

# Plot with fill
labels_2 %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, match, match_a, match_b) %>%
  mutate(
    phase=toupper(substr(phase,7,7)),
    match=case_when(
      match==1 ~ 'perfect',
      match==.5 ~ 'half',
      match==0 ~ 'wrong'
    )) %>%
  mutate(match=factor(match, levels=c('perfect', 'half', 'wrong'))) %>%
  count(condition, phase, match) %>%
  ggplot(aes(x=phase, y=n, fill=match)) +
  geom_bar(stat='identity', position='fill') +
  # scale_fill_manual(values=c('#999999'))
  facet_grid(~condition) +
  theme_bw()


# Use dot + line plots
match_acc_count = labels_2 %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, match, match_a, match_b) %>%
  mutate(phase=toupper(substr(phase,7,7))) %>%
  count(condition, phase, match)
match_acc_group = labels_2 %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, match, match_a, match_b) %>%
  mutate(phase=toupper(substr(phase,7,7))) %>%
  count(condition, phase) %>%
  rename(total=n)
match_acc_full = expand.grid(
  condition=c('combine','construct','discern'),
  phase=c('A','B'),
  match=c(0, 1, .5),
  default=0)

match_acc_data = match_acc_full %>%
  left_join(match_acc_count, by=c('condition', 'phase', 'match')) %>%
  left_join(match_acc_group, by=c('condition', 'phase')) %>%
  mutate(
    share=n/total,
    match=case_when(
      match==1 ~ 'perfect',
      match==.5 ~ 'half',
      match==0 ~ '-'
    )
  ) %>%
  mutate(
    share=if_else(is.na(share), 0, share),
    condition=factor(condition, levels=c('construct', 'combine', 'discern')),
    match=factor(match, levels=c('perfect', 'half', '-'))
  )

ggplot(match_acc_data, aes(x=phase, y=share, group=match)) +
  geom_line(aes(color=match),linetype="dashed", size=1.2) +
  geom_point(aes(shape=match, color=match), size=3.5) +
  labs(x='', y='', title='Self-report accuracy') +
  scale_color_manual(values=c('#1F78B4', '#A6CEE3', '#A9A9A9')) +
  theme_bw() +
  facet_wrap(~condition)

# Per condition
ggplot(match_acc_data, aes(x=phase, y=share, group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(shape=condition, color=condition), size=3.5) +
  labs(x='', y='', title='Self-report accuracy') +
  theme_bw() +
  facet_wrap(~match)

#### End of Experiment 1 data plots #######################


#### Pilot data plots #####################################
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


#### End of Pilot data plots ###################









