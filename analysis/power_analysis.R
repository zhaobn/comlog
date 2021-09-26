
# Packages
library(dplyr)
library(googlesheets4)

# Data
load('data/pilot_1_cleaned.rdata')
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




