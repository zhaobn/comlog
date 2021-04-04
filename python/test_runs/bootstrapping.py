
# %%
import pandas as pd
import json
import sys
sys.path.append('..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *

# %% Task configs
main_path = '../test_data/bootstrapping/'
tdata_path = main_path + 'training.json'
ldata_path = main_path + 'learning.json'
gdata_path = main_path + 'gen.json'
N_T_TASK = 30
N_L_TASK = 5
N_G_TASK = 10
# pm_init = pd.read_csv('../data/pm_init.csv', index_col=0, na_filter=False)

# %% Run experiments
with open(tdata_path) as json_file:
  training_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(ldata_path) as json_file:
  learning_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(gdata_path) as json_file:
  gen_data = [objstr_to_stone(d) for d in json.load(json_file)]

# Training
pm_init = pd.read_csv(f'{main_path}/training/pm_00002_00030.csv', index_col=0, na_filter=False)
pt = Gibbs_sampler(Program_lib(pm_init), training_data, iteration=10000, iter_start=1, data_start=29)
pt.run(save_prefix=f'{main_path}training/pm')

# %%
# Learning
pl = Gibbs_sampler(Program_lib(pt.cur_programs), learning_data, iteration=10000)
pl.run(save_prefix=f'{main_path}learning/pm')

# Prediction
preds = sim_for_all(gen_data, Program_lib(pl.cur_programs), 10000)
preds.to_csv(f'{main_path}preds.csv')


# # %% Generate data
# pl = Program_lib(pm_init)

# training_rule = Program([
#   CS,[
#     SB,[B,
#       ifElse,[C,[B,eqColor,[B,getColor,I]],Red]],[SC,
#         [BB,setShape,[BC,[B,setSize,I],[B,getSaturation,I]]],
#         [B,getShape,I]
#       ],
#     ],
#   I])

# learning_rule = Program([
#   CS,[
#     SB,[B,
#       ifElse,[C,[B,eqColor,[B,getColor,I]],Blue]],[SC,
#         [BB,setPattern,[BC,[B,setSize,I],[B,getSaturation,I]]],
#         [B,getPattern,I]
#       ],
#     ],
#   I])

# training_data = []
# for _ in range(N_T_TASK):
#   data = {}
#   data['agent'] = pl.sample_base('obj')['terms']
#   data['recipient'] = pl.sample_base('obj')['terms']
#   data['result'] = training_rule.run([eval(data['agent']), eval(data['recipient'])]).name
#   training_data.append(data)
# with open(tdata_path, 'w') as outfile:
#   json.dump(training_data, outfile)

# learning_data = []
# for _ in range(N_L_TASK):
#   data = {}
#   data['agent'] = pl.sample_base('obj')['terms']
#   data['recipient'] = pl.sample_base('obj')['terms']
#   data['result'] = learning_rule.run([eval(data['agent']), eval(data['recipient'])]).name
#   learning_data.append(data)
# with open(ldata_path, 'w') as outfile:
#   json.dump(learning_data, outfile)

# gen_data = []
# for _ in range(N_G_TASK):
#   data = {}
#   data['agent'] = pl.sample_base('obj')['terms']
#   data['recipient'] = pl.sample_base('obj')['terms']
#   gen_data.append(data)
# with open(gdata_path, 'w') as outfile:
#   json.dump(gen_data, outfile)

# %%
with open(tdata_path) as json_file:
  training_data = json.load(json_file)
  # training_data = [objstr_to_stone(d) for d in json.load(json_file)]

# %%
