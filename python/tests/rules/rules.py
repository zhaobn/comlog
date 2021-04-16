
# %%
import pandas as pd
import sys
sys.path.append('..')
sys.path.append('../..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from helpers import secure_list

# %%
pm_init = pd.read_csv('../../data/pm_init_cut.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init, 0.1)

# %% Get all the rules
rule_terms = [
  '[KK,I,Stone(Red,S1,Circle,S1,Dotted,S1)]',
  '[KC,[B,setColor,I],Red]',
  '[KC,[B,setColor,[C,[B,setSize,I],S1]],Red]',
  '[BC,[B,setColor,I],[B,getColor,I]]',
  '[SC,[BB,setColor,[BC,[B,setSize,I],[B,getSize,I]]],[B,getColor,I]]',
  '[SC,[BB,setColor,[BC,[B,setSize,I],[B,getSaturation,I]]],[B,getColor,I]]'
]
cond_terms = [
  '[CS,[SB,[B,ifElse,[B,isRed,I]],PM],I]',
  '[CS,[SB,[B,ifElse,[B,isRed,I]],[CS,[SB,[B,ifElse,[B,isDotted,I]],PM],I]],I]',
  '[CS,[BS,[B,ifElse,[B,isRed,I]],PM],I]',
  '[CS,[BS,[B,ifElse,[B,isRed,I]],[CS,[BS,[B,ifElse,[B,isDotted,I]],PM],I]],I]',
  '[CS,[SB,[B,ifElse,[B,isRed,I]],[CS,[BS,[B,ifElse,[B,isBlue,I]],PM],I]],I]',
  '[CS,[SB,[B,ifElse,[B,isRed,I]],[CS,[BS,[B,ifElse,[B,isDotted,I]],PM],I]],I]',
  '[CS,[SS,[BB,ifElse,[CB,[B,eqShape,[B,getShape,I]],[B,getShape,I]]],PM],I]',
  '[CS,[SS,[BB,ifElse,[CB,[B,eqInt,[B,getSize,I]],[B,getSaturation,I]]],PM],I]',
]
cond_rule_terms = []
for c in cond_terms:
  for r in rule_terms:
    cond_rule_terms.append(c.replace('PM',r))

rules = pd.DataFrame({'terms':rule_terms+cond_rule_terms})
rules.to_csv('rules.csv')

# %% Calculate prior
def get_lp(term, pos, plib=pl):
  if isinstance(term, str):
    term = eval(term)
  assert pos in ['left', 'right', 'router'], 'Invalid pos!'
  if pos == 'left':
    matched = plib.get_matched_program(term.return_type)
  elif pos == 'right':
    if isinstance(term, bool):
      matched = plib.content.query(f'type=="base_term"&return_type=="bool"')
    elif term.ctype in plib.SET_MARKERS:
      matched = plib.content.query(f'type=="base_term"&return_type=="{term.ctype}"')
    elif term.ctype == 'obj':
      matched = plib.get_all_objs()
    elif term.ctype == 'primitive':
      matched = plib.get_cached_program([secure_list(term.arg_type), term.return_type])
  else:
    all_routers = plib.get_all_routers([0]*term.n_arg, 0)
    matched = pd.DataFrame({'terms':all_routers,'count':1,'type':'router'})
  if len(matched.columns)==2:
    return matched[matched['terms']==term.name].log_prob.values[0]
  else:
    matched = matched.reset_index(drop=1)
    idx = matched[matched['terms']==term.name].index.values[0]
    return plib.log_dir(matched['count'])[idx]

def get_log_prior(terms, plib=pl):
  if isinstance(terms, str):
    terms = eval(terms)
  assert isinstance(terms, list) and len(terms)==3
  router, left_term, right_term = terms
  if any(isinstance(i, list) for i in terms):
    if isinstance(left_term, list) and isinstance(right_term, list):
      return get_lp(router, 'router', plib)+get_log_prior(left_term, plib)+get_log_prior(right_term, plib)
    elif isinstance(left_term, list):
      return get_lp(router, 'router', plib)+get_log_prior(left_term, plib)+get_lp(right_term, 'right', plib)
    else:
      return get_lp(router, 'router',plib)+get_lp(left_term, 'left', plib)+get_log_prior(right_term, plib)
  else:
    return get_lp(left_term, 'left', plib)+get_lp(right_term, 'right', plib)

rules['log_prob'] = rules.apply(lambda row: get_log_prior(row['terms']), axis=1)
rules.to_csv('rules.csv')

# %% Measure entropy
# rules = pd.read_csv('../data/rules.csv', index_col=0, na_filter=False)
# all_objs = list(pl.get_all_objs().terms)

def read_term(term):
  if isinstance(term, str):
    return eval(term)
  else:
    return term

def get_covered(term, agents, recipients, results):
  covered = 0
  for a in agents:
    a = read_term(a)
    for r in recipients:
      r = read_term(r)
      for t in results:
        covered += Program(secure_list(read_term(term))).run([a, r]).name == read_term(t).name
  return covered
# get_covered('[KK,I,Stone(Red,S1,Circle,S1,Dotted,S1)]', all_objs, all_objs, all_objs)

# %%
rules = pd.read_csv('rules.csv', index_col=0, na_filter=False)
ep_results = rules.copy()
ep_results = ep_results.reset_index(drop=True)

pm_init = pd.read_csv('../../data/pm_init_cut.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init, 0.1)
all_objs = list(pl.get_all_objs().terms)

ep_results['total'] = len(all_objs)**3
ep_results['covered'] = 0

for i in range(len(ep_results)):
  cur_term = ep_results.at[i,'terms']
  print(f'Checking {i+1}/{len(ep_results)}: {cur_term}')
  covered = get_covered(cur_term, all_objs, all_objs, all_objs)
  print(f'=> {covered}')
  ep_results.at[i, 'covered'] = covered
  ep_results.to_csv('ep_results.csv')

# # %% Test for fun
# terms = [SS,[SB,[B,ifElse,[B,isRed,I]],[KC,[B,setColor,I],Red]],[CS,[SB,[B,ifElse,[B,isDotted,I]],[KC,[B,setShape,I],Circle]],I]]
# all_objs = list(pl.get_all_objs().terms)
# x = get_covered(terms, all_objs, all_objs, all_objs)
# print(x)
