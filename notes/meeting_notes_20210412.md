# Meeting notes (2021-04-12)

## Current status

- Complete runs take a long time: ~20min for one iteration
- Ground truth is quite complicated, haven't been able to get it for now (actually wasn't able to complete a full run)
  - Batch processing fails to find a rule that is consistent with all the observations
  - Order matters?
  - Given enough iterations it might work, just that I wasn't able to let the Gibbs sampler run long enough

## Plan

- Carefully design data
- Let the normative model run as long as it needs
- Process model online update?
