
library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)
library(ggridges)

load('../data/all_cleaned.Rdata')
load('../data/fitted_models.Rdata')

fit_results = read.csv('cross_valids/processes.csv') %>% select(-X)
cond_levels=c('construct', 'decon', 'combine', 'flip')

answers = read.csv('../data/tasks/answers.csv') %>% select(condition, trial, gt)
answers = rbind(mutate(answers, batch='A'), mutate(answers, batch='B')) %>%
  select(condition, batch, trial, gt)

#### Accuracy plot #### 
ppt_cond = df.tw %>% count(condition,batch,trial,prediction)
gen_task = expand.grid(condition=c('combine','construct','decon','flip'),batch=c('A','B'),trial=seq(8),prediction=seq(0,16)) %>%
  arrange(condition, batch, trial, prediction)
ppt_cond = gen_task %>%
  left_join(ppt_cond, by=c('condition','batch','trial','prediction')) %>%
  mutate(n=ifelse(is.na(n),0,n))

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

rr_accs = df.rr %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

rrr_accs = df.rrr %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

model_accs = rbind(
  mutate(ag_accs, model='AG'),
  mutate(agr_accs, model='AGR'),
  mutate(rr_accs, model='RR'),
  #mutate(rrr_accs, model='RRR'),
) %>%
  mutate(condition=factor(condition, levels=cond_levels),
         batch=ifelse(batch=='A','I','II'),
         model=factor(model, levels=c('AGR','AG','RR')))



ggplot(ppt_accs, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9), color='#116466') +
  geom_point(
    aes(x=batch, y=accuracy, shape=model, color=model), 
    position = position_jitterdodge(jitter.width = 0.05, jitter.height = 0.5, dodge.width = 0.4),
    size=5, stroke=1.5, data=model_accs) +
  scale_shape_manual(values=c(16, 17, 15, 18)) +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5")) +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position = 'right',
      #legend.position=c(.9,.9),
      strip.background = element_blank(),
      panel.grid.minor = element_blank(),
      text = element_text(size = 25)) +
  facet_wrap(~condition, nrow=2)



#### Accuracy plot with alternative models #### 
load('../data/alter_fitted.Rdata')

sim_accs = df.sim %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

lm_accs = df.lm %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

mm_accs = df.mm %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

gp_accs = df.gp %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))

rand_accs = df.gp %>%
  mutate(fitted=1/17) %>%
  left_join(answers, by=c('condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction)) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*fitted)/sum(fitted),2))


all_models = c('AGR', 'AG', 'RR', 'Similarity', 'GpReg', 'LinReg', 'Multinom')

model_accs = rbind(
  mutate(agr_accs, model='AGR'),
  mutate(ag_accs, model='AG'),
  mutate(rr_accs, model='RR'),
  #mutate(rrr_accs, model='RRR'),
  mutate(sim_accs, model='Similarity'),
  mutate(lm_accs, model='LinReg'),
  mutate(mm_accs, model='Multinom'),
  mutate(gp_accs, model='GpReg'),
  #mutate(rand_accs, model='Random'),
) %>%
  mutate(condition=factor(condition, levels=cond_levels),
         model=factor(model, levels=all_models),
         batch=ifelse(batch=='A','I','II')) %>%
  filter(model %in% c('AGR', 'AG', 'RR'))

ggplot(ppt_accs, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9)) +
  geom_hline(yintercept=1/17*100, linetype='dashed', color='green', size=2) +
  geom_point(
    aes(x=batch, y=accuracy, shape=model, color=model), 
    position = position_jitterdodge(jitter.width = 0.1, jitter.height = 0.5, dodge.width = 0.4),
    size=5, stroke=1.5, data=model_accs) +
  scale_shape_manual(values=c(16, 17, 15, rep(20,length(all_models)-3))) +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5", rep('#808080',length(all_models)-3))) +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    legend.position='bottom',
    text=element_text(size = 25),
    strip.background =element_rect(fill="white", colour='white'),
  )


#### Plot for presentation #### 
ppt_accs_plot = ppt_accs %>% filter(condition!='flip')
model_accs_plot = model_accs %>% 
  filter(condition!='flip') %>%
  mutate(model=as.character(model)) %>%
  mutate(model=ifelse(model=='Standard', 'Unbounded', model)) %>%
  mutate(model=factor(model, levels=c('AG', 'AGR', 'Unbounded', 'Similarity', 'GPR', 'LinReg', 'Multimon')))

ggplot(data=ppt_accs_plot, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9)) +
  geom_hline(yintercept=1/17*100, linetype='dashed', color='green', size=2) +
  geom_point(
    aes(x=batch, y=accuracy, shape=model, color=model,alpha=model),
    position = position_jitterdodge(jitter.width = 0.1, jitter.height = 0.5, dodge.width = 0.4),
    size=5, stroke=1.5, data=model_accs_plot) +
  scale_shape_manual(values=c(16, 17, 15, rep(20,length(all_models)-3))) +
  scale_color_manual(values=c("#cc0000", "#f1c232", "#63ace5", rep('#808080',length(all_models)-3))) +
  scale_alpha_manual(values=c(1,1,1,rep(1,length(all_models)-3))) +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    text=element_text(size = 25),
    strip.background =element_rect(fill="white", colour='white'),
  )

#### Acc fit plot #### 
diag_accs = ppt_accs %>%
  mutate(ppt=accuracy) %>%
  select(condition, batch, ppt) %>%
  right_join(model_accs, by=c('condition', 'batch')) %>%
  mutate(index=paste0(condition, '-', batch)) %>%
  mutate(model=factor(model, levels=c('AGR','AG','RR','GpReg','Similarity','Multinom','LinReg'))) %>%
  filter(model %in% c('GpReg','Similarity','Multinom','LinReg'))

ggplot(diag_accs, aes(x=accuracy, y=ppt)) +
  geom_point() +
  geom_smooth(method='lm', formula= y~x, fill = "lightgray") +
  stat_cor(aes(label = ..r.label..), label.x = 9, label.y = 54) + # x 36
  facet_wrap(~model, nrow=1) +
  labs(x='model', y='people') +
  scale_y_continuous(labels=function(x) x/100) +
  scale_x_continuous(labels=function(x) x/100) +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position=c(.07,.87),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 20))

#### NLL Improvement ####
fits_all = read.csv(file='../data/fits_all.csv') %>%
  filter(model != 'RRR')
baseline_stats = df.tw %>% 
  count(condition) %>% 
  mutate(baseline=n*log(1/17)) %>% select(-n)

fits_all %>% group_by(model, condition) %>%
  summarise(nll=sum(nll)) %>%
  left_join(baseline_stats, by='condition') %>%
  mutate(improv=round(nll-baseline)) %>%
  mutate(condition=ifelse(condition=='decon', 'de-construct', condition)) %>%
  mutate(condition=factor(condition, levels=c("construct", 'de-construct', 'combine', 'flip'))) %>%
  ggplot(aes(x=reorder(model, -nll), y=improv, fill=condition)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(
    aes(label = paste0('+', after_stat(y)), group = model), 
    stat = 'summary', fun = sum, vjust = -1
  ) +
  theme_bw() +
  labs(x='', y='') +
  scale_fill_brewer(palette="Blues", direction=-1) +
  theme(legend.title=element_blank(),
        legend.position=c(.75,.9),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 20),
        axis.text.x = element_text(angle = 45, vjust = 0.5, hjust=.5))
  




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
  #facet_grid(condition~batch) +
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
  

#### New plots ####

ppt_cond = df.tw %>% count(exp_id,condition,batch,trial,prediction)
gen_task = expand.grid(exp_id=seq(4),condition=c('combine','construct','decon','flip'),batch=c('A','B'),trial=seq(8),prediction=seq(0,16)) %>%
  arrange(exp_id, condition, batch, trial, prediction)
ppt_cond = gen_task %>%
  left_join(ppt_cond, by=c('exp_id', 'condition','batch','trial','prediction')) %>%
  mutate(n=ifelse(is.na(n),0,n))

answers = read.csv('../data/tasks/answers.csv') %>% select(exp_id, condition, trial, gt)
answers = rbind(mutate(answers, batch='A'), mutate(answers, batch='B')) %>%
  select(exp_id, condition, batch, trial, gt)

# People
ppt_accs = ppt_cond %>%
  left_join(answers, by=c('exp_id', 'condition', 'batch', 'trial')) %>%
  mutate(acc=(gt==prediction))

exp_1_accs = ppt_accs %>%
  filter(exp_id==1, condition != 'flip') %>%
  group_by(exp_id, condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>% ungroup() %>%
  mutate(exp_label='1') %>%
  select(exp_label, condition, batch, accuracy, se)
exp_2_accs = ppt_accs %>%
  filter(exp_id==2, condition != 'flip') %>%
  group_by(exp_id, condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>%  ungroup() %>%
  mutate(exp_label='2') %>%
  select(exp_label, condition, batch, accuracy, se)
exp_cur_accs = ppt_accs %>%
  filter(exp_id<3, condition != 'flip') %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>% ungroup() %>%
  mutate(exp_label='cur') %>%
  select(exp_label, condition, batch, accuracy, se)

exp_3_accs = ppt_accs %>%
  filter(exp_id==3, condition %in% c('combine', 'flip')) %>%
  group_by(exp_id, condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>% ungroup() %>%
  mutate(exp_label='3') %>%
  select(exp_label, condition, batch, accuracy, se)
exp_4_accs = ppt_accs %>%
  filter(exp_id==4, condition %in% c('combine', 'flip')) %>%
  group_by(exp_id, condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>% ungroup() %>%
  mutate(exp_label='4') %>%
  select(exp_label, condition, batch, accuracy, se)
exp_com_accs = ppt_accs %>%
  filter(exp_id>2, condition %in% c('combine', 'flip')) %>%
  group_by(condition, batch) %>%
  summarise(accuracy=round(100*sum(acc*n)/sum(n),2), se=sd(acc)/sqrt(n())) %>% ungroup() %>%
  mutate(exp_label='com') %>%
  select(exp_label, condition, batch, accuracy, se)

ppt_agg = rbind(exp_1_accs, exp_2_accs, exp_3_accs, exp_4_accs, exp_cur_accs, exp_com_accs) %>%
  mutate(exp_label=factor(exp_label, levels=c('1','2','cur','3','4','com')),
         se=100*se, # in line with percentage
         condition=factor(condition, level=cond_levels),
         batch=ifelse(batch=='A','I','II'))

ggplot(ppt_agg, aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9), color='gray50') +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
    panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
    panel.background = element_blank(), axis.line = element_line(colour = "black"),
    panel.spacing.y = unit(2, "lines")
  ) +
  facet_grid(exp_label~condition)



rbind(exp_1_accs, exp_2_accs, exp_cur_accs) %>%
  mutate(exp_label=factor(exp_label, levels=c('1','2','cur')),
         se=100*se, # in line with percentage
         condition=factor(condition, level=c('construct','decon','combine')),
         batch=ifelse(batch=='A','I','II')) %>%
  ggplot(aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9), color='gray50') +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
    panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
    panel.background = element_blank(), axis.line = element_line(colour = "black"),
    panel.spacing.y = unit(2, "lines")
  ) +
  facet_grid(exp_label~condition)


rbind(exp_3_accs, exp_4_accs, exp_com_accs) %>%
  mutate(exp_label=factor(exp_label, levels=c('3','4','com')),
         se=100*se, # in line with percentage
         condition=factor(condition, level=c('combine', 'flip')),
         batch=ifelse(batch=='A','I','II')) %>%
  ggplot(aes(x=batch, y=accuracy)) +
  geom_bar(stat='identity', fill='black') +
  facet_grid(~condition) +
  geom_errorbar(aes(ymin=accuracy-se, ymax=accuracy+se), width=.2, position=position_dodge(.9), color='gray50') +
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x, '%')) +
  theme_bw() +
  theme(
    text=element_text(size = 15),
    strip.background =element_rect(fill="white", colour='white'),
    panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
    panel.background = element_blank(), axis.line = element_line(colour = "black"),
    panel.spacing.y = unit(2, "lines")
  ) +
  facet_grid(exp_label~condition)


#### New plots Neil suggested ####

answers = read.csv('../data/tasks/answers.csv') %>% select(exp_id, condition, trial, gt)
answers = rbind(mutate(answers, batch='A'), mutate(answers, batch='B')) %>%
  select(exp_id, condition, batch, trial, gt)

# Accuracy per participant
ind_acc = df.tw %>%
  left_join(answers, by=c('exp_id', 'condition', 'batch', 'trial')) %>%
  mutate(acc=(prediction==gt)*100, 
         batch=ifelse(batch=='A', 'I', 'II'),
         condition=ifelse(condition=='decon', 'de-construct', condition),
         condition=factor(condition, levels=c('construct','de-construct','combine','flip'))) %>%
  group_by(exp_id, ix, condition, batch) %>%
  summarise(acc=sum(acc)/n())

agg_stat = ind_acc %>%
  group_by(exp_id, condition, batch) %>%
  summarise(se=sd(acc)/sqrt(n()), acc=sum(acc)/n())

agg_stat %>%
  filter(exp_id < 3) %>%
  mutate(exp_id=paste0('Exp ', as.character(exp_id))) %>%
  ggplot(aes(x=batch, y=acc, fill=exp_id)) +
  geom_bar(position='dodge', stat='identity') +
  #geom_jitter(data=filter(ind_acc, exp_id < 3), aes(x=batch, y=acc), alpha=.5, size=.5, color='#116466', fill='white', shape=21) +
  geom_errorbar(aes(ymin=acc-se, ymax=acc+se), width=.2, position=position_dodge(.9), color='#116466') +
  scale_fill_manual(values=c("black", "#9E9E9E")) +
  facet_grid(~condition)+
  labs(x='', y='accuracy') +
  scale_y_continuous(labels=function(x) paste0(x,"%")) +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position=c(.07,.87),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 25))
  

agg_stat %>%
  filter(exp_id > 2) %>%
  mutate(exp_id=paste0('Exp ', as.character(exp_id))) %>%
  ggplot(aes(x=batch, y=acc, fill=exp_id)) +
  geom_bar(position='dodge', stat='identity') +
  #geom_jitter(data=filter(ind_acc, exp_id > 2), aes(x=batch, y=acc), alpha=.5, size=.5, color='#116466', fill='white', shape=21) +
  geom_errorbar(aes(ymin=acc-se, ymax=acc+se), width=.2, position=position_dodge(.9), color='#116466') +
  scale_fill_manual(values=c("black", "#9E9E9E")) +
  facet_grid(~condition)+
  labs(x='', y='') +
  scale_y_continuous(labels=function(x) paste0(x,"%")) +
  theme_bw() +
  theme(legend.title=element_blank(),
        legend.position=c(.1,.87),
        strip.background = element_blank(),
        panel.grid.minor = element_blank(),
        text = element_text(size = 25))

#### Model fit results ####

fits = read.csv('cross_valids/sum.csv') %>% select(-X)

fits_long = fits %>% 
  gather('cond', 'value', -model) %>%
  filter(cond!='overall')

ggplot(fits_long, aes(x=model, y=value, fill=cond)) +
  geom_bar(position="stack", stat="identity")

# improvement
fits %>% 
  select(model, overall) %>%
  mutate(impro=fits$overall[8]-overall) %>%
  ggplot(aes(x=model, y=impro)) +
    geom_bar(stat='identity')

































