# Meeting notes (2021-05-05)

## Experiment design

### Stimuli

- 5 white agents: enlarge the recipient, and A's edges ~ how much larger R gets
- 1 black agent: shrink the recipient

(Counterbalance agent feature values between participants)

Example learning data

| trial | agent                       | recipient                 | result                    |
|-------|-----------------------------|---------------------------|---------------------------|
| 1     | Stone(white,S1,triangle,S3) | Stone(black,S1,square,S3) | Stone(black,S1,square,S4) |
| 2     | Stone(white,S1,square,S3)   | Stone(white,S1,square,S3) | Stone(white,S1,square,S5) |
| 3     | Stone(white,S1,pentagon,S3) | Stone(black,S1,square,S3) | Stone(black,S1,square,S6) |
| 4     | Stone(white,S1,triangle,S3) | Stone(white,S1,square,S3) | Stone(white,S1,square,S4) |
| 5     | Stone(white,S1,square,S3)   | Stone(black,S1,square,S3) | Stone(black,S1,square,S5) |
| 6     | Stone(black,S1,triangle,S3) | Stone(white,S1,square,S3) | Stone(white,S1,square,S2) |

### Procedure

We could test several kinds of generalization scenarios, each as a separate experiment:

- **Bootstrapping**: test generalization on black agents, and see if participants are biased towards "A's edges ~ how much shrinkage R undergoes"
- **Extrapolation**: test on red agents, and see if participants get more creative on the prediction or still incline to the "A's edges ~ how much larger R gets" influence (model prediction)
- **Composition/mediation**: test on gray agents, and grayness might mix the enlarge & shrink effects together into some sort of mediated predictions? Like darker gray agents are more likely to shrink while lighter grays enlarge? 

Consider using sliders to adjust size in the generalization task phase.

## Model

The normative bfs + sample method might not reproduce bootstrapping; consider local update.

## Other ideas

- Context (background factor) ~ multiplicative composition
- Curriculum design
- Unlearn a cause
