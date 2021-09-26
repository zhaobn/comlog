
# Notes (2021-09-05)

## Main experiment

Ran a power analysis using  G*Power based on

* Sample size: 20
* Between-subject conditions: 3
* One way ANOVA (fixed effects) on self-report alignment with ground truth, summing over phase A and phase B

=> Total sample size 159

## Modeling

Implemented the simplified type signature `[egg, num] -> num`.
Our model now can produce:

* Successful constructive learning with depth=1 search and a basic set of primitives (no `ifElse`)
* Finding ground truth in the de-construction setting with depth=2 search and a basic set of primitives
* Finding approximate rules (like people) with depth=1 search, a basic set of primitives, and allowing exceptions
* Finding alternative rules with depth=1 search and an extended set of primitves (with `ifElse`, `moreDots`, `lessDots`)
* Finding complex rules (like people) with depth=1 search, extended set of primitves, and a local + global search procedure

Questions/comments:

* Gibbs sampling: what are the parameters that I'm approximating?
* Adaptor grammar (AG) prior prob definitions not working: AG encourages sharing and reusing of *sub-programs*, but we got a lot of program samples with the *same* type signature
* We achieve efficient re-use, in practice, by compressing programs with the same type with our "typed frames"
