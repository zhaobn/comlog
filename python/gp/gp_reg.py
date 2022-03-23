# %%
import GPy
import numpy as np
import pandas as pd


# %% Read data
task_data = pd.read_csv('../../data/tasks/exp_1.csv', index_col=0)
trainings = task_data.query('condition=="combine"&batch!="gen"') #batch=="A"'
trX = trainings[['stripe','dot','block']].to_numpy()
trY = trainings[['result_block']].to_numpy()

predictions = task_data.query('condition=="combine"&batch=="gen"')
prX = predictions[['stripe','dot','block']].to_numpy()


# %% GP regression model
k = GPy.kern.RBF(input_dim=3, variance=1., lengthscale=1.)
m = GPy.models.GPRegression(trX,trY,k)

m.optimize(messages=True)

# %% Prediction
prY, prV = m.predict(prX)

# %%
