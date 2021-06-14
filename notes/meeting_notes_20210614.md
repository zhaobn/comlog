
# Notes (2021-06-14)

## Model update

- Adjust the "fast_run" method to use repeated-sample *without* replacement, so that in the end we will finish checking all the possible frames. Since ground-truth is now covered by depth 2 frames, this resample procedure will always end up finding consistent programs
- **Need a measure for "difficulty": number of inconsistent programs checked before finding the first consistent program?**
- Process model may consider weighted resample (update frames with latest primitive weights) & stop at *n* times

## Experiment design & model results

### Stimuli

|   | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | 1 | 2 | 3 | 4 |
| 2 | 2 | 4 | 6 |   |
| 3 | 3 | 6 | 9 |   |
| 4 | 4 |   |   |   |

Per row: agent, stripes

Per column: recipient, length (number of blocks)

Groud truth: `setLen(R,mult(getLen(R),getStripe(A)))`

### Experiment setup

Alice and Bob are testing two sets of magic eggs.

1. Alice (red stripy agents):

   1. `(4, 1) => 4`
   2. `(2, 2) => 4`
   3. `(1, 4) => 4`

   What do you think the magic power of these eggs are? (Model: `[KC,[B,setLength,[B,I,I]],4]`)

   Make prediction for a new egg `(3, 3) => ?`

2. Bob (green stripy agents):

   1. `(1, 1) => 1`
   2. `(2, 1) => 2`
   3. `(3, 1) => 3`

   What do you think the magic power of these eggs are? (Model: `[SC,[KB,mulnn,getLength],getStripe]`)

   Make prediction for a new egg `(4, 1) => ?`

3. Actually, the eggs Alice and Bob tested are all from a same hen - meaning that they have the same magic power. (With two sets of history showing on top of the page) what is that power?

   Make predictions with the rest of the trials (yellow stripy agent?)

We have three candidates for Bob's set:

- Easy (used in the example above):

   1. `(1, 1) => 1`
   2. `(2, 1) => 2`
   3. `(3, 1) => 3`

- Easy (model: `[C,[B,mulnn,getStripe],2]]`):

   1. `(2, 1) => 2`
   2. `(2, 2) => 4`
   3. `(2, 3) => 6`

- Hard (Model: `[KB,I,I]`):

   1. `(1, 1) => 1`
   2. `(1, 2) => 2`
   3. `(1, 3) => 3`

## Normative model results

All compositions are able to recover the groundtruth. There is no difference between easy and hard composition.

