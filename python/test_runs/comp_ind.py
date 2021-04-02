
# %%
from os import getcwd
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
tdata1_path = '../test_data/comp/training_1.json'
tdata2_path = '../test_data/comp/training_2.json'
gdata_path = '../test_data/comp/gen.json'
run_path = '../test_data/comp/comp_ind/'
N_T_TASK = 15
N_G_TASK = 10
pm_init = pd.read_csv('../data/pm_init.csv', index_col=0, na_filter=False)

# %% Run experiments
with open(tdata1_path) as json_file:
  training_data_1 = [objstr_to_stone(d) for d in json.load(json_file)]

with open(tdata2_path) as json_file:
  training_data_2 = [objstr_to_stone(d) for d in json.load(json_file)]

with open(gdata_path) as json_file:
  gen_data = [objstr_to_stone(d) for d in json.load(json_file)]

# Training
pl_1 = Gibbs_sampler(Program_lib(pm_init), training_data_1, iteration=1000)
pl_1.run(save_prefix=f'{run_path}training_1/pm')

pl_2 = Gibbs_sampler(Program_lib(pm_init), training_data_2, iteration=1000)
pl_2.run(save_prefix=f'{run_path}training_2/pm')

# Prediction
pp = pd.concat([pl_1.cur_programs, pl_2.cur_programs]).groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})
preds = sim_for_all(gen_data, Program_lib(pp), 1000)
preds.to_csv(f'{run_path}preds.csv')

# # %% Generate data
# pl = Program_lib(pm_init)

# training_rule_1 = Program([
#   CS, [
#     SB,
#     [B, ifElse, [C, [B, eqColor, [B, getColor, I]], Red]],
#     [BC, [B, setPattern, I], [B, getPattern, I]]
#   ], I
# ])

# training_rule_2 = Program([
#   CS, [
#     SB,
#     [B, ifElse, [C, [B, eqColor, [B, getColor, I]], Red]],
#     [BC, [B, setPattern, I], [B, getPattern, I]]
#   ], I
# ])

# training_data_1 = []
# def sample_fixed_size(size='S2'):
#   stone = pl.sample_base('obj')['terms']
#   if eval(stone).size.name == size:
#     return stone
#   else:
#     return sample_fixed_size(size)

# for _ in range(N_T_TASK):
#   data = {}
#   data['agent'] = sample_fixed_size()
#   data['recipient'] = sample_fixed_size()
#   data['result'] = training_rule_1.run([eval(data['agent']), eval(data['recipient'])]).name
#   training_data_1.append(data)
# with open(tdata1_path, 'w') as outfile:
#   json.dump(training_data_1, outfile)


# training_data_2 = []
# def sample_excl_red(color='Red'):
#   stone = pl.sample_base('obj')['terms']
#   if eval(stone).color.name == color:
#     return sample_excl_red(color)
#   else:
#     return stone

# for _ in range(N_T_TASK):
#   data = {}
#   data['agent'] = sample_excl_red()
#   data['recipient'] = sample_excl_red()
#   data['result'] = training_rule_1.run([eval(data['agent']), eval(data['recipient'])]).name
#   training_data_2.append(data)
# with open(tdata2_path, 'w') as outfile:
#   json.dump(training_data_2, outfile)

# gen_data = []
# for _ in range(N_G_TASK):
#   data = {}
#   data['agent'] = pl.sample_base('obj')['terms']
#   data['recipient'] = pl.sample_base('obj')['terms']
#   gen_data.append(data)
# with open(gdata_path, 'w') as outfile:
#   json.dump(gen_data, outfile)
