
# Notes (2021-06-07)

## Stimuli design

|   | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | 1 | 2 | 3 | 4 |
| 2 | 2 | 4 | 6 |   |
| 3 | 3 | 6 | 9 |   |
| 4 | 4 |   |   |   |

Per row: agent, stripes

Per column: recipient, length (number of blocks)

## Gardenpathing

1. Agent: 1 stripe; Recipients: 1 block, 2 blocks, 3 blocks. Expected generalization: no change
2. Agent: 2 stripes; Recipients: 1 block, 2 blocks, 3 blocks. Expected generalization: `setLen(R,mult(getLen(R),2))`
3. Agent: 1 stripe, 2 stripes, 3 stripes; Recipients: 1 block. Expected generalization: `setLen(R,getStripe(A))`
4. (Agent: 1 stripe; Recipient: 4 blocks),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 4 stripes; Recipient: 1 block). Expected generalization: `setLen(R,4)`

## Composition

* 2 + 3: compose ground truth easily
* 1 + 4: hard

## More possible gardenpathing combos

* (Agent: 1 stripe; Recipient: 1 blocks),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 3 stripes; Recipient: 3 blocks). Expected generalization: `setLen(R,mult(getLen(R),getLen(R)))`
* (Agent: 1 stripe; Recipient: 3 blocks),  (Agent: 2 stripes; Recipient: 2 blocks), (Agent: 3 stripes; Recipient: 1 block). Expected generalization: `setLen(R,mult(getLen(R),getStripe(A)))`
