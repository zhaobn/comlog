
# %%
#LEARN_ITERS = [10,50,100] + list(range(200, 1001, 200)) + list(range(2000, 10001, 2000)) + list(range(20000, 100001, 20000))
#LEARN_ITERS = list(range(100, 1001, 100)) + list(range(2000, 10001, 1000))
LEARN_ITERS = list(range(100, 1501, 100)) + list(range(2000, 5001, 500))

# %%
for i in LEARN_ITERS:
  print(f'mkdir process_{str(i)}')
  # print(f'cp ag/decon_preds_a.csv ag/process_{str(i)}/decon_preds_a.csv')
  # print(f'cp ag/decon_preds_b.csv ag/process_{str(i)}/decon_preds_b.csv')

# %%
TO_CP_ITERS = list(range(4000, 10001, 2000)) + list(range(20000, 100001, 20000))
for i in TO_CP_ITERS:
  print(f'cp -r process_4000/ process_{str(i)}/')

# %%
for i in LEARN_ITERS:
  for c in ['construct', 'combine', 'decon', 'flip']:
    print(f'cp pcfg/process_{str(i)}/{c}_preds_a.csv pcfg_rj/process_{str(i)}/{c}_preds_a.csv')

# %%
LEARN_ITERS = list(range(100, 1001, 150))
for i in LEARN_ITERS:
  print(f'mkdir process_{str(i)}')


# %%
# LEARN_ITERS = list(range(100, 1001, 100)) + list(range(2000, 10001, 1000))

LEARN_ITERS = list(range(12000, 20001, 2000))

for i in LEARN_ITERS:
  print(f'mkdir process_{str(i)}')

# %%
