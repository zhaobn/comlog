
# %%
from numpy.random import normal
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from helpers import term_to_dict, normalize, softmax

# %% Test program generation
def clist_to_df(clist):
  df = pd.DataFrame({
    'terms': [],
    'arg_types': [],
    'return_type': [],
    'type': [],
    'count': [],
  })
  for et in secure_list(clist):
    if isinstance(et, dict) == 0:
      et = term_to_dict(et)
    df = df.append(pd.DataFrame({
      'terms': [et['terms']],
      'arg_types': [et['arg_types']],
      'return_type': [et['return_type']],
      'type': [et['type']],
      'count': [0]
    }), ignore_index=True)
  return df.groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})

pm_init = clist_to_df([
  getColor, setColor, eqColor,
  getSaturation, setSaturation, eqSaturation,
  getShape, setShape, eqShape,
  getSize, setSize, eqSize,
  getPattern, setPattern, eqPattern,
  getDensity, setDensity, eqDensity,
  eqObject, ifElse,
  {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
  True, False,
  Red, Yellow, #Blue,
  Square, Triangle, #Circle,
  Dotted, Plain, #Stripy, Checkered,
  S1, S2, #S3, S4,
])

pm_init.to_csv('data/pm_init_cut.csv')

# %%
pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init, 0.1)
t = [['obj', 'obj'], 'obj']
pl.generate_program(t)
rf = pl.bfs(t,1)
rf

# %%
data_list = [
  {
    'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
    'recipient': Stone(Yellow,S1,Square,S2,Dotted,S2),
    'result': Stone(Red,S1,Square,S1,Dotted,S2)
  },
  {
    'agent': Stone(Yellow,S2,Square,S2,Dotted,S1),
    'recipient': Stone(Red,S1,Triangle,S1,Plain,S2),
    'result': Stone(Yellow,S1,Triangle,S2,Plain,S2)
  },
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Yellow,S2,Square,S1,Dotted,S1),
    'result': Stone(Yellow,S2,Square,S2,Dotted,S1)
  },
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
    'result': Stone(Yellow,S1,Triangle,S2,Plain,S1)
  },
]

pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)
x = Gibbs_sampler(Program_lib(pm_init), data_list, iteration=5, burnin=0)
x.run()

# %%
post_lib = pd.read_csv('data/test.csv', index_col=0, na_filter=False)
pl = Program_lib(post_lib)

data = {
  'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
  'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
}

def get_pred(program_lib, partial_data, depth=3, type_sig=[['obj', 'obj'], 'obj']):
  pm_info = program_lib.generate_program(type_sig,max_step=depth)
  if 'ERROR' in pm_info['terms']:
    return None
  else:
    pm = Program(eval(pm_info['terms']))
    return pm.run([partial_data['agent'], partial_data['recipient']])
# get_pred(pl, data)

def sim_preds(partial_data, program_lib, n, softmax_base=0):
  ret_df = program_lib.get_all_objs()[['terms']]
  ret_df['count'] = 0
  for _ in range(n):
    result = get_pred(program_lib, partial_data)
    if result is not None:
      found_index = ret_df[ret_df['terms']==result.name].index.values[0]
      ret_df.at[found_index, 'count'] += 1
  ret_df['prob'] = normalize(ret_df['count']) if softmax_base == 0 else softmax(ret_df['count'], softmax_base)
  return ret_df
# sim_preds(data, pl, 100)

def sim_for_all(data_list, program_lib, n, softmax_base=0):
  ret_df = ret_df = program_lib.get_all_objs()[['terms']]
  for i in range(len(data_list)):
    preds = sim_preds(data_list[i], program_lib, n, softmax_base)
    preds = preds.rename(columns={"count": f"count_{i+1}", "prob": f"prob_{i+1}"})
    ret_df = pd.merge(ret_df, preds, on='terms', how='left')
  return ret_df


sim_for_all([
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Yellow,S2,Square,S1,Dotted,S1)
  },
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
  },
], pl, 5)
