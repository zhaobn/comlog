
library(ggridges)
library(ggplot2)
library(dplyr)
library(tidyr)
library(forcats)
library(networkD3)

rm(list=ls())


# Curious
ggplot(df.sw, aes(x=age, y=correct)) + geom_point() + facet_grid(~condition)


# Debug
x = labels %>%
  select(ix, condition, match_a, match_b) %>%
  gather(phase, correct, match_a, match_b) %>%
  mutate(phase=toupper(substr(phase,7,7)))

#### Experiment 1 Labeles ##############################

load('data/exp_1_cleaned.rdata')
load('data/exp_1_coded.Rdata')

# Plot fine-grained match acc per match type
labels %>%
  select(ix, condition, rule_a, rule_b) %>%
  gather(phase, rule_type, rule_a, rule_b) %>%
  mutate(
    phase=toupper(substr(phase,6,6)),
    condition=factor(condition, levels=c('construct', 'combine', 'decon'))
  ) %>%
  count(condition, phase, rule_type) %>%
  ggplot(aes(x=phase, y=n, fill=rule_type)) +
  # geom_bar(stat='identity', color='black', position = position_dodge(preserve="single"), width = 0.7) +
  geom_bar(stat='identity', position='fill') +
  # scale_fill_manual(values=c('#999999'))
  facet_grid(~condition) +
  theme_bw()

# Use dot + line plots
rule_count = labels %>%
  select(ix, condition, rule_a, rule_b) %>%
  gather(phase, rule_type, rule_a, rule_b) %>%
  mutate(
    phase=toupper(substr(phase,6,6)),
    condition=factor(condition, levels=c('construct', 'combine', 'decon'))
  ) %>%
  count(condition, phase, rule_type)
rule_group = labels %>%
  select(ix, condition, rule_a, rule_b) %>%
  gather(phase, rule_type, rule_a, rule_b) %>%
  mutate(
    phase=toupper(substr(phase,6,6)),
    condition=factor(condition, levels=c('construct', 'combine', 'decon'))
  ) %>%
  count(condition, phase) %>%
  rename(total=n)
rule_full = expand.grid(
  condition=c('combine','construct','decon'),
  phase=c('A','B'),
  rule_type=unique(c(labels$rule_a, labels$rule_b)),
  default=0)

rule_data = rule_full %>%
  left_join(rule_count, by=c('condition', 'phase', 'rule_type')) %>%
  left_join(rule_group, by=c('condition', 'phase')) %>%
  mutate(n=if_else(is.na(n), 0, as.numeric(n))) %>%
  mutate(share=n/total) %>%
  mutate(
    condition=factor(condition, levels=c('construct', 'combine', 'decon')),
    rule_type=factor(rule_type, levels=c(
      "ground_truth",
      "mult",
      "subtraction",
      "add_2",
      "relative",
      "position",
      "parity",
      "nominal",
      "description", 
      "increase",
      "decrease",
      "mix",
      "reverse",  
      "not_sure",
      "incompatible"
    ))
  )

ggplot(rule_data, aes(x=phase, y=share, group=rule_type)) +
  geom_line(aes(color=rule_type),linetype="dashed", size=1.2) +
  geom_point(aes(shape=rule_type, color=rule_type), size=3.5) +
  labs(x='', y='', title='Self-report rules') +
  theme_bw() +
  facet_wrap(~condition)

# Per condition
ggplot(rule_data, aes(x=phase, y=share, group=condition)) +
  geom_line(linetype="dashed") +
  geom_point() +
  labs(x='', y='', title='') +
  scale_y_continuous(breaks=c(0,1)) +
  theme_bw() +
  facet_grid(rule_type~condition, switch = "y") +
  theme(strip.text.y.left = element_text(angle = 0))


# Local change
sum(labels$local_change)/nrow(labels)
labels %>%
  select(ix, condition, local_change) %>%
  group_by(condition) %>%
  summarise(local_change=sum(local_change), n= n())

# Ground truth stats
labels %>%
  group_by(condition) %>%
  summarise(ground_truth=sum(rule_b=='ground_truth'), n=n()) %>%
  mutate(ground_truth_perc=round(100*ground_truth/n,2))

res.aov <- aov(rule_b=='ground_truth' ~ condition, data=labels)
summary(res.aov)
#eta_square
4.632/(4.632+24.616)


labels$total_match=labels$match_a+labels$match_b
boxplot(total_match ~ condition, data = labels,
        xlab = "Treatment", ylab = "match", frame = FALSE)

match.aov <- aov(total_match ~ condition, data=labels)
summary(match.aov)
# eta_square
10.25/(10.25+46.06)


# Look at interesting ones
# Ground truth
rule_data %>%
  filter(rule_type=='ground_truth') %>%
  ggplot(aes(x=phase, y=share, group=condition)) +
  geom_line(aes(color=condition),linetype="dashed", size=1.2) +
  geom_point(aes(shape=condition, color=condition), size=3.5) +
  labs(x='', y='', title='Self-reported ground truth rates') +
  theme_bw()

# Merge some rule types
rule_cat_data = rule_data %>%
  mutate(rule_type=as.character(rule_type)) %>%
  mutate(rule_cat=case_when(
    rule_type %in% c('incompatible', 'not_sure') ~ 'uncertain',
    rule_type %in% c('relative', 'position', 'parity', 'nominal', 'description', 
                     'increase', 'decrease', 'mix', 'reverse') ~ 'complex',
    TRUE ~ rule_type
  )) %>%
  select(-rule_type) %>%
  group_by(condition, phase, rule_cat) %>%
  summarise(n=sum(n), total=max(total)) %>%
  mutate(share=n/total) %>%
  mutate(rule_cat=factor(rule_cat, levels = c(
    'ground_truth', 'mult', 'subtraction', 'add_2', 'complex', 'uncertain'
  )))
  

# A cool one
rule_cat_data %>%
  ggplot(aes(x=phase, y=n, fill=rule_cat)) +
  geom_bar(stat='identity', color='black', position='fill') +
  # geom_bar(stat='identity', color='black', position = position_dodge(preserve="single"), width = 0.7) +
  labs(x='', y='', title='Self-reported rules') +
  theme_bw() +
  facet_grid(~condition) +
  scale_fill_brewer('Paired', direction=-1)


# Try Sankey diagram
links_construct=filter(labels, condition=='construct') %>%
  select(ix, rule_a=rule_cat_a, rule_b=rule_cat_b) %>%
  count(rule_a, rule_b) %>%
  mutate(rule_a_match=paste0('A:', rule_a), rule_b_match=paste0('B:', rule_b))
# Have a look
unique(c(links_construct$rule_a_match, links_construct$rule_b_match))
# Order manually
rules_construct=c(
  "A:mult", "A:add_2", "A:complex", "A:uncertain",
  "B:ground_truth", "B:add_2", "B:complex", "B:uncertain"
)
# Get nodes
nodes_construct=data.frame(
  node=c(0:(length(rules_construct)-1)),
  match_name=rules_construct
)
nodes_construct$name=substr(nodes_construct$match_name, 3, nchar(nodes_construct$match_name))
# Add node refs back to links
links_construct = links_construct %>%
  left_join(select(nodes_construct, rule_a_match=match_name, node), by='rule_a_match') %>%
  rename(source=node) %>%
  left_join(select(nodes_construct, rule_b_match=match_name, node), by='rule_b_match') %>%
  rename(target=node)
# Draw Sankey plot
sankeyNetwork(
  Links=as.data.frame(links_construct), Nodes=nodes_construct,
  Source='source', Target='target', Value='n', NodeID='name',
  fontSize= 15, nodeWidth = 40, fontFamily = 'Helvetica', width=400, height=600
)

# decon
links_decon=filter(labels, condition=='decon') %>%
  select(ix, rule_a=rule_cat_a, rule_b=rule_cat_b) %>%
  count(rule_a, rule_b) %>%
  mutate(rule_a_match=paste0('A:', rule_a), rule_b_match=paste0('B:', rule_b))
# Have a look
unique(c(links_decon$rule_a_match, links_decon$rule_b_match))
# Order manually
rules_decon=c(
  "A:complex", "A:uncertain",
  "B:mult", "B:add_2", "B:complex", "B:uncertain"
)
# Get nodes
nodes_decon=data.frame(
  node=c(0:(length(rules_decon)-1)),
  match_name=rules_decon
)
nodes_decon$name=substr(nodes_decon$match_name, 3, nchar(nodes_decon$match_name))
# Add node refs back to links
links_decon = links_decon %>%
  left_join(select(nodes_decon, rule_a_match=match_name, node), by='rule_a_match') %>%
  rename(source=node) %>%
  left_join(select(nodes_decon, rule_b_match=match_name, node), by='rule_b_match') %>%
  rename(target=node)
# Draw Sankey plot
sankeyNetwork(
  Links=as.data.frame(links_decon), Nodes=nodes_decon,
  Source='source', Target='target', Value='n', NodeID='name',
  fontSize= 15, nodeWidth = 40, fontFamily = 'Helvetica', width=400, height=600
)

# combine
links_combine=filter(labels, condition=='combine') %>%
  select(ix, rule_a=rule_cat_a, rule_b=rule_cat_b) %>%
  count(rule_a, rule_b) %>%
  mutate(rule_a_match=paste0('A:', rule_a), rule_b_match=paste0('B:', rule_b))
# Have a look
unique(c(links_combine$rule_a_match, links_combine$rule_b_match))
# Order manually
rules_combine=c(
  "A:mult",  "A:add_2", "A:complex", "A:uncertain",
  "B:ground_truth", "B:subtraction", "B:add_2", "B:complex"
)
# Get nodes
nodes_combine=data.frame(
  node=c(0:(length(rules_combine)-1)),
  match_name=rules_combine
)
nodes_combine$name=substr(nodes_combine$match_name, 3, nchar(nodes_combine$match_name))
# Add node refs back to links
links_combine = links_combine %>%
  left_join(select(nodes_combine, rule_a_match=match_name, node), by='rule_a_match') %>%
  rename(source=node) %>%
  left_join(select(nodes_combine, rule_b_match=match_name, node), by='rule_b_match') %>%
  rename(target=node)
# Draw Sankey plot
sankeyNetwork(
  Links=as.data.frame(links_combine), Nodes=nodes_combine,
  Source='source', Target='target', Value='n', NodeID='name',
  fontSize= 15, nodeWidth = 40, fontFamily = 'Helvetica', width=400, height=600
)



#### End of Experiment 1 Labels ##############################


#### Experiment 1 raw and model preds #######################
load('data/exp_1_cleaned.rdata')
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
  geom_density_ridges(alpha=0.6, stat="binline", bins=13, scale=0.95) +
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  # facet_grid(batch~condition) +
  facet_grid(condition~batch) +
  theme_bw() +
  theme(legend.position = 'none')


# Plot all model preds
model.preds = data.frame(condition=character(0), phase=character(0), trial=numeric(0), prediction=numeric(0), value=numeric(0))
for (cond in c('construct', 'combine', 'decon')) {
  for (ph in c('a', 'b')) {
    preds = read.csv(paste0('data/model_preds/', cond, '_preds_', ph, '.csv'))
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
model.preds = model.preds %>% 
  mutate(
    trial=as.factor(as.character(trial)),
    # prediction=prediction+1
  ) 


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
  scale_x_discrete(limits=c(0,seq(max(model.preds$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  theme(
    legend.position = 'none',
    axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)
  )
#### End of Experiment 1 raw and model preds #######################


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
  geom_density_ridges(alpha=0.6, stat="binline", bins=13, scale=0.95) +
  geom_point(data=answers) +
  scale_x_discrete(limits=c(0,seq(max(df.tw$prediction)))) +
  scale_y_discrete(limits=rev) +
  # facet_grid(batch~condition) +
  facet_grid(condition~batch) +
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









