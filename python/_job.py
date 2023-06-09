
# %%
RUNS = range(42)
LEARN_ITERS = list(range(1,11)) + [ 2**x for x in range(4,11) ]

# # %%
# for i in LEARN_ITERS:
#   print(f'mkdir process_{str(i)}')
#   #print(f'cp decon_preds.csv process_{str(i)}/decon_preds_a.csv')
#   #print(f'cp decon_preds.csv process_{str(i)}/decon_preds_b.csv')

# # %%
# TO_CP_ITERS = list(range(4000, 10001, 2000)) + list(range(20000, 100001, 20000))
# for i in TO_CP_ITERS:
#   print(f'cp -r process_4000/ process_{str(i)}/')

# # %%
# for i in LEARN_ITERS:
#   for c in ['construct', 'combine', 'decon', 'flip']:
#     print(f'cp pcfg/process_{str(i)}/{c}_preds_a.csv pcfg_rj/process_{str(i)}/{c}_preds_a.csv')

#%%
for r in range(25,38):
  for i in LEARN_ITERS:
    print(f'mkdir run_{r}/data_geo/process_{i}')

# %%
