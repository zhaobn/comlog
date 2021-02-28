
# %%
from base_terms import *

# %%
s = Stone(Red, S2, Circle, S2, Plain, S1)
t = Stone(Red, S1, Square, S4, Dotted, S2)

# demo = Program([C, setColor, Yellow])
# demo.run([s]).name

# demo = Program([BC, setColor, getColor])
# demo.run([s, t]).name

# demo = Program([B, [eqColor, Red], getColor])
# demo.run([s])

# demo = Program([CS, [CB, [B, ifElse, [B, [eqColor, Red], getColor]], [C, setColor, Red]], I])
# demo.run([s, t]).name

demo = Program([CB, [S, [B, ifElse, [B, [eqColor, Blue], getColor]], I], I])
demo.run([s, t]).name

# %%
