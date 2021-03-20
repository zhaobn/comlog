
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from program_generator import Program_lib

# %% Basic setup
pms = pd.read_csv('data/rc_cp.csv', index_col=0)

pl = Program_lib(
  program_list=[
    getColor, setColor, eqColor,
    getSaturation, setSaturation, eqSaturation,
    getShape, setShape, eqShape,
    getSize, setSize, eqSize,
    getPattern, setPattern, eqPattern,
    getDensity, setDensity, eqDensity,
    eqObject, ifElse, {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'}
   ],
  base_list=[
    True, False,
    Red, Yellow, Blue,
    Square, Triangle, Circle,
    Dotted, Plain,
    S1, S3, S3, S4
  ])

base_df = pl.base_terms
programs_df = pl.content

base_index =

# %%
def extract_programs(terms, base_df, programs_df):
  if isinstance(terms, str):
    terms = eval(terms)
  for t in terms:
    if isinstance(t, bool) != 1:
      if t.ctype in pl.SET_MARKERS:
        base_df.at[base_df[base_df.terms==t].index.values[0], 'count'] += 1
      # elif c.type == 'obj':
      #   base_df.at[base_df[base_df.terms==t].index.values[0], 'count'] += 1
  return base_df

# %%
pl = Program_lib(
  program_list=[
    getColor, setColor, eqColor,
    getSaturation, setSaturation, eqSaturation,
    getShape, setShape, eqShape,
    getSize, setSize, eqSize,
    getPattern, setPattern, eqPattern,
    getDensity, setDensity, eqDensity,
    eqObject, ifElse, {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'}
   ],
  base_list=[
    True, False,
    Red, Yellow, Blue,
    Square, Triangle, Circle,
    Dotted, Plain,
    S1, S3, S3, S4
  ])

data = {
  'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
  'recipient': Stone(Yellow,S3,Square,S3,Dotted,S1),
  'result': Stone(Red,S3,Square,S3,Dotted,S1)
}

# %%
t = [['obj', 'obj'], 'obj']
rf = pl.bfs(t,1)
# rf

# %%
rc = pl.filter_program(rf, data)

# # %% Tests
# pl.generate_program([['obj'], 'obj'], alpha=0.1, d=0.2)
# s = eval(pl.sample_base('obj')['terms'])
# t = eval(pl.sample_base('obj')['terms'])
# Program([SC, [CS, [BB, ifElse, eqObject], I], I]).run([t,t]).name
# Program([B, [setColor, Stone(Yellow,S1,Triangle,S2,Plain,S4)], getColor]).run(s).name
# Program([B, [setShape, Stone(Red,S2,Circle,S3,Dotted,S4)], [B, getShape, [B, [setPattern, Stone(Blue,S2,Square,S2,Plain,S4)], getPattern]]]).run(s).name
# Program([BK,[setColor,Stone(Red,S1,Circle,S1,Dotted,S1)],getColor]).run([s,t]).name

# %%
# x = pl.content
# x['type'] = 'primitive'
# y = pl.base_terms
# y['type'] = 'base_term'

# z = y.append(x, ignore_index=True)
# z = z.drop(['name'], axis=1)
# z.to_csv('data/pm_init.csv')
