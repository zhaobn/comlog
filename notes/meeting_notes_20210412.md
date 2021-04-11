# Meeting notes (2021-04-12)

## From two weeks ago:

- Finished implementing complete runs
- Generalization tests:
  |               | Training                                | Learning                                      |
  |---------------|-----------------------------------------|-----------------------------------------------|
  | Bootstrapping | If red, take A shape; saturation ~ size | If blue, take A pattern; saturation ~ density |
  | Trapped       | If red, take A shape; saturation ~ size | If red, take A pattern; saturation ~ density  |
- Compositional generalization tests:
  |      | Training 1           | Training 2        |
  |------|----------------------|-------------------|
  | Rule | If red, take A shape | Saturation ~ size |
  | Data | Fixed size           | Non-red agents    |

  Conditions: independent, mixed, sequence 1, sequence 2

**Problems**

- First attempt: batch processing cannot get a program that is consistent with all observations (depth=1) => falls back to filtering with single data point
- Second attempt: `ifElse` not returning meaningful boolean condition checks => use a local `depth = 1` for the boolean condition
- `MemoryExceed` error. Remove too complicated unfoldings?


## Current status

- Complete runs take a long time: ~20min for checking one data point
- Ground truth is quite complicated, haven't been able to get it for now (actually wasn't able to complete a full run)
  - Batch processing fails to find a rule that is consistent with all the observations (this may be solved if I can actually run a long chain)
  - Order matters (it might not order if I'd able to run a long chain)?

## Plan

- Carefully design data
- Let the normative model run as long as it needs
- Process model online update?
