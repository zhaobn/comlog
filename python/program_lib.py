
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)
from numpy import random as np_random
from math import log, exp
from itertools import product as itertools_product

from task_configs import *
from base_terms import Program
from helpers import args_to_string, names_to_string, term_to_dict, secure_list, print_name

# %%
class Program_lib_light:
  def __init__(self, df, dir_alpha=0.1):
    self.content = df
    self.DIR_ALPHA = dir_alpha
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
          'count': [1],
        }), ignore_index=True)

class Program_lib(Program_lib_light):
  def __init__(self, df, dir_alpha=0.1):
    Program_lib_light.__init__(self, df, dir_alpha)
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'type': 'ERROR'}
    self.SET_MARKERS = set(list(self.content[self.content['type']=='base_term'].return_type))

  # Get log probs
  def update_log_prob(self, init=False):
    df = self.content.query(f'type=="primitive"')
    df['log_prob'] = self.log_dir(df['count'])
    for t in self.SET_MARKERS:
      sub_df = self.content.query(f'type=="base_term"&return_type=="{t}"')
      sub_df['log_prob'] = self.log_dir(sub_df['count'])
      df = df.append(sub_df)
    programs = self.content.query(f'type=="program"')
    if init==1:
      self.content = df.append(programs).fillna(0)
    else:
      # complexity penalty, adjustable
      programs['prior'] = programs.apply(lambda row: exp(row['log_prob']), axis=1)
      programs['log_prob'] = self.log_dir(programs['count'], programs['prior'])
      self.content = df.append(programs[['terms','arg_types','return_type','type','count','log_prob']])

  # List all the possile stones (w flat prior)
  def get_all_objs(self):
    stones_df = pd.DataFrame({'terms': []})
    colors_df = self.content.query('return_type=="col"&type=="base_term"')
    shapes_df = self.content.query('return_type=="shp"&type=="base_term"')
    # patterns_df = self.content.query('return_type=="pat"&type=="base_term"')
    ints_df = self.content.query('return_type=="int"&type=="base_term"')
    for c in range(len(colors_df)):
      for ci in range(len(ints_df)):
        for s in range(len(shapes_df)):
          for si in range(len(ints_df)):
            # for p in range(len(patterns_df)):
            #   for pi in range(len(ints_df)):
            stone_feats = [
              colors_df.iloc[c].at['terms'],
              ints_df.iloc[ci].at['terms'],
              shapes_df.iloc[s].at['terms'],
              ints_df.iloc[si].at['terms'],
              # patterns_df.iloc[p].at['terms'],
              # ints_df.iloc[pi].at['terms']
            ]
            counts = [
              colors_df.iloc[c].at['count'],
              ints_df.iloc[ci].at['count'],
              shapes_df.iloc[s].at['count'],
              ints_df.iloc[si].at['count'],
              # patterns_df.iloc[p].at['count'],
              # ints_df.iloc[pi].at['count'],
            ]
            stones_df = stones_df.append(pd.DataFrame({'terms': [f'Stone({",".join(stone_feats)})'], 'count': [sum(counts)]}), ignore_index=True)
    stones_df['log_prob'] = self.log_dir(list(stones_df['count']))
    return stones_df[['terms', 'log_prob']]

  def get_cached_program(self, type_signature):
    arg_t, ret_t = type_signature
    matched_pms = self.content.query(f'arg_types=="{args_to_string(arg_t)}"&return_type=="{ret_t}"&type!="base_term"')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type, filter_pm=False):
    filter_program = '&type!="program"' if filter_pm else ''
    matched_pms = self.content.query(f'return_type=="{return_type}"&type!="base_term"{filter_program}')
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

  def sample_matched_program(self, return_type, filter_pm = False, add=False):
    matched = self.get_matched_program(return_type, filter_pm)
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
      # pattern = self.sample_base('pat', add)
      # pattern_scale = self.sample_base('int', add)
      sampled_props = [ color, color_scale, shape, shape_scale ] #, pattern, pattern_scale ]
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
          left = self.sample_matched_program(ret_t, True, add)
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

  def log_dir(self, count_vec, priors = []):
    if len(count_vec) == 1:
      dir_prob = [1]
    elif len(priors) == 0:
      dir_prob = [ i+self.DIR_ALPHA-1 for i in count_vec ]
    else:
      dir_prob = [ i+j-1+self.DIR_ALPHA for i,j in zip(count_vec, priors) ]
    return [ log(i/sum(dir_prob)) for i in dir_prob ]

  @staticmethod
  def get_all_routers(arg_list, left_arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    candidates = ['B']
    if free_index >= 0:
      candidates.append('K')
    if free_index > 0: #and len(arg_list) <= len(left_arg_list):
      candidates.append('C')
      candidates.append('S')
    routers = []
    for r in list(itertools_product(candidates, repeat=len(arg_list))):
      routers.append(''.join(r))
    return routers

  # enumeration
  def bfs(self, type_signature, depth = 0):
    programs_df = pd.DataFrame({'terms': [], 'log_prob': []})
    arg_types, ret_type = type_signature
    # when no arg is provided, return all the base terms
    if len(arg_types) < 1:
      programs_df = programs_df.append(pd.DataFrame({'terms': [ret_type], 'log_prob': [0]}), ignore_index=True)
      return programs_df
    else:
      # find direct matches
      ret_terms = self.get_cached_program(type_signature)
      if ret_terms is not None:
        prims = ret_terms.query('type=="primitive"')
        prims_append = pd.DataFrame({'terms': [], 'log_prob': []})
        if len(prims) > 0:
          prims_append = prims[['terms','count']]
          prims_append['log_prob'] = self.log_dir(list(prims_append['count']))
          programs_df = pd.concat([programs_df, prims_append[['terms', 'log_prob']]])
        if len(ret_terms) > len(prims_append):
          pm_typesig = args_to_string(arg_types) + '_' + ret_type
          programs_df = programs_df.append(pd.DataFrame({'terms': [f'PM("{pm_typesig}")'], 'log_prob': [1]}), ignore_index=True)
      # return direct matches
      if depth < 1:
        return programs_df
      # enumerate recursively
      else:
        left_trees = self.get_matched_program(ret_type, True)
        for i in left_trees.index:
          left_terms = left_trees.at[i, 'terms']
          left_arg_types = left_trees.at[i, 'arg_types'].split('_')
          free_index = len(left_arg_types)-1
          # get routers
          routers = self.get_all_routers(arg_types, left_arg_types, free_index)
          for rt in routers:
            routed_args = eval(rt).run({'left': [], 'right': []}, arg_types)
            left = self.expand(left_terms, left_arg_types, free_index-1, routed_args['left'], depth)
            # depth = depth if (left_terms == 'ifElse' and free_index == 0) else depth-1
            right = self.bfs([routed_args['right'], left_arg_types[free_index]], depth-1)
            if len(left) > 0 and len(right) > 0:
              programs_df = programs_df.append(self.combine_terms(left, right, rt, log(1/len(routers))), ignore_index=True)
        return programs_df

  def expand(self, left_term, left_arg_types, free_index, args, depth):
    if free_index < 0:
      return pd.DataFrame({'terms': [ left_term ], 'log_prob': [0]})
    else:
      if len(args) < 1:
        left = self.expand(left_term, left_arg_types, free_index-1, [], depth)
        right = self.bfs([[],left_arg_types[free_index]], depth-1)
        return self.combine_terms(left, right)
      else:
        routers = self.get_all_routers(args, left_arg_types, free_index-1)
        terms_df = pd.DataFrame({'terms': [], 'log_prob': []})
        for rt in routers:
          routed_args = eval(rt).run({'left': [], 'right': []}, args)
          left = self.expand(left_term, left_arg_types, free_index-1, routed_args['left'], depth)
          # depth = depth if (left_term == 'ifElse' and free_index == 0) else depth-1
          right = self.bfs([routed_args['right'], left_arg_types[free_index]], depth-1)
          if len(left) > 0 and len(right) > 0:
            terms_df = terms_df.append(self.combine_terms(left, right, rt, log(1/len(routers))))
      return terms_df

  def typed_enum(self, type_signature, depth = 1):
    programs_df = pd.DataFrame({'terms': [], 'log_prob': []})
    arg_types, ret_type = type_signature
    if len(arg_types) < 1:
      programs_df = programs_df.append(pd.DataFrame({'terms': [ret_type], 'log_prob': [0]}), ignore_index=True)
      return programs_df
    else:
      # Compress direct matches
      if self.get_cached_program(type_signature) is not None:
        programs_df = programs_df.append(pd.DataFrame({'terms': [f'PM("{args_to_string(arg_types)}_{ret_type}")'], 'log_prob': [0]}), ignore_index=True)
      # return direct matches
      if depth < 1:
        return programs_df
      # enumerate recursively
      else:
        left_trees = self.get_matched_program(ret_type, True)
        for i in left_trees.index:
          left_terms = left_trees.at[i, 'terms']
          left_arg_types = left_trees.at[i, 'arg_types'].split('_')
          free_index = len(left_arg_types)-1
          # get routers
          routers = self.get_all_routers(arg_types, left_arg_types, free_index)
          for rt in routers:
            routed_args = eval(rt).run({'left': [], 'right': []}, arg_types)
            left = self.typed_expand(left_terms, left_arg_types, free_index-1, routed_args['left'], depth)
            right = self.typed_enum([routed_args['right'],left_arg_types[free_index]], depth-1)
            if len(left) > 0 and len(right) > 0:
              programs_df = programs_df.append(self.combine_terms(left, right, rt, log(1/len(routers))), ignore_index=True)
        return programs_df

  def typed_expand(self, left_term, left_arg_types, free_index, args, depth):
    if free_index < 0:
      return pd.DataFrame({'terms': [ left_term ], 'log_prob': [0]})
    else:
      if len(args) < 1:
        left = self.typed_expand(left_term, left_arg_types, free_index-1, [], depth)
        right = self.typed_enum([[],left_arg_types[free_index]], depth-1)
        return self.combine_terms(left, right)
      else:
        routers = self.get_all_routers(args, left_arg_types, free_index)
        terms_df = pd.DataFrame({'terms': [], 'log_prob': []})
        for rt in routers:
          routed_args = eval(rt).run({'left': [], 'right': []}, args)
          left = self.typed_expand(left_term, left_arg_types, free_index-1, routed_args['left'], depth)
          right = self.typed_enum([routed_args['right'], left_arg_types[free_index]], depth-1)
          if len(left) > 0 and len(right) > 0:
            terms_df = terms_df.append(self.combine_terms(left, right, rt, log(1/len(routers))))
      return terms_df

  @staticmethod
  def exclude_identity(df):
    id_df = df.query('terms=="I"')
    if len(id_df) > 0:
      df = df.drop(id_df.index.values[0])
    return df

  @staticmethod
  def combine_terms(left_df, right_df, router = '', router_lp = 0):
    left_df = left_df.add_prefix('left_'); left_df['key'] = 0
    right_df = right_df.add_prefix('right_'); right_df['key'] = 0
    combined = left_df.merge(right_df, how='outer')
    if len(router) < 1:
      combined['terms'] = '[' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob']
    else:
      combined['terms'] = '[' + router + ',' + combined['left_terms'] + ',' + combined['right_terms'] + ']'
      combined['log_prob'] = combined['left_log_prob'] + combined['right_log_prob'] + router_lp
    # combined = combined.astype({'left_log_prob': 'int32', 'right_log_prob': 'int32'})
    # combined['log_prob'] = combined['left_log_prob'] | combined['right_log_prob']
    return combined[['terms', 'log_prob']]

  @staticmethod
  def query_obj_lp(obj, df):
    return df.query(f'terms=="{obj}"').log_prob.values[0]

  @staticmethod
  def trim_frames(frames):
    to_ignore = [
      'eqObject],obj],obj]',
      'eqColor,col],col]',
      'eqSaturation,int],int]',
      'eqShape,shp],shp]',
      'eqSize,int],int]',
      'eqPattern,pat],pat]',
      'eqDensity,int],int]',
      'ifElse,bool',
    ]
    trimed = frames[~frames.terms.isin(to_ignore)]
    return trimed

  def unfold_programs_with_lp(self, terms, log_prob, data):
    programs = self.unfold_program(terms, data)
    programs['log_prob'] = programs['log_prob'] + log_prob
    return programs

  def unfold_program(self, terms, data):
    if terms[:2]=='PM':
      pm = eval(terms)
      unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"&type=="program"')
      if len(unfolded) > 0:
        return unfolded[['terms', 'log_prob']]
      else:
        return pd.DataFrame({'terms': [], 'log_prob': []})
    else:
      programs_list = []
      log_probs_list = []
      term_list = terms.split(',')
      all_obs = self.get_all_objs()
      for i in range(len(term_list)):
        t = term_list[i]
        tm = t.strip('[]')
        if tm in list(self.SET_MARKERS):
          unfolded = self.content.query(f'return_type=="{tm}"&type=="base_term"')
          unfolded_terms = list(unfolded['terms'])
          unfolded_lps = list(unfolded['log_prob'])
        elif tm == 'obj':
          cur_data = data[-1]
          unfolded_terms = [str(cur_data['recipient']), str(cur_data['result'])]
          unfolded_lps = [self.query_obj_lp(x, all_obs) for x in unfolded_terms]
        elif 'PM' in tm:
          pm = eval(tm)
          qs = '&type=="program"' if (pm.arg_types == ['obj'] and pm.return_type == 'obj') else ''
          unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"{qs}')
          unfolded_terms = list(unfolded['terms'])
          unfolded_lps = list(unfolded['log_prob'])
        elif eval(tm).ctype == 'router':
          unfolded_terms = [tm]
          unfolded_lps = [0] # Taken care of by the frame base lp
        elif eval(tm).ctype == 'primitive':
          unfolded_terms = [tm]
          unfolded_lps = list(self.content.query(f'terms=="{tm}"&type=="primitive"').log_prob)
        else:
          print('Unknow term!')
        programs_list.append([t.replace(tm, u) for u in unfolded_terms])
        log_probs_list.append(unfolded_lps)
      return self.iter_compose_programs(programs_list, log_probs_list)

  @staticmethod
  def iter_compose_programs(terms_list, lp_list):
    programs_list = list(itertools_product(*terms_list))
    programs_list_agg = [','.join(p) for p in programs_list]
    log_probs_list = list(itertools_product(*lp_list))
    log_probs_list_agg = [sum(x) for x in log_probs_list]
    return pd.DataFrame({'terms': programs_list_agg, 'log_prob': log_probs_list_agg})

  @staticmethod
  def check_program(terms, data):
    result = Program(eval(terms)).run([data['agent'], data['recipient']])
    return result.name == data['result'].name

  def filter_program(self, df, data):
    data = secure_list(data)
    query_string = '&'.join([f'consistent_{i}==1' for i in range(len(data))])
    filtered = pd.DataFrame({'terms': [], 'log_prob': []})
    for i in range(len(df)):
      to_unfold = df.iloc[i].at['terms']
      print(f'Unfolding {to_unfold}')
      to_check = self.unfold_programs_with_lp(df.iloc[i].at['terms'], df.iloc[i].at['log_prob'], data)
      if len(to_check) > 0:
        for j in range(len(data)):
          to_check[f'consistent_{j}'] = to_check.apply(lambda row: self.check_program(row['terms'], data[j]), axis=1)
        passed_pm = to_check.query(query_string)
        print(f"{i+1}/{len(df)} | Unfolding {df.iloc[i].at['terms']} - {len(passed_pm)} passed")
        filtered = filtered.append(passed_pm[['terms', 'log_prob']], ignore_index=True)
    return filtered

# # %%
# pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)
# pl = Program_lib(pm_init, 0.1)
# pl.update_log_prob(init=True)
# pl.update_log_prob(init=False)

# frames = pd.read_csv('data/pm_frames.csv',index_col=0)
# data = [{
#   'agent': Stone(Yellow,S2,Triangle,S1), # Plain,S1
#   'recipient': Stone(Red,S1,Triangle,S1),
#   'result': Stone(Yellow,S1,Triangle,S2)
# }]
# pl.unfold_program(frames.at[73,'terms'], data)

# # %%
# def clist_to_df(clist):
#   df = pd.DataFrame({
#     'terms': [],
#     'arg_types': [],
#     'return_type': [],
#     'type': [],
#     'count': [],
#   })
#   for et in secure_list(clist):
#     if isinstance(et, dict) == 0:
#       et = term_to_dict(et)
#     df = df.append(pd.DataFrame({
#       'terms': [et['terms']],
#       'arg_types': [et['arg_types']],
#       'return_type': [et['return_type']],
#       'type': [et['type']],
#       'count': [0]
#     }), ignore_index=True)
#   return df.groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})

# pm_init = clist_to_df([
#   isRed, isBlue, isYellow,
#   isCircle, isSquare, isTriangle,
#   isStripy, isDotted, isPlain, isCheckered,
#   isS1Sat, isS2Sat, isS3Sat, isS4Sat,
#   isS1Size, isS2Size, isS3Size, isS4Size,
#   isS1Den, isS2Den, isS3Den, isS4Den,
#   getColor, setColor, eqColor,
#   getSaturation, setSaturation,
#   getShape, setShape, eqShape,
#   getSize, setSize,
#   getPattern, setPattern, eqPattern,
#   getDensity, setDensity,
#   eqInt, eqObject, ifElse,
#   {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
#   True, False,
#   Red, Yellow, Blue,
#   Square, Triangle, Circle,
#   Dotted, Plain, Stripy, Checkered,
#   S1, S2, S3, S4,
# ])
# pm_init.to_csv('data/pm_init.csv')

# pm_init_test = clist_to_df([
#   True, False,
#   Red, Yellow, Blue,
#   Square, Triangle, Circle,
#   S1, S2, S3,
#   isRed, isBlue, isYellow,
#   isCircle, isSquare, isTriangle,
#   isS1Sat, isS2Sat, isS3Sat,
#   isS1Size, isS2Size, isS3Size,
#   getColor, setColor, eqColor,
#   getSaturation, setSaturation,
#   getShape, setShape, eqShape,
#   getSize, setSize,
#   eqInt, eqObject, ifElse,
#   {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
# ])
# pm_init_test.to_csv('data/pm_init_test.csv')

# # %%
# pm_init = pd.read_csv('data/task_pm_2.csv', index_col=0, na_filter=False)
# pl = Program_lib(pm_init, 0.1)
# pl.update_log_prob(init=1)
# pl.update_log_prob()

# pl.get_init_prior()
# pl.content.to_csv('data/pm_init_cut.csv')

# t = [['obj', 'obj'], 'obj']
# pl.generate_program(t)
# rf = pl.typed_enum(t,1)
# rf2 = pl.typed_enum(t,2)
# rf2.to_csv('data/task_frames_2.csv')

# rf.to_csv('data/pm_frames.csv')
# rf = pd.read_csv('data/new_frames.csv', index_col=0, na_filter=False)

# rf = pd.read_csv('data/pm_frames.csv', index_col=0, na_filter=False)
# terms = rf.at[118,'terms']

# # %%
# data = {
#   'agent': Stone(Yellow,S2,Triangle,S1), # Plain,S1
#   'recipient': Stone(Red,S1,Triangle,S1),
#   'result': Stone(Yellow,S1,Triangle,S2)
# }
# pl = Program_lib(pm_init_test, 0.1)
# t = [['obj', 'obj'], 'obj']
# pl.generate_program(t)
# rf = pl.bfs(t,1)
# x = pl.filter_program(rf,data)


# %%
