
# Notes (2021-06-28)

## Experiment demo

- Row 2 + col 2: <https://eco.ppls.ed.ac.uk/~s1941626/eggs_easy/p/welcome.html>
- Row 1 + set 4: <https://eco.ppls.ed.ac.uk/~s1941626/eggs_hard/p/welcome.html>

  Subset batch description:

  - Row 1: `(1, 1) => 1`, `(1, 2) => 2`, `(1, 3) => 3`, model preds: no change
  - Row 2: `(2, 1) => 2`, `(2, 2) => 4`, `(2, 3) => 6`, model preds: doubles R
  - Col 2: `(1, 2) => 2`, `(2, 2) => 4`, `(3, 2) => 6`, model preds: doubles A, A + A
  - Set 4: `(1, 4) => 4`, `(2, 2) => 4`, `(4, 1) => 4`, model preds: 4

To edit the instruction text, use this link: <https://docs.google.com/document/d/19TEv5uSu9-Pb3Bf_5ayo5u49FgiI_vVwfDIFDjK3PCw/edit?usp=sharing>

## Design sketch

1. Bootstrapping

   - Condition 1: Alice (row 2) + Bob (col 2) + Combined
   - Condition 2: Alice (col 2) + Bob (row 2) + Combined
   - Control: randomly picked 6 learning trials

   Hypothesis:

   1. For each subset, people will conclude a minimal causal relationship that is consistent with the subset info but deviates from the more complex ground truth.
   2. When combined together, people will be able to conclude the ground truth by composing the learned info together
   3. In the control condition, people may fail to generalize the ground truth (?)

   **Alternatively**, we could drop the Alice/Bob framing, and simply present two batches of three eggs as if they are from the same hen.

   By doing this, we expect to observe the change from a minimal causal relation expanded to the ground truth one in order to account for the second batch of observations.

2. Misguided

   - Condition 1: Alice (row 1) + Bob (set 4) + Combined
   - Condition 2: Alice (set 4) + Bob (row 1) + Combined
   - Control: the two bootstrapping conditions

   Hypothesis: People should find it harder to generalize the grouth truth in the misguided condition as they are specificially guided to a wrong sub-part of the ground truth.

   Some people may be able to get the ground truth, as it is not too complicated anyways. We may observe two groups of answers: one failed, and one got it. Use decision time to measure difficulty???

   **Alternatively**, we can drop the Alice/Bob phasing design and use col 1 + col 2 to contrast row 2 + col 2.

3. Color-variants

   Each magic egg is randomly assigned a color
