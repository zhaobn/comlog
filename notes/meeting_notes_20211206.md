
# Notes (2021-11-29)

## Experiment 3

See [Rmarkdown](https://eco.ppls.ed.ac.uk/~s1941626/exp_3_analysis.html)

## Alternative models

### PCFG in CNF form

Productions (with flat prior):

```
S -> +(A,A)
S -> -(A,A)
S -> x(A,A)
A -> S
A -> B
B -> C
B -> D
C -> stripe
C -> spot
C -> stick
D -> 0
D -> 1
D -> 2
D -> 3
```

Implementation plan:

- Enumerate up till length 1 and 2
- Inference: prior * likelihood ~ posterior over expressions => generate generalization predictions

### Similarity-based exemplar categorization

- For two pairs of observations `A` and `B`, dissimilarity `DS(A,B) = \sum_F(abs(F(A)-F(B)))`, where feature `F = {stripe, spot, stick}`
- Can convert to a similarity scale by `exp(-DS)`
- Generalization prediction: compare each generalization trial with all the available learning pairs, find the most similar learning pair, and change to the `L'` of that learning pair
- RULEX (covered by our model where we allow exceptions?)

### Linear regression

- IV: `stripe`, `spot`, `stick`
- DV: `L'` (round to int)
- Formula: `L' = a*stripe + b*spot + c*stick`
- Include interation: `L' = a*stripe + b*spot + c*stick + d*stripe*spot + e*stripe*stick + f*spot*stick`

### Gaussian process regression

- 6 learning + 8 generalization = 14 dimensional covariance matrix
- Each data point has 3 dimentional input (stripe, spot, stick) and 1 output prediction (L')
- Scikit-learn package?
- Kernel choice: sum?

## General question

- Fit individual participants?
