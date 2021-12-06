
# Notes (2021-12-06)

## Experiments

In Experiment 1 and 2, we found that an incremental currciulum design can bootstrap causal generalization via constructive composition.
However, when it comes to the functional form of composition, it seems that people "add" the later bit on top of the initial bit.

Note that in previous analysis I just looked at the final learning accuracy. Will do a check on prediction homogeniety change from phase A to phase B too.

To investigate whether this preference for "addition" overrules order, or the other way around, we conducted [Experiment 3](https://eco.ppls.ed.ac.uk/~s1941626/exp_3_analysis.html). Results demonstrate that when facing both a multiplicative and an additive relations, people tend to wrap multiplication within addition, regardless of order.

## Alternative models

### PCFG

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

- Each data point has 3 dimentional input (stripe, spot, stick) and 1 output prediction (L')
- 6 learning + 8 generalization = 14 dimensional covariance matrix? 
- Scikit-learn package?
- Kernel choices

## General question

- Fit individual participants?
