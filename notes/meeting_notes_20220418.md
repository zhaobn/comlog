
# Notes (2022-04-28)

## Cross validation

N.b. for the similarity model, I also fitted a softmax parameter in addition to the three parameters for each feature in order to avoid -Inf in log likelihood calculations

Random baseline: -7319.634

| model      | expt  | LL        |
|------------|-------|-----------|
| similarity | exp_1 | -7277     |
| PCFG       | exp_1 | -6248     |
| AG         | exp_1 | **-6186** |
| similarity | exp_2 | -6687     |
| PCFG       | exp_2 | -6276     |
| AG         | exp_2 | **-6270** |


## Classification models

Considering both Chris' suggestion and cogsci reviews, instead of regression model we can do classification models.

(We might want regression model as an alternative to the symbolic programs? Meaning that we don't really compare their predicted result quantity with people's, just list that they fail to learn the ground truth function.)

## Cogsci reviews



## Writing

## Experiments 3 and 4

## Research statement
