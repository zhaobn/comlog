# Meeting notes (2021-04-05)

## Implemented

- Complete runs
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

## Problems

- First attempt: batch processing cannot get a program that is consistent with all observations (depth=1) => falls back to filtering with single data point
- Second attempt: `ifElse` not returning meaningful boolean condition checks => use a local depth = 1 for the boolean condition
- `MemoryExceed` error. Remove too complicated unfoldings?
