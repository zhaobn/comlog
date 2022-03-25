
library(dplyr)
library(ggplot2)

# Try single heatmap
load('../../data/exp_1_cleaned.rdata')
all_terms = expand.grid(
  condition=c('construct', 'combine', 'decon'),
  phase=c('A', 'B'),
  trial=seq(8),
  term=c(0, seq(16))
)

ppts = df.tw %>%
  group_by(condition, batch, trial, prediction) %>%
  summarise(n=n()) %>%
  mutate(freq=n/sum(n)) %>%
  select(condition, phase=batch, trial, term=prediction, value=freq) %>%
  right_join(all_terms, by=c('condition', 'phase', 'trial', 'term')) %>%
  mutate(value=ifelse(is.na(value), 0, value), model='prolifc') %>%
  arrange(condition, phase, trial, term)

ggplot(ppts, aes(x=term, y=trial, fill=value)) +
  geom_tile() +
  scale_y_continuous(trans = "reverse", breaks = seq(8)) +
  scale_fill_gradient(low="white", high="black") +
  facet_grid(phase~condition)
  







