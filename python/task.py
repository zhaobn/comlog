# %%
import math
import random
import pandas as pd

from task_configs import *
from base_classes import Program
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK
from program_lib import Program_lib #,clist_to_df
from program_inf import Gibbs_sampler

class Task_lib(Program_lib):
  def __init__(self, df, dir_alpha=0.1):
    Program_lib.__init__(self, df, dir_alpha)
  def sample_base(self, type, add):
    if type == 'obj':
      color = self.sample_base('color', add)
      shape = self.sample_base('shape', add)
      size = self.sample_base('size', add)
      sampled_props = [color, shape, size]
      stone = 'Stone(' + ','.join([p['terms'] for p in sampled_props]) + ')'
      return {'terms': stone, 'arg_types': '', 'return_type': 'obj', 'type': 'base_term'}
    else:
      bases = self.content.query(f'return_type=="{type}"&type=="base_term"')
      if bases is None or bases.empty:
        print('No base terms found!')
        return self.ERROR_TERM
      else:
        sampled = bases.sample(n=1, weights='count').iloc[0].to_dict()
        if add:
          self.add(sampled)
        return sampled
  def get_all_objs(self):
    stones_df = pd.DataFrame({'terms': []})
    color_df = self.content.query('return_type=="color"&type=="base_term"')
    shape_df = self.content.query('return_type=="shape"&type=="base_term"')
    size_df = self.content.query('return_type=="size"&type=="base_term"')
    for c in range(len(color_df)):
      for s in range(len(shape_df)):
        for z in range(len(size_df)):
          stone_feats = [
            color_df.iloc[c].at['terms'],
            shape_df.iloc[s].at['terms'],
            size_df.iloc[z].at['terms'],
          ]
          counts = [
            color_df.iloc[c].at['count'],
            shape_df.iloc[s].at['count'],
            size_df.iloc[z].at['count'],
          ]
          stones_df = stones_df.append(pd.DataFrame({'terms': [f'Stone({",".join(stone_feats)})'], 'count': [sum(counts)]}), ignore_index=True)
    stones_df['log_prob'] = self.log_dir(list(stones_df['count']))
    return stones_df[['terms', 'log_prob']]

class Task_gibbs(Gibbs_sampler):
  def __init__(self, program_lib, data_list, iteration, inc=True, burnin=0, down_weight=1, iter_start=0, data_start=0):
    Gibbs_sampler.__init__(self, program_lib, data_list, iteration, inc, burnin, down_weight, iter_start, data_start)
  def run(self, type_sig=[['obj', 'obj'], 'obj'], top_n=1, sample=True, base=0, logging=True, save_prefix=''):
    for i in range(self.iter_start, self.iter):
      print(f'Running {i+1}/{self.iter} ({round(100*(i+1)/self.iter, 2)}%):') if logging else None
      data_start = 0 if i > self.iter_start else self.data_start
      if self.inc == 1:
        for j in range(data_start, len(self.data)):
          print(f'---- {j+1}-th out of {len(self.data)} ----') if logging else None
          if i < 1:
            # incrementally
            data = self.data[:(j+1)]
            pms = self.cur_programs
          else:
            # Use full batch
            data = self.data
            # Remove previously-extracted counts
            previous = self.extraction_history[i-1][j]
            if previous is not None:
              pms = pd.merge(self.cur_programs, previous, on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
              pms = pms.fillna(0)
              pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw ranges 0 to 1
              pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count']]
            else:
              pms = self.cur_programs
          pl = Task_lib(pms, self.dir_alpha)
          enumed = pl.bfs(type_sig, 1)
          filtered = pl.filter_program(enumed, data)
          if len(filtered) < 1:
            print('No programs found, filtering again with single input...') if logging else None
            self.filtering_history[i][j] = 0
            filtered = pl.filter_program(enumed, self.data[j])
          else:
            self.filtering_history[i][j] = 1
            padding = len(str(self.iter))
            filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
          extracted = self.extract(filtered, top_n, sample, base)
          print(extracted) if logging else None
          self.extraction_history[i][j] = extracted
          self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
          if len(save_prefix) > 0:
            padding = len(str(self.iter))
            # filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
            pd.DataFrame.from_records(self.filtering_history).to_csv(f'{save_prefix}filter_hist.csv')
            self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
      else: # use full batch
        pms = self.cur_programs
        data = self.data
        pl = Task_lib(pms, self.dir_alpha)
        enumed = pl.bfs(type_sig, 1)
        filtered = pl.filter_program(enumed, data)
        if len(filtered) < 1:
          self.filtering_history[0][i] = 0
          print('No programs found, filtering again with random input...') if logging else None
          rd_idx = random.choice(range(len(data)))
          filtered = pl.filter_program(enumed, self.data[rd_idx])
        else:
          self.filtering_history[0][i] = 1
        extracted = self.extract(filtered, top_n, sample, base)
        print(extracted) if logging else None
        self.extraction_history[0][i] = extracted
        self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}.csv')
          pd.DataFrame.from_records(self.filtering_history).to_csv(f'{save_prefix}filter_hist.csv')
          self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}.csv')
# %%
task_data_df = pd.read_csv('task_data.csv',index_col=0)
task_data = []
for i in range(len(task_data_df)):
  tdata = task_data_df.iloc[i].to_dict()
  task = {
    'agent': eval(tdata['agent']),
    'recipient': eval(tdata['recipient']),
    'result': eval(tdata['result'])
  }
  task_data.append(task)

pm_init = pd.read_csv('data/pm_task.csv',index_col=0,na_filter=False)
g = Task_gibbs(Task_lib(pm_init), task_data, iteration=1000, burnin=0, inc=1)
g.run(save_prefix='task_test/', sample=True, top_n=1)

# # %%
# pm_init = pd.read_csv('data/pm_task.csv',index_col=0,na_filter=False)
# pl.
# t =

# data = {
#   'agent': Stone(White,Triangle,S3),
#   'recipient': Stone(Black,Square,S3),
#   'result': Stone(Black,Square,S4)
# }

# rf = pl.bfs(t,1)
# rt = pl.filter_program(rf,[data])

# # %%
# data_list = [
#   {
#     'agent': Stone(White,Triangle,S3),
#     'recipient': Stone(White,Square,S3),
#     'result': Stone(White,Square,S4)
#   },
#   {
#     'agent': Stone(White,Square,S3),
#     'recipient': Stone(White,Square,S3),
#     'result': Stone(White,Square,S5)
#   },
# ]

# pm_init = pd.read_csv('data/pm_task.csv',index_col=0,na_filter=False)
# g = Task_gibbs(Task_lib(pm_init), data_list, iteration=1, burnin=0, inc=1)
# g.run(save_prefix='task_test', sample=True, top_n=1)

# # filtered = pd.read_csv('tests/composition/phase_1/pm_filtered_1_2.csv', index_col=0, na_filter=False)
# # extracted = g.extract(filtered, 6, False)
# # print(extracted)

# # pms=pd.read_csv('task_test_1_1.csv',index_col=0)
# # pl = Task_lib(pms)
# # enumed = pl.bfs([['obj','obj'],'obj'], 1)
# # filtered = pl.filter_program(enumed, data_list)

# # %%
# x = Stone(White,Square,S4)
# y = Stone(Black,Square,S3)
# z = Program([KK,[setColor,Stone(Black,Square,S3)],Black]).run([x,y])
# z.name

# %% Set up
# pm_task = clist_to_df([
#   White,Black,isWhite,isBlack,
#   Triangle,Square,Pentagon,Hexagon,isTriangle,isSquare,isPentagon,isHexagon,
#   S1,S2,S3,S4,S5,S6,S6,isS1,isS2,isS3,isS4,isS5,isS6,
#   getColor, setColor, eqColor,
#   getShape, setShape, eqShape,
#   getSize, setSize, eqSize,
#   getEdge,setEdge,eqEdge,
#   addVal,mulVal,ifElse,
#   {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
#   True, False, 1,2,3,4,5,6
# ])
# pm_task.to_csv('data/pm_task.csv')
