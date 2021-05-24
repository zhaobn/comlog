
# Meeting notes (2021-05-24)

Previous experiment stimuli draft: https://docs.google.com/presentation/d/1uTY-Tnpu7i1vSZGUGWzDuUZ6rHr-V6f_25ykbu_uYyY/edit#slide=id.gd892460753_0_5

## Model updates

- Use typed enumeration (cf. Lucas Morales)
- Introduce `fast_run`: sample typed frames => unfold and check for consistency w.r.t. data => max attempt 100 (This is very, very efficient).

Task-specifically, I'm making these changes:

- Fix (typed frames) enumeration depth = 2, in order to include `addnn <num -> num -> num>`, `mulnn <num -> num -> num>`.
- Not consider `ifElse` for now (otherwise typed frames N = 7 million). Hence not having `isShape`, `eqShape` sorts of primitives, instead let the model really focus on the universal arithmetric relationships that we are testing.


## Model results

- Data: the 3 * 3 design, observing data per (1) row, (2) column, (3) right-diagonal, (4) left-diagonal, (5) combined
- Method: `fast_run`, iteration = 500, for each loop sample 1 consistent program; ran a comprehensive run for the combined data setup for comparison
- Result:
  - (1)-(4) is learning the expected sub-programs
    - Per row: `[C,[B,addnn,getLength],1]`
    - Per column: `[B,[addnn,-1],getEdge]`
    - Left diagonal: `[C,[B,mulnn,getLength],2]`
    - Right diagonal: `[B,[setLength,Stone(Rect,L3)],[K,getEdge,Stone(Rect,L4)]]` (subprogram `[K,getEdge,Stone(Rect,L4)]]` is an approximation for number 4)
  - Combined data failed to learn a consistent program, even for the comprehensive run (because of depth=2 typed enumeration & no `ifElse` primitive & no fallback)

However we can "pre-train" the model to learn the `addnn(getEdge(A),-2)` sub-program. In this way, our model can learn the ground-truth rule (`setLength(R, addnn(getLength(R), addnn(getEdge(A),-2))`) successfully.

For completeness, we can get 4 models:

- Factor 1: `fast_run` vs. `run`
- Factor 2: use fallback (to existing data point) vs. no fallback

We may be able to use KL divergence to measure a model's generalization prediction against participants' as per number of iteration/computation increases.

## Experiment interface

- See demo. So far drafted pretrainings (_"(magic) power detection"_), learning examples and one generalization task.


