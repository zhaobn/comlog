
# Notes (2022-04-18)

## Cross validation

Considering both Chris' suggestion and cogsci reviews, instead of regression model we should do classification models.

(We might still want regression model as an alternative to the symbolic programs? Meaning that we just list that they fail to learn the ground truth function.)

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

Nb. for the similarity and multinom models, I also fitted a softmax parameter in addition to the three parameters for each feature in order to avoid -Inf in log likelihood calculations.

## Cogsci reviews

<https://docs.google.com/document/d/1NApIjwM82vfLrXdLrzQVZzsmjgBimG0rByI2x3vQrfs/edit?usp=sharing>

* Framing about bootstrapping - move toward how complex concepts can be build?
* Chunking in comparison with hierarchical deep neural nets
* compare with non-symbolic methods (classification model)
* Linguistic context (i'm not so keen)
* Analyze our order effects better

## Writing

* Framings - been struggling a lot, and how see why given cogsci reviews
  * Should we still use bootstrapping, or shift towards construction?
  * Learning vs. generalization
* Experiments 3 and 4 models
## Other

* [Research Statement](https://docs.google.com/document/d/1CHQTUlxeVGopyek4Vven0_I-ajyav1xpIwBiC3Cc8Lk/edit?usp=sharing) 1st draft for TG's lab
* Would very much appreciate high level guidance (I'm not sure whether the kind of information/level of detail I put in there is right)
