
# Notes (2022-04-28)

## Cross validation

Considering both Chris' suggestion and cogsci reviews, instead of regression model we should do classification models.

(We might want regression model as an alternative to the symbolic programs? Meaning that we don't really compare their predicted result quantity with people's, just list that they fail to
learn the ground truth function.)

For the similarity and multinom models, I also fitted a softmax parameter in addition to the three parameters for each feature in order to avoid -Inf in log likelihood calculations

Random baseline: -7319.634

| model expt | LL    | LL        |
|------------|-------|-----------|
| AG         | exp_1 | **-6186** |
| PCFG       | exp_1 | -6248     |
| multinom   | exp_1 | -7246     |
| similarity | exp_1 | -7277     |
| AG         | exp_2 | **-6270** |
| PCFG       | exp_2 | -6276     |
| similarity | exp_2 | -6687     |
| multinom   | exp_2 | -6813     |

## Cogsci reviews

* Framing about bootstrapping - move toward how complex concepts can be build?
* Chunking in comparison with hierarchical deep neural nets
* compare with non-symbolic methods (classification model)
* Linguistic context (i'm not so keen)
* Analyze our order effects better

## Writing

Framings

## Experiments 3 and 4

## Research statement
