
# Notes (2021-11-29)

## WHY-21 workshop

- Camera ready version submitted. Also on [arXiv](http://arxiv.org/abs/2111.12560).
- [Poster](https://drive.google.com/file/d/1ujjimjUzyOkIsoucPk0bgtGtPQt6S_WA/view?usp=sharing) (due Dec 1)
- Thumbnail?

## Experiment 3 pilot

See [Rmarkdown](http://eco.ppls.ed.ac.uk/~s1941626/pilot_2_analysis.html)

## Alternative models

### PCFG in CNF form

Productions (with flat prior):

```
S -> and(S,A)
A -> +(B,B)
A -> -(B,B)
A -> x(B,B)
B -> stripe
B -> spot
B -> stick
B -> 0
B -> 1
B -> 2
B -> 3
```

- Expection: depth 1 enumeration fails to learn ground truth; depth 2 enumeration no order effect (de-construct condition learns ground truth successfully)
- Inference: (enumerated expressions) prior * likelihood ~ posterior over expressions => generate generalization predictions
- Or MCMC? Generate expressions, local tree update, accept/reject => posterior over expressions => generate generalization predictions
- Or, from expressions that are consistent with data, update production rule probabilities (Dirichlet) => generate generalization predictions

### Similarity-based exemplar categorization

- For two pairs of observations `A` and `B`, dissimilarity `DS(A,B) = \sum_F(abs(F(A)-F(B)))`, where feature `F = {stripe, spot, stick}`
- Can convert to a similarity scale by `exp(-DS)`
- Generalization prediction: compare each generalization trial with all the available learning pairs, find the most similar learning pair, and change to the `L'` of that learning pair
- RULEX (covered by AG?)

### Linear regression

- IV: `stripe`, `spot`, `stick`
- DV: `L'` (round to int)
- Formula: `L' = a*stripe + b*spot + c*stick`
- What if with `L' = a*stripe + b*spot + c*stick + d*stripe*spot + e*stripe*stick + f*spot*stick`?

### Gaussian Process

## General question

- Fit individual participants?
