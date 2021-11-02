
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













