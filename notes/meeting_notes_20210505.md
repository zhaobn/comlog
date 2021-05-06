# Meeting notes (2021-05-05)

## Experiment design

### Stimuli

- 5 white agents: enlarge the recipient, and A's edges ~ how much larger R gets
- 1 black agent: shrink the recipient

(Counterbalance agent feature values between participants)

Example learning data

| trial | agent                    | recipient              | result                 |
|-------|--------------------------|------------------------|------------------------|
| 1     | Stone(white,triangle,S3) | Stone(white,square,S3) | Stone(white,square,S4) |
| 2     | Stone(white,square,S3)   | Stone(white,square,S3) | Stone(white,square,S5) |
| 3     | Stone(white,pentagon,S3) | Stone(white,square,S3) | Stone(white,square,S6) |
| 4     | Stone(white,triangle,S3) | Stone(black,square,S3) | Stone(black,square,S4) |
| 5     | Stone(white,square,S3)   | Stone(black,square,S3) | Stone(black,square,S5) |
| 6     | Stone(white,pentagon,S3) | Stone(black,square,S3) | Stone(black,square,S6) |
| 7     | Stone(black,triangle,S3) | Stone(white,square,S3) | Stone(white,square,S2) |

### Procedure

We could test several kinds of generalization scenarios (each as a separate experiment, or factors in a mixed design?)

- **Bootstrapping**: test generalization on black agents, and see if participants are biased towards "A's edges ~ how much shrinkage R undergoes"
- **Extrapolation**: test on red agents, and see if participants get more creative on the prediction or still incline to the "A's edges ~ how much larger R gets" influence (model prediction)
- **Composition/mediation**: test on gray agents, and grayness might mix the enlarge & shrink effects together into some sort of mediated predictions? Like darker gray agents are more likely to shrink while lighter grays enlarge? 

Consider using sliders to adjust size in the generalization task phase.

## Model

I coded up a quick demo with the extended primitives (add, mul) and it seems that the step 1 search + loop method is likely to produce if-else chains. 
We might consider setting up the primitives carefully to encode the desired effect, or compare the step 1 search method vs a purely sampling-based method?

## Other ideas

- Context (background factor) ~ multiplicative composition
- Curriculum design
- Unlearn a cause
