
# Notes (2022-03-28)

## Alternative models

### 1. PCFG

* Implementation

  Productions (with flat prior):

  ```
  S -> and(S,A)
  A -> +(B,B), A -> -(B,B), A -> x(B,B)
  B -> C, B -> D,
  C -> stripe, C -> spot, C -> stick
  D -> 0, D -> 1, D -> 2, D -> 3
  ```

  Generation depth cap at 40

  Determinstic likelihood (0 or 1)

  Generated 100,000 hypothese

* Results replicate the slicing model (no chunking) as in our cogsci sumbission: no order effects between `construct` and `deconstruct`, and `combine` mixed two alternative explanations (while people and AG model strongly favors one of them).

Note that the PCFG productions here already guarantee that they won't produce senseless expressions.
A more close-to-AG version might extend the `C ->` productions to

```
C -> stripe(O), C -> spot(O), C -> stick(O),
O -> agent_obj, O -> recipient_obj
```

### 2. Similarity-based


```
DS(A,B) = exp[-(a*|stripe-stripe'| + b*|dot-dot'| + c*|block-block'|)]
```

For a gen task `g_i`, for each learning example `l_j`, compute `DS(g_i, l_j) * resultBlock_j` and sum up.

**Result**: about 3 or 4 blocks in Phase A, and in `{0, 2, 3, 4}` in Phase B (condition construct).

**Note**: used `a = b = c = 1` for now; haven't tried fitting them.


### 3. Linear regression

``` R
lm(resultBlock ~ stripe + dot + block)
```

**Result**: Phase A all gen tasks point to 4, phase B to 2, 3 or 4.

**Note**: Could perhaps bin CI to a distribution over possible selections?


### 4. GP regression

``` Python
k = GPy.kern.RBF(input_dim=3, variance=1., lengthscale=1.)
m = GPy.models.GPRegression(X,Y,k)
m.optimize(messages=True)
```

| Tasks | Phase A pred | Variance | Phase B pred | Variance |
|-------|--------------|----------|--------------|----------|
|     0 |     3.299987 | 0.443404 | 1.936271     | 0.436094 |
|     1 |     3.299981 | 0.443441 | 1.175364     | 2.792737 |
|     2 |     3.299991 | 0.443376 | 2.643355     | 0.437606 |
|     3 |     3.299980 | 0.443450 | 0.450200     | 0.640816 |
|     4 |     3.299986 | 0.443413 | 1.671853     | 1.843249 |
|     5 |     3.299970 | 0.443514 | -0.040645    | 2.651764 |
|     6 |     3.299987 | 0.443404 | 2.774185     | 2.705330 |
|     7 |     3.299961 | 0.443579 | -0.112345    | 4.391032 |


## Paper draft

<https://www.overleaf.com/3838639435zfgsztjjghym>

## Misc

* Dave L's comments
  * Constrast causal representation with non-causal cateogory learning
  * Compositional forms in comp. generalization
  * Incremental hypothesis construction using Christo's [2013 data](https://journals.sagepub.com/doi/full/10.1177/0956797613476046)
* Amsterdam talk feedback
  * Philosophy of science: when is a rule a "law"?
  * Inductive logic programming
