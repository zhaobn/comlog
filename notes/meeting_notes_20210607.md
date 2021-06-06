
# Notes (2021-06-07)

## Model update

- Adjust the "fast_run" method to use repeated-sample *without* replacement, so that in the end we will finish checking all the possible frames. Since ground-truth is now covered by depth 2 frames, this resample procedure will always end up finding consistent programs
- Need a measure for "difficulty": number of inconsistent programs checked before finding the first consistent program?

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

### Gardenpathing

1. Agent: 1 stripe; Recipients: 1 block, 2 blocks, 3 blocks. Model prediction: `[KB,I,I]`
2. Agent: 2 stripes; Recipients: 1 block, 2 blocks, 3 blocks. Model prediction: `setLen(R,mult(getLen(R),2))`, `setLen(R,add(getLen(R),getLen(R)))`
3. Agent: 1 stripe, 2 stripes, 3 stripes; Recipients: 1 block. Model prediction: `setLen(R,getStripe(A))`, `setLen(R,mult(getLen(R),getStripe(A)))`
4. (Agent: 1 stripe; Recipient: 4 blocks),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 4 stripes; Recipient: 1 block). Model prediction: `setLen(R,4)`, `Stone(Rect,S0,L4)`

### Composition

Group numbers are the same as list numbers in previous section.

- Group 2 + group 3: should be easy to compose ground truth, as it empahsed both `getLen(R)` and `getStripe(A)` by the two groups separately. Since the two critical subparts are symmetric (`mult(getLen(R)),getStripe(A)` <> `mult(getStripe(A)),getLen(R)`), there shouldn't be a difference if participants learn group 2 first then group 3, or learn group 3 first then group 2.
- Group 1 + group 4: hard. Our model will be able to find consistent programs because of design, but my suspicion is that people will find it hard.

### More possible gardenpathing candidates

- (Agent: 1 stripe; Recipient: 1 block),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 3 stripes; Recipient: 3 blocks). Expected generalization: `setLen(R,mult(getLen(R),getLen(R)))`
- (Agent: 1 stripe; Recipient: 3 blocks),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 3 stripes; Recipient: 1 block). Expected generalization: `setLen(R,mult(getLen(R),getStripe(A)))` - get ground truth by just three observations
