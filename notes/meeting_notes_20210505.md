# Meeting notes (2021-05-05)

## Experiment design

Learning data

| trial | agent                       | recipient                 | result                    |
|-------|-----------------------------|---------------------------|---------------------------|
| 1     | Stone(white,S1,triangle,S3) | Stone(black,S1,square,S3) | Stone(black,S1,square,S4) |
| 2     | Stone(white,S1,square,S3)   | Stone(white,S1,square,S3) | Stone(white,S1,square,S5) |
| 3     | Stone(white,S1,pentagon,S3) | Stone(black,S1,square,S3) | Stone(black,S1,square,S6) |
| 4     | Stone(white,S1,triangle,S3) | Stone(white,S1,square,S3) | Stone(white,S1,square,S4) |
| 5     | Stone(white,S1,square,S3)   | Stone(black,S1,square,S3) | Stone(black,S1,square,S5) |
| 6     | Stone(black,S1,triangle,S3) | Stone(white,S1,square,S3) | Stone(white,S1,square,S2) |

### Experiment 1: Bootstrapping

Generalization data: black agents

### Experiment 2: Creation

Generalization data: red agents

### Experiment 3: Composition

Generalization data: gray agents, grayness ~ mediate white & black

## Model

The normative bfs + sample method might not reproduce bootstrapping; consider local update.

## Alternative ideas

- Context (background factor) ~ multiplicative composition
- Curriculum design
- Unlearn a cause
