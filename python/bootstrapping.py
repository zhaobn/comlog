
# %%
import pandas as pd
import json
# import sys
# sys.path.append('..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *

# %% Task configs
tdata_path = 'test_data/bootstrapping/training.json'
ldata_path = 'test_data/bootstrapping/learning.json'
gdata_path = 'test_data/bootstrapping/gen.json'
N_T_TASK: 30
N_L_TASK: 5
N_G_TASK: 10

# %% Run experiments
with open(tdata_path) as json_file:
  training_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(ldata_path) as json_file:
  learning_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(gdata_path) as json_file:
  gen_data = [objstr_to_stone(d) for d in json.load(json_file)]

pm_init = pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False)

# Training
pt = Gibbs_sampler(Program_lib(pm_init), training_data, iteration=2)
pt.run(save_prefix='test_data/bootstrapping/training/pm')

# Learning
pl = Gibbs_sampler(Program_lib(pt.cur_programs), learning_data, iteration=2)
pl.run(save_prefix='test_data/bootstrapping/learning/pm')

# Prediction
preds = sim_for_all(gen_data, pl, 3)
preds.to_csv('test_data/bootstrapping/preds.csv')


# %% Generate data
pm_init = pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init)

training_rule = Program([
  CS,[
    SB,[B,
      ifElse,[C,[B,eqColor,[B,getColor,I]],Red]],[SC,
        [BB,setShape,[BC,[B,setSize,I],[B,getSaturation,I]]],
        [B,getShape,I]
      ],
    ],
  I])

learning_rule = Program([
  CS,[
    SB,[B,
      ifElse,[C,[B,eqColor,[B,getColor,I]],Blue]],[SC,
        [BB,setPattern,[BC,[B,setSize,I],[B,getSaturation,I]]],
        [B,getPattern,I]
      ],
    ],
  I])

training_data = []
for _ in range(N_T_TASK):
  data = {}
  data['agent'] = pl.sample_base('obj')['terms']
  data['recipient'] = pl.sample_base('obj')['terms']
  data['result'] = training_rule.run([eval(data['agent']), eval(data['recipient'])]).name
  training_data.append(data)
with open(tdata_path, 'w') as outfile:
  json.dump(training_data, outfile)

learning_data = []
for _ in range(N_L_TASK):
  data = {}
  data['agent'] = pl.sample_base('obj')['terms']
  data['recipient'] = pl.sample_base('obj')['terms']
  data['result'] = learning_rule.run([eval(data['agent']), eval(data['recipient'])]).name
  learning_data.append(data)
with open(ldata_path, 'w') as outfile:
  json.dump(learning_data, outfile)

gen_data = []
for _ in range(N_G_TASK):
  data = {}
  data['agent'] = pl.sample_base('obj')['terms']
  data['recipient'] = pl.sample_base('obj')['terms']
  gen_data.append(data)
with open(gdata_path, 'w') as outfile:
  json.dump(gen_data, outfile)
