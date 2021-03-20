
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from numpy import random as np_random
from math import log
from itertools import product as itertools_product

from base_terms import *
from helpers import args_to_string, names_to_string, term_to_dict

# %%
class Program_lib_light:
  def __init__(self, df):
    self.content = df

  def add(self, entry_list):
    entry_list = secure_list(entry_list)
    for et in entry_list:
      # check existence
      if isinstance(et, dict) == 0:
        et = term_to_dict(et)
      found_terms = self.content.query('terms=="'+et['terms']+'"&arg_types=="'+et['arg_types']+'"&return_type=="'+et['return_type']+'"&type=="'+et['type']+'"')
      if len(found_terms) > 0:
        self.content.at[found_terms.index.values[0],'count'] += 1
      else:
        self.content = self.content.append(pd.DataFrame({
          'terms': [et['terms']],
          'arg_types': [et['arg_types']],
          'return_type': [et['return_type']],
          'type': [et['type']],
          'count': [1]
        }))
class Program_lib(Program_lib_light):
  def __init__(self, df):
    Program_lib_light.__init__(self, df)
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'type': 'ERROR'}
    self.SET_MARKERS = set(list(self.content[self.content['type']=='base_term'].return_type))

  # def add(self, entry_list):
  #   entry_list = secure_list(entry_list)
  #   for et in entry_list:
  #     # check existence
  #     if isinstance(et, dict) == 0:
  #       et = term_to_dict(et)
  #     found_terms = self.content.query('terms=="'+et['terms']+'"&arg_types=="'+et['arg_types']+'"&return_type=="'+et['return_type']+'"&type=="'+et['type']+'"')
  #     if len(found_terms) > 0:
  #       self.content.at[found_terms.index.values[0],'count'] += 1
  #     else:
  #       self.content.append(pd.DataFrame({
  #         'terms': [et['terms']],
  #         'arg_types': [et['arg_types']],
  #         'return_type': [et['return_type']],
  #         'type': [et['type']],
  #         'count': [1]
  #       }))

  # List all the possile stones (w flat prior)
  def get_all_objs(self):
    stones_df = pd.DataFrame({'terms': [], 'log_prob': []})
    colors_df = self.content.query('return_type=="col"&type=="base_term"')
    shapes_df = self.content.query('return_type=="shp"&type=="base_term"')
    patterns_df = self.content.query('return_type=="pat"&type=="base_term"')
    ints_df = self.content.query('return_type=="int"&type=="base_term"')
    for c in range(len(colors_df)):
      for ci in range(len(ints_df)):
        for s in range(len(shapes_df)):
          for si in range(len(ints_df)):
            for p in range(len(patterns_df)):
              for pi in range(len(ints_df)):
                stone_feats = [
                  colors_df.iloc[c].at['terms'],
                  ints_df.iloc[ci].at['terms'],
                  shapes_df.iloc[s].at['terms'],
                  ints_df.iloc[si].at['terms'],
                  patterns_df.iloc[p].at['terms'],
                  ints_df.iloc[pi].at['terms']
                ]
                counts = [
                  colors_df.iloc[c].at['count'],
                  ints_df.iloc[ci].at['count'],
                  shapes_df.iloc[s].at['count'],
                  ints_df.iloc[si].at['count'],
                  patterns_df.iloc[p].at['count'],
                  ints_df.iloc[pi].at['count'],
                ]
                stones_df = stones_df.append(pd.DataFrame({'terms': [f'Stone({",".join(stone_feats)})'], 'count': [sum(counts)]}))
    return stones_df

  def get_cached_program(self, type_signature):
    arg_t, ret_t = type_signature
    matched_pms = self.content.query(f'arg_types=="{args_to_string(arg_t)}"&return_type=="{ret_t}"&type!="base_term"')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type):
    matched_pms = self.content.query(f'return_type=="{return_type}"&type!="base_term"')
    return matched_pms if not matched_pms.empty else None

  def sample_program(self, p_source, add=False, weight_col = 'count'):
    if p_source is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      sampled = p_source.sample(n=1, weights=weight_col).iloc[0].to_dict()
      if add:
        self.add(sampled)
      return sampled

  def sample_cached_program(self, type_signature, add=False):
    cached = self.get_cached_program(type_signature)
    if cached is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      return self.sample_program(cached, add)

  def sample_matched_program(self, return_type, add=False):
    matched = self.get_matched_program(return_type)
    if matched is None:
      print('No match found!')
      return self.ERROR_TERM
    else:
      sampled = self.sample_program(matched, add)
      return sampled

  def sample_base(self, type, add=False):
    if type == 'obj':
      color = self.sample_base('col', add)
      color_scale = self.sample_base('int', add)
      shape = self.sample_base('shp', add)
      shape_scale = self.sample_base('int', add)
      pattern = self.sample_base('pat', add)
      pattern_scale = self.sample_base('int', add)
      sampled_props = [ color, color_scale, shape, shape_scale, pattern, pattern_scale ]
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

  @staticmethod
  def sample_router(arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    if free_index < 0:
      return 'B' * len(arg_list)
    else:
      return ''.join([np_random.choice(['C', 'B', 'S', 'K']) for _ in arg_list])

  # Tail-recursion; righthand-side tree
  def generate_program(self, type_signature, cur_step = 0, max_step = 5, alpha = 1, d = 0.2, add=True):
    if cur_step > max_step:
      print('Max step exceeded!')
      return self.ERROR_TERM
    else:
      # Pitman-Yor process
      cached = self.get_cached_program(type_signature)
      if cached is None:
        cache_param = 1
      else:
        Nt = len(cached)
        Ct = sum(cached['count'])
        cache_param = (alpha+Nt*d)/(alpha+Ct)
      # print(f'threashold: {cache_param}')
      if np_random.random() < cache_param: # Construct
        cur_step += 1
        arg_t, ret_t = type_signature
        if len(arg_t) < 1:
          # return a base term
          base_term = self.sample_base(ret_t, add)
          return base_term
        else:
          # generate new program
          left = self.sample_matched_program(ret_t, add)
          left_args = left['arg_types'].split('_')
          free_index = len(left_args) - 2
          router = self.sample_router(arg_t, free_index)
          routed_args = eval(router).run({'left': [], 'right': []}, arg_t)
          # expand left side until no un-filled arguments
          left_pm = self.expand_program(left, routed_args['left'], free_index, cur_step, max_step, alpha, d, add)
          right_pm = self.generate_program([routed_args['right'], left_args[-1]], cur_step, max_step, alpha, d, add)
          terms = [router, left_pm['terms'], right_pm['terms']]
          program_dict = {
            'terms': names_to_string(terms),
            'arg_types': args_to_string(type_signature[0]),
            'return_type': type_signature[1],
            'type': 'program',
          }
          # add to program lib
          if add:
            self.add(program_dict) if 'ERROR' not in program_dict['terms'] else None
          return program_dict
      else:
        cached['weight'] = (cached['count']-d)/(Ct-Nt*d)
        sampled = self.sample_program(cached, add, weight_col='weight')
        return sampled

  # Lefthand-side tree
  def expand_program(self, candidate, arg_list, free_index, cur_step, max_step, alpha, d, add):
    if free_index < 0:
      return candidate
    else:
      left_args = candidate['arg_types'].split('_')
      if len(arg_list) < 1:
        left_pm = self.expand_program(candidate, arg_list, free_index - 1, cur_step, max_step, alpha, d, add)
        right_pm = self.generate_program([arg_list, left_args[free_index]], cur_step, max_step, alpha, d, add)
        terms = [left_pm['terms'], right_pm['terms']]
      else:
        router = self.sample_router(arg_list, free_index-1)
        routed_args = eval(router).run({'left': [], 'right': []}, arg_list)
        left_pm = self.expand_program(candidate, routed_args['left'], free_index-1, cur_step, max_step, alpha, d, add)
        right_pm = self.generate_program([routed_args['right'], left_args[free_index]], cur_step, max_step, alpha, d, add)
        terms = [router, left_pm['terms'], right_pm['terms']]
      return {
        'terms': names_to_string(terms),
        'arg_types': candidate['arg_types'],
        'return_type': candidate['return_type'],
        'type': 'program',
      }

  # enumeration
  def bfs(self, type_signature, depth = 0):
    programs_df = pd.DataFrame({'terms': [], 'is_set': []})
    arg_types, ret_type = type_signature
    # when no arg is provided, return all the base terms
    if len(arg_types) < 1:
      programs_df = programs_df.append(pd.DataFrame({'terms': [ret_type], 'is_set': [1]}))
      return programs_df
    else:
      # find direct matches
      ret_terms = self.get_cached_program(type_signature)
      if ret_terms is not None:
        programs_df['terms'] = ret_terms['terms']
        programs_df['is_set'] = 0
        # total = sum(ret_terms['count'])
        # programs_df['log_prob'] = ret_terms.apply(lambda row: log(row['count']/total), axis = 1)
      # return direct matches
      if depth < 1:
        return programs_df
      # enumerate recursively
      else:
        left_trees = self.get_matched_program(ret_type)
        left_trees = left_trees.drop(programs_df.index) # exclude direct matches
        left_trees = self.exclude_identity(left_trees) # Identity function cannot go to the left
        for i in left_trees.index:
          left_terms = left_trees.at[i, 'terms']
          left_arg_types = left_trees.at[i, 'arg_types'].split('_')
          free_index = len(left_arg_types)-1
          # get routers
          routers = self.get_all_routers(arg_types, free_index)
          for rt in routers:
            routed_args = eval(rt).run({'left': [], 'right': []}, arg_types)
            left = self.expand(left_terms, left_arg_types, free_index-1, routed_args['left'], depth)
            right = self.bfs([routed_args['right'], left_arg_types[free_index]], depth-1)
            if len(left) > 0 and len(right) > 0:
              programs_df = programs_df.append(self.combine_terms(left, right, rt)) # log(1/len(routers))
        return programs_df

  def expand(self, left_term, left_arg_types, free_index, args, depth):
    if free_index < 0:
      return pd.DataFrame({'terms': [ left_term ], 'is_set': [0]})
    else:
      if len(args) < 1:
        left = self.expand(left_term, left_arg_types, free_index-1, [], depth)
        right = self.bfs([[],left_arg_types[free_index]], depth-1)
        return self.combine_terms(left, right)
      else:
        routers = self.get_all_routers(args, free_index-1)
        terms_df = pd.DataFrame({'terms': [], 'is_set': []})
        for rt in routers:
          routed_args = eval(rt).run({'left': [], 'right': []}, args)
          left = self.expand(left_term, left_arg_types, free_index-1, routed_args['left'], depth)
          right = self.bfs([routed_args['right'], left_arg_types[free_index]], depth-1)
          if len(left) > 0 and len(right) > 0:
            terms_df = terms_df.append(self.combine_terms(left, right, rt)) # log(1/len(routers))
      return terms_df

  @staticmethod
  def exclude_identity(df):
    id_df = df.query('terms=="I"')
    if len(id_df) > 0:
      df = df.drop(id_df.index.values[0])
    return df

  @staticmethod
  def combine_terms(left_df, right_df, router = ''): #router_lp = 0
    left_df = left_df.add_prefix('left_'); left_df['key'] = 0
    right_df = right_df.add_prefix('right_'); right_df['key'] = 0
    combined = left_df.merge(right_df, how='outer')
    if len(router) < 1:
      combined['terms'] = '[' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      # combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob']
    else:
      combined['terms'] = '[' + router + ',' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      # combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob'] + router_lp
    combined = combined.astype({'left_is_set': 'int32', 'right_is_set': 'int32'})
    combined['is_set'] = combined['left_is_set'] | combined['right_is_set']
    return combined[['terms', 'is_set']]

  @staticmethod
  def get_all_routers(arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    if free_index < 0:
      return 'B' * len(arg_list)
    else:
      routers = []
      for r in list(itertools_product(['C', 'B', 'S', 'K'], repeat=len(arg_list))):
        routers.append(''.join(r))
      return routers

  def unfold_program(self, terms, is_set):
    # Ignore 'eqObject],obj],obj]' terms
    if 'eqObject],obj],obj]' in terms:
      return pd.DataFrame({'terms': []})
    elif is_set == False:
      return pd.DataFrame({'terms': [ terms ]}) # log_prob?
    else:
      programs_list = []
      term_list = terms.split(',')
      for i in range(len(term_list)):
        t = term_list[i]
        tm = t.strip('[]')
        if tm in list(self.SET_MARKERS):
          unfolded = self.content.query(f'return_type=="{tm}"&type=="base_term"').terms.values
        elif tm == 'obj':
          unfolded = self.get_all_objs().terms.values
        else:
          unfolded = [tm]
        unfolds = [t.replace(tm, u) for u in unfolded]
        programs_list.append(unfolds)
      if 'bool]' in term_list: # TODO: do this recursively if there are more than one plain bool
        bi = term_list.index('bool]')
        # Compress the True conditions
        true_conditions = programs_list.copy()
        true_conditions[bi] = ['True]']
        if len(true_conditions[bi+2]) > 1:
          true_conditions[bi+2] = ['obj]']
        true_programs = self.iter_compose_programs(true_conditions)
        # Compress the False conditions
        false_conditions = programs_list.copy()
        false_conditions[bi] = ['False]']
        if len(false_conditions[bi+1]) > 1:
          false_conditions[bi+1] = ['obj]']
        false_programs = self.iter_compose_programs(false_conditions)
        return true_programs.append(false_programs)
      else:
        return self.iter_compose_programs(programs_list)

  @staticmethod
  def iter_compose_programs(terms_list):
    programs_list = list(itertools_product(*terms_list))
    programs_list = [','.join(p) for p in programs_list]
    return pd.DataFrame({'terms': programs_list})

  @staticmethod
  def check_program(terms, data):
    result = Program(eval(terms)).run([data['agent'], data['recipient']])
    return result.name == data['result'].name

  def filter_program(self, df, data):
    filtered = pd.DataFrame({'terms': [], 'consistent': []})
    for i in range(len(df)):
      to_check = self.unfold_program(df.iloc[i].at['terms'], df.iloc[i].at['is_set'])
      if len(to_check) > 0:
        to_check['consistent'] = to_check.apply(lambda row: self.check_program(row['terms'], data), axis=1)
        filtered = filtered.append(to_check.loc[to_check['consistent']==1], ignore_index=True)
    return filtered[['terms']]

  # Combined function
  def bfs_filter(self, type_signature, depth, data):
    programs_df = self.bfs(type_signature, depth)
    return self.filter_program(programs_df, data)

# %%
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
      'count': [1]
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
  Red, Yellow, Blue,
  Square, Triangle, Circle,
  Dotted, Plain,
  S1, S3, S3, S4,
])
# pm_init.to_csv('data/pm_init.csv')
pl = Program_lib(pm_init)

# %%
t = [['obj', 'obj'], 'obj']
rf = pl.bfs(t,1)
rf

# %%
data = {
  'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
  'recipient': Stone(Yellow,S3,Square,S3,Dotted,S1),
  'result': Stone(Red,S3,Square,S3,Dotted,S1)
}
rc = pl.filter_program(rf, data)

# %%
