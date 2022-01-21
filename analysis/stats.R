
library(dplyr)
library(bruceR)

load('data/exp_1_cleaned.rdata')
load('data/exp_1_coded.Rdata')

# On self-report match
self_report_match = labels %>%
  select(ix, condition, match_a, match_b) %>%
  rename(match1=match_a, match2=match_b)

MANOVA(
  data=self_report_match, 
  dvs="match1:match2", 
  dvs.pattern = "match(.)",
  between='condition', 
  within='match'
) %>%
  # EMMEANS('match', by='condition') %>%
  EMMEANS('condition')


aov(match2 ~ condition, data=self_report_match) %>% summary()
aov(match2 ~ condition, data=self_report_match) %>% summary()

aov(correct ~ condition, data=filter(df.tw, batch=='B')) %>% summary()

df.sw %>%
  group_by(condition) %>%
  summarise(sum(certainty_a)/n(), sd(certainty_a))

df.sw %>%
  group_by(condition) %>%
  summarise(sum(certainty_b)/n(), sd(certainty_b))


# certainty
MANOVA(
  data=select(df.sw, ix, condition, certainty_a, certainty_b),
  dvs="certainty_a:certainty_b", 
  dvs.pattern = "certainty_(.)",
  between='condition', 
  within='certainty_'
) %>%
  # EMMEANS('match', by='condition') %>%
  EMMEANS('condition')





