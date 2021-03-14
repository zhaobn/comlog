
# %%
from program_generator import *

# %%
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

# %%
t = [['obj', 'obj'], 'obj']
rf = pl.enumerate_program(t,1)
rf

# %%
data = {
  'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
  'recipient': Stone(Yellow,S3,Square,S3,Dotted,S1),
  'result': Stone(Red,S3,Square,S3,Dotted,S1)
}

# %%
def check_consistence(terms_list, data_dict):
  if isinstance(terms_list, str):
    terms_list = eval(terms_list)
  result = Program(terms_list).run([data_dict['agent'], data_dict['recipient']])
  return result.name == data_dict['result'].name

# check_consistence([BC,[B,setColor,I],getColor], data)
# %%
rf['consistence'] = rf.apply(lambda row: check_consistence(row['terms'], data), axis=1)

# %%
