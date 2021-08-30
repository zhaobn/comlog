
# Notes (2021-08-30)

## Pilot summary

<http://eco.ppls.ed.ac.uk/~s1941626/pilot_1_analysis.html>

### Main experiment

Edits ([1fe907a](https://github.com/zhaobn/comlog/commit/1fe907ace8462ad993d4f2da4637577f2368899e)) I did in encouraging synthesizing:

- Added a sentence in Introduction: "Your updated guess should be able to explain both pairs in this second phase AND the pairs you tested previously."
- Added a comprehension Q: "Your second guess has to explain the first three pairs of objects as well" (Correct)
- When writing the second guess: "What is your best guess about these magic eggs (all six, including previously shown ones)?"

Things we need to decide:

- Three conditions, or just two (construct vs. de-construct)?
- Planned sample size 80 for three conditions (~26 per condition)

### Model

See the pilot analysis above for model prediction plots. 

Problems we have now:

- In the `construct` condition, `mult` part is overwhelming because the model now recursively adds sub-parts
- Now the model can't learn anything in the `de-construct` (`discern`) condition. I'm allowing up to 1 exceptions for now, but could consider alternative ways eg.
  - Deeper search, allow `if-else`
  - Probablistic primitives: `increase`, `decrease`

## NeurIPs workshop submission

Call for submission: https://why21.causalai.net

Draft: <https://www.overleaf.com/3434632942ckrmrrjbwphy>

## COBB submission response

Editor

- **What’s causal in the judgments**
- Align models & observations
- Clean up and comment my code

Review \#2

- Restructure, explain model steps with data.
- Elaborate: what’s “causal” about the model
- Reversed agent-recipient roles
- Captions
- Grammars & typos
- Reference formats

Review \#3

- What’s causal about the inferences made
- Experiment 2, compare to ground truth; raw predictions. **We can compare B1 v B4, B2 v B3**! What a brilliant spot
- Changing both A and R (discussion point)
- Give an example how the grammar works, also the prior calculation
- Explain fitting procedure, why some can use MLE some grid-search
- Elaborate on the algorithm
- **Model preds after a single or a few run**
- Is LoCaLa a normative model? I think so
- Add mean or median to the violin plot
- **Remove the Gaussian mixture model analysis on fitted parameters?**
