library(dplyr)

# PIlot 2 groundtruth alignment analysis
load('../data/pilot_2_cleaned.Rdata')
load('../data/pilot_2_coded.Rdata')

# First look
df.tw %>%
  filter(batch=='B') %>%
  group_by(ix) %>%
  summarise(total=n(), gt=sum(gt_correct), other=sum(alt_correct))
  
# Accuracy


# Strategies



# Labels







