
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from numpy import random as np_random
from math import log
from itertools import product as itertools_product

from base_terms import *
from list_helpers import args_to_string, names_to_string

# %%
class Program_lib:
  def __init__(self, program_list = [], base_list = []):
    self.content = pd.DataFrame({
      'terms': pd.Series([], dtype='str'),
      'arg_types': pd.Series([], dtype='str'),
      'return_type': pd.Series([], dtype='str'),
      'count': pd.Series([], dtype='int'),
      'name': pd.Series([], dtype='str')
    })
    self.base_terms = copy(self.content)
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'name': 'ERROR'}
    if len(program_list) > 0: self.add(program_list)
    if len(base_list) > 0: self.add_bases(base_list)
    self.SET_MARKERS = set(list(self.base_terms.return_type))

  def add(self, entry_list):
    entry_list = secure_list(entry_list)
    for et in entry_list:
      if isinstance(et, dict):
        # sampled from program lib
        terms = et['terms']
        arg_types = et['arg_types']
        return_type = et['return_type']
        name = et['name'] if 'name' in et else ''
      elif et.ctype == 'primitive':
        terms = et.name
        arg_types = args_to_string(et.arg_type)
        return_type = et.return_type
        name = et.name
      else:
        print('Adding to program lib: Bad entry type!')
        pass
      # check existence
      program_found = self.content.query(f'terms == "{terms}" & arg_types == "{arg_types}" & return_type == "{return_type}"')
      if program_found.empty:
        # entry is new to lib, add to lib
        df_et = pd.DataFrame({
          'terms': pd.Series([terms], dtype='str'),
          'arg_types': pd.Series([arg_types], dtype='str'),
          'return_type': pd.Series([return_type], dtype='str'),
          'count': pd.Series([1], dtype='int'),
          'name': pd.Series([name], dtype='str')
        })
        self.content = self.content.append(df_et, ignore_index=True)
      else:
        assert len(program_found) == 1, 'Duplicated entries in program lib!'
        idx = program_found.index[0]
        self.content.at[idx, 'count'] += 1

  def add_bases(self, base_list):
    base_list = secure_list(base_list)
    for bt in base_list:
      if isinstance(bt, dict):
        # sampled from program generation
        terms = bt['terms']
        return_type = bt['return_type']
      elif isinstance(bt, bool):
        terms = 'True' if bt == True else 'False'
        return_type = 'bool'
      else:
        terms = bt.name
        return_type = bt.ctype
      # check existence
      found = self.base_terms.query(f'return_type == "{return_type}" & terms == "{terms}"')
      if found.empty:
        self.base_terms = self.base_terms.append(pd.DataFrame({
          'terms': pd.Series([terms], dtype='str'),
          'arg_types': pd.Series([''], dtype='str'),
          'return_type': pd.Series([return_type], dtype='str'),
          'count': pd.Series([1], dtype='int'),
          'name': pd.Series([terms], dtype='str'),
        }), ignore_index=True)
      elif len(found) > 1:
        print('Duplicated base terms!'); exit
      else:
        self.base_terms.at[found.index[0], 'count'] += 1

    # List all possible stones (w flat prior)

  # List all the possile stones (w flat prior)
  def get_all_objs(self):
    stones_df = pd.DataFrame({'terms': [], 'log_prob': []})
    colors_df = self.base_terms.query('return_type=="col"')
    shapes_df = self.base_terms.query('return_type=="shp"')
    patterns_df = self.base_terms.query('return_type=="pat"')
    ints_df = self.base_terms.query('return_type=="int"')
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
    matched_pms = self.content.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type):
    matched_pms = self.content.query(f'return_type == "{return_type}"')
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
      stone = 'Stone(' + ','.join([p['name'] for p in sampled_props]) + ')'
      return {'terms': stone, 'arg_types': '', 'return_type': 'obj', 'name': stone}
    else:
      bases = self.base_terms.query(f'return_type == "{type}"')
      if bases is None or bases.empty:
        print('No base terms found!')
        return self.ERROR_TERM
      else:
        sampled = bases.sample(n=1, weights='count').iloc[0].to_dict()
        if add:
          self.add_bases(sampled)
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
            'return_type': type_signature[1]
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
        'return_type': candidate['return_type']
      }

  # enumeration
  def bfs(self, type_signature, depth = 0):
    programs_df = pd.DataFrame({'terms': [], 'is_set': []})
    arg_types, ret_type = type_signature
    # when no arg is provided, return all the base terms
    if len(arg_types) < 1:
      programs_df = programs_df.append(pd.DataFrame({'terms': [ret_type], 'is_set': [1]}))
      # if ret_type == 'obj':
      #   ret_terms = self.get_all_objs()
      # else:
      #   ret_terms = self.base_terms.query(f'return_type=="{ret_type}"')
      # programs_df['terms'] = ret_terms['terms']
      # total = sum(ret_terms['count'])
      # programs_df['log_prob'] = ret_terms.apply(lambda row: log(row['count']/total), axis = 1)
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

  def check_program(self, terms, is_set, data):
    if is_set == True:
      programs_list = []
      term_list = terms.split(',')
      for t in term_list:
        tm = t.strip('[]')
        if tm in list(self.SET_MARKERS):
          unfolded = self.base_terms.loc[self.base_terms['return_type']==tm].terms.values
        elif tm == 'obj':
          unfolded = self.get_all_objs().terms.values
        else:
          unfolded = [tm]
        unfolds = [t.replace(tm, u) for u in unfolded]
        programs_list.append(unfolds)
      programs_list = list(itertools_product(*programs_list))
      programs_list = [','.join(p) for p in programs_list]
      return [self.check_program(p, 0, data) for p in programs_list]
    else:
      result = Program(eval(terms)).run([data['agent'], data['recipient']])
      return {'terms': terms, 'is_consistent': result.name == data['result'].name}

  def filter_program(self, df, data, to_df = False):
    filtered = []
    for i in range(len(df)):
      checks = self.check_program(df.iloc[i].at['terms'], df.iloc[i].at['is_set'], data)
      filtered += list(filter(lambda x: x['is_consistent']==True, secure_list(checks)))
    filtered_terms = [x['terms'] for x in filtered]
    return pd.DataFrame({'terms': filtered_terms}) if to_df else filtered_terms

  # Combined function
  def bfs_filter(self, type_signature, depth, data, to_df=True):
    programs_df = self.bfs(type_signature, depth)
    return self.filter_program(programs_df, data, to_df)


pl = Program_lib(
  program_list=[
    getColor, setColor, eqColor,
    # getSaturation, setSaturation, eqSaturation,
    # getShape, setShape, eqShape,
    # getSize, setSize, eqSize,
    # getPattern, setPattern, eqPattern,
    # getDensity, setDensity, eqDensity,
    eqObject, ifElse, {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'}
   ],
  base_list=[
    True, #False,
    Red, Red, Yellow,
    Circle, #Square, #Triangle,
    Dotted, #Plain,
    S1, #S2, #S3, S4
  ])

data = {
  'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
  'recipient': Stone(Yellow,S3,Square,S3,Dotted,S1),
  'result': Stone(Red,S3,Square,S3,Dotted,S1)
}

# %%
t = [['obj', 'obj'], 'obj']
rf = pl.bfs(t,1)
rf

# %%
pl.check_program('[BC,[B,setColor,I],getColor]', rf.iloc[0].at['is_set'], data)
# # %% Tests
# pl.generate_program([['obj'], 'obj'], alpha=0.1, d=0.2)
# s = eval(pl.sample_base('obj')['terms'])
# t = eval(pl.sample_base('obj')['terms'])
# Program([SC, [CS, [BB, ifElse, eqObject], I], I]).run([t,t]).name
# Program([B, [setColor, Stone(Yellow,S1,Triangle,S2,Plain,S4)], getColor]).run(s).name
# Program([B, [setShape, Stone(Red,S2,Circle,S3,Dotted,S4)], [B, getShape, [B, [setPattern, Stone(Blue,S2,Square,S2,Plain,S4)], getPattern]]]).run(s).name
# Program([BK,[setColor,Stone(Red,S1,Circle,S1,Dotted,S1)],getColor]).run([s,t]).name

# %%
