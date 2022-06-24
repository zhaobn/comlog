
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggridges)

load('../data/all_cleaned.Rdata')
load('../data/fitted_models.Rdata')
answers = read.csv('../data/tasks/answers.csv') %>% select(condition, trial, gt)
fit_results = read.csv('cross_valids/processes.csv') %>% select(-X)
cond_levels=c('construct', 'decon', 'combine', 'flip')

#### Accuracy plot #### 
ppt_cond = df.tw %>% count(condition,batch,trial,prediction)
gen_task = expand.grid(condition=c('combine','construct','decon','flip'),batch=c('A','B'),trial=seq(8),prediction=seq(0,16)) %>%
  arrange(condition, batch, trial, prediction)
ppt_cond = gen_task %>%
  left_join(ppt_cond, by=c('condition','batch','trial','prediction')) %>%
  mutate(n=ifelse(is.na(n),0,n))

answers = read.csv('../data/tasks/answers.csv') %>% select(condition, trial, gt)
answers = rbind(mutate(answers, batch='A'), mutate(answers, batch='B')) %>%
  select(condition, batch, trial, gt)

# People
ppt_accs = ppt_cond %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2))
ppt_se = df.tw %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=gt==prediction) %>%
  group_by(condition, batch) %>%
  summarise(se=sd(acc)/sqrt(n()))
ppt_accs = ppt_accs %>%
  left_join(ppt_se, by=c('condition', 'batch')) %>%
  mutate(
    se=100*se, # in line with percentage
    condition=factor(condition, level=cond_levels),
    batch=ifelse(batch=='A','I','II')
  )


# Model
ag_accs = df.ag %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))
  
agr_accs = df.agr %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

pcfg_accs = df.pcfg %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

model_accs = rbind(
  mutate(ag_accs, model='AG'),
  mutate(agr_accs, model='AG-RJ'),
  mutate(pcfg_accs, model='RatRule')
) %>%
  mutate(condition=factor(condition, levels=cond_levels),
         batch=ifelse(batch=='A','I','II'))



ggplot(ppt_accs, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9), color='gray50') +
  geom_point(
    aes(x=batch, y=accuracy, shape=model, color=model), 
    position = position_jitterdodge(jitter.width = 0.05, jitter.height = 0.5, dodge.width = 0.4),
    size=3, stroke=1.5, data=model_accs) +
  scale_shape_manual(values=c(16, 17, 15)) +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5")) +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
  )



#### Process plot #### 
# patch up
full_iters = fit_results %>%
  filter(model=='PCFG') %>%
  pull(iter) %>%
  unique()
ag_iters = fit_results %>%
  filter(model=='AG') %>%
  pull(iter) %>%
  unique()
ag_batch_iters = setdiff(full_iters, ag_iters)

ag_last_fit = fit_results %>%
  filter(model=='AG', iter==max(ag_iters))
agr_last_fit = fit_results %>%
  filter(model=='AGR', iter==max(ag_iters))

ag_batches = do.call("rbind", replicate(length(ag_batch_iters), ag_last_fit, simplify = FALSE))
ag_batches$iter = ag_batch_iters

agr_batches = do.call("rbind", replicate(length(ag_batch_iters), agr_last_fit, simplify = FALSE))
agr_batches$iter = ag_batch_iters

all_fits = rbind(
  fit_results, ag_batches, agr_batches
)

all_fits %>%
  mutate(model=case_when(model=='AGR'~'AG-RJ', model=='PCFG'~'RatRule', TRUE~model)) %>%
  ggplot(aes(x=iter, y=-fit, color=model)) +
  geom_line() +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5")) +
  theme_bw() +
  labs(y='log likelihood', x='iteration') +
  theme(
    text=element_text(size = 15),
  )


#### Rainbow plot #### 

answers_rb = rbind(mutate(answers, batch='I'), mutate(answers, batch='II')) %>% 
  mutate(prediction=gt,
         trial=as.factor(as.character(trial)),
         condition=factor(condition, levels=cond_levels)) %>%
  select(condition, batch, trial, prediction)


df.agr = df.agr %>% mutate(
  trial=as.factor(as.character(trial)),
  condition=factor(condition, level=cond_levels),
  batch=ifelse(batch=='A','I','II')
)

# df.gpr = gp_preds %>% mutate(
#   trial=as.factor(as.character(trial)),
#   condition=factor(condition, level=cond_levels),
#   batch=ifelse(batch=='A','I','II')
# )


df.tw %>%
  mutate(
    trial=as.factor(as.character(trial)),
    condition=factor(condition, levels=cond_levels),
    batch=ifelse(batch=='A','I','II')
  ) %>%
  ggplot(aes(y=trial, x=prediction, fill=trial)) +
  geom_density_ridges(alpha=0.6, stat="binline", bins=20, scale=0.95) +
  geom_point(data=answers_rb) +
  geom_density_ridges(data=df.agr, aes(height=fitted), stat="identity", alpha=0.4, scale=0.95) +
  #geom_density_ridges(data=df.gpr, aes(height=prob), stat="identity", alpha=0.4, scale=0.95) +
  #scale_x_discrete(limits=c(0,seq(max(df.agr$prediction)))) +
  scale_y_discrete(limits=rev) +
  facet_grid(batch~condition) +
  theme_bw() +
  labs(x='result segment prediction', y='generalization task') +
  theme(
    legend.position = 'none',
    #axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
  )



#### Rule match plot #### 

ppt_pred = df.tw %>%
  filter(batch=='B') %>%
  mutate(
    ground_truth=ifelse(exp_id%%2==1, stripe*block-dot, dot*block-stripe),
    alt=ifelse(exp_id%%2==1, stripe*(block-dot), dot*(block-stripe)),
    subtraction=ifelse(exp_id%%2==1, block-dot, block-stripe),
    mult=ifelse(exp_id%%2==1, stripe*block, dot*block)
  ) %>%
  mutate(
    ground_truth=ifelse(ground_truth<0, 0, ground_truth), 
    alt=ifelse(alt<0, 0, alt),
    subtraction=ifelse(subtraction<0, 0, subtraction), 
    mult=ifelse(mult<0, 0, mult)
  ) %>%
  mutate(
    is_ground_truth=prediction==ground_truth, is_alt=prediction==alt, 
    is_subtraction=prediction==subtraction, is_mult=prediction==mult
  ) %>%
  group_by(condition, ix) %>%
  summarise(
    n=n(), is_ground_truth=sum(is_ground_truth), is_alt=sum(is_alt), 
    is_subtraction=sum(is_subtraction), is_mult=sum(is_mult)
  ) %>%
  mutate(
    pred=ifelse(is_ground_truth>=6, 'ground_truth', 
                ifelse(is_alt>=6, 'alt', 
                       ifelse(is_subtraction>6, 'subtraction', 
                              ifelse(is_mult>6, 'mult', 'other'))))
  ) %>%
  mutate(
    pred=factor(pred, levels=c('ground_truth', 'alt', 'subtraction', 'mult', 'other')),
    condition=factor(condition, levels=c('construct', 'decon', 'combine', 'flip'))
  )

ggplot(ppt_pred, aes(x=condition, fill=pred)) +
  geom_bar(position='fill', color='#888888', size=0.2) +
  theme_bw() +
  labs(x='', y = 'proportion', fill='concept') +
  scale_fill_manual(values=c('#577590', '#277DA1', '#43AA8B', '#90BE6D', '#F9C74F')) +
  theme(
    text=element_text(size = 20),
  )
  























