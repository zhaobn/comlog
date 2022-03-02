# %%
from random import sample
from math import log

# %%
class Rational_rules:
  def __init__(self, p_rules, cap=10):
    self.NON_TERMINALS = [x[0] for x in p_rules]
    self.PRODUCTIONS = {}
    self.CAP = cap
    for rule in p_rules:
      self.PRODUCTIONS[rule[0]] = rule[1]

  def generate_tree(self, tree_str='S', log_prob=0., depth=0):
    current_nt_indices = [tree_str.find(nt) for nt in self.NON_TERMINALS]
    # Sample a non-terminal for generation
    to_gen_idx = sample([idx for idx, el in enumerate(current_nt_indices) if el > -1], 1)[0]
    to_gen_nt = self.NON_TERMINALS[to_gen_idx]
    # Do generation
    leaf = sample(self.PRODUCTIONS[to_gen_nt], 1)[0]
    to_gen_tree_idx = tree_str.find(to_gen_nt)
    tree_str = tree_str[:to_gen_tree_idx] + leaf + tree_str[(to_gen_tree_idx+1):]
    # Update production log prob
    log_prob += log(1/len(self.PRODUCTIONS[to_gen_nt]))
    # Increase depth count
    depth += 1

    # Recursively rewrite string
    if any (nt in tree_str for nt in self.NON_TERMINALS) and depth <= self.CAP:
      self.generate_tree(tree_str, log_prob, depth)
    elif any (nt in tree_str for nt in self.NON_TERMINALS):
      print('====DEPTH EXCEEDED!====')
      return None
    else:
      print(tree_str, log_prob)
      return (tree_str, log_prob)

# %%
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe', 'spot', 'stick']],
  ['D', ['0', '1', '2', '3']]
]

# %%
test = Rational_rules(productions, cap=40)
test.generate_tree()
