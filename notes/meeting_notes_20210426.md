# Meeting notes (2021-04-26)

## Implementation

- Adding sub-program (`M`) complexity into prior probability: get a complexity measure of this sub-program, use it as the parameter for the dirichlet distribution
  - Approximately: `1/C_M`, where `C_M` is the number of terms in program `M`. `0 < 1/C_M < 1`, the more complicated program `M` gets, the smaller this value is.
  - Precisely: use the probability of generating this sub-program given the current program library.
- Batch processing with fallback: for `n` data point and a step 1 search, if none of the enumerated programs is consistent with all the data point, fall back to filter consistent programs that are consistent with a random data point => add to library => next iteration

## Tests

- Two sets of rules. Each consists of a `4 x 3` set up.
  - Rule set 1: Red A makes R red, Red A set R's size to the same saturation level of A, Red A makes R square
  - Rule set 2: Red A makes R red, All A set R's size to the same saturation level of A, Circled A makes R square
- Batch processing vs. incremental processing.
- Pick top 1, 2, 3 filtered programs, iternation = number of data points vs. sample 1 filtered program, iteration = 100.

## Results
