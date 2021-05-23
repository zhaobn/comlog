
# Meeting notes (2021-05-24)

## Model implementation updates

- Typed enumeration
- Depth = 2, in order to include `addnn <num -> num -> num>`, `mulnn <num -> num -> num>`
- Not including `ifElse` for now (typed frames N = 7 million)
- `fast_run`: sample typed frames => unfold and check for consistency w.r.t. data => max attempt 100 (This is very, very efficient)

## Model results

- Data: the 3 * 3 design, show (1) per row, (2) column, (3) right-diagonal, (4) left-diagonal, (5) combined
- Method: `fast_run`, iteration = 500, for each loop sample 1 consistent program; ran a comprehensive run for the combined data setup for comparison
- Result:
  - (1)-(4) is learning the expected sub-programs
    - Per row:
    - Per column:
    - Left diagonal:
    - Right diagonal
  - Combined data failed to learn a consistent program, even for the comprehensive run (because of depth=2 typed enumeration & no `ifElse` primitive)

However we can "pre-train" the model to learn the `addnn(getEdge(A),-2)` sub-program. In this way, our model can learn the ground-truth rule (`setLength(R, addnn(getLength(R), addnn(getEdge(A),-2))`) successfully.

- Pre-train setup: triangle ~ 1, rectangle ~ 2, pentagon ~ 3 (See demo experiment)
