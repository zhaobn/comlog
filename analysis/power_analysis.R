
# Packages
library(dplyr)
library(googlesheets4)

# Data
load('../data/pilot_1_cleaned.rdata')
labels = read_sheet("https://docs.google.com/spreadsheets/d/1xmfK-JrVznHkPfKPoicelXOW5Mj252G2TtY6O9PP2tM/edit#gid=1386715201")
labels = labels  %>%
  mutate(condition=case_when(condition=='comp_const'~'combine', 
                             condition=='comp_mult'~'construct', 
                             condition=='comp_mult_reverse'~'discern'))

# Pull out measures for analysis
self_report_acc = labels %>%
  mutate(acc = input_a_correct+input_b_correct,
         condition=factor(condition)) %>%
  select(ix, condition, acc)
  
# Check assumptions
group_by(self_report_acc, condition) %>%
  summarise(
    count = n(),
    mean = mean(acc, na.rm = TRUE),
    sd = sd(acc, na.rm = TRUE)
  )

boxplot(acc ~ condition, data = self_report_acc,
        xlab = "Treatment", ylab = "acc",
        frame = FALSE, col = c("#00AFBB", "#E7B800", "#FC4E07"))

# One-way ANOVA
res.aov <- aov(acc ~ condition, data = self_report_acc)
summary(res.aov)

sd(self_report_acc$acc)
# Effect size f: 0.3114
# with alpha 0.05, beta 0.95 => Total sample size 165


load('../data/raw/pilot_1_raw.rdata')
colnames(df.tw)[2] <- 'pid'
tdata = df.tw %>% 
  filter(phase=='gen') %>%
  select(ix, batch, trial, correct)
cond_data = df.sw %>% select(ix, condition)
tdata_extended = tdata %>% left_join(cond_data, by='ix')

tdata_extended %>%
  group_by(condition, ix) %>%
  summarise(acc=sum(correct)) %>%
  group_by(condition) %>%
  summarise(n=n(), acc=sum(acc)/(n()*8))
  









