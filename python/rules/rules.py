
# %%
import pandas as pd

# %%
rule_terms = [
  '[KK,I,Stone(Red,S1,Square,S2,Dotted,S3)]',
  '[KC,[B,setColor,I],Red]',
  '[KC,[B,setColor,[C,[B,setSize,I],S3]],Red]',
  '[BC,[B,setColor,I],[B,getColor,I]]',
  '[SC,[BB,setColor,[BC,[B,setSize,I],[B,getSize,I]]],[B,getColor,I]]',
  '[SC,[BB,setColor,[BC,[B,setSize,I],[B,getSaturation,I]]],[B,getColor,I]]'
]

# %%
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
