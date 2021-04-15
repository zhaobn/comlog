
# %%
from base_terms import *

# %%
s = Stone(Blue, S2, Circle, S2, Dotted, S1)
t = Stone(Blue, S2, Circle, S2, Dotted, S2)

# demo = Program([C, setColor, Yellow])
# demo = Program([B, [eqColor, Red], getColor])
# demo.run([s]).name


# demo = Program([BC, setColor, getColor])
# demo = Program([CS, [CB, [B, ifElse, [B, [eqColor, Red], getColor]], [C, setColor, Red]], I])
# demo = Program([CB, [S, [B, ifElse, [B, [eqColor, Blue], getColor]], I], I])
# demo.run([s, t]).name

# Program([getColor, Stone(Red, S2, Circle, S2, Plain, S1)]).run().name
# Program([KC, [B, setColor, I], Blue]).run([s,t]).name

# Program([CB,[S,[B,ifElse,[C,[B,objEqColor,I],Red]],I],I]).run([s,t]).name
# Program([KK,I,Stone(Red,S1,Square,S2,Dotted,S3)]).run([s,t]).name
Program([CS,[SS,[BB,ifElse,[CB,[B,eqInt,[B,getSize,I]],[B,getSaturation,I]]],[KK,I,Stone(Yellow,S1,Square,S2,Dotted,S3)]],I]).run([s,t]).name
