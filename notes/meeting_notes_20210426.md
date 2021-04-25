# Meeting notes (2021-04-26)

## Implementation

- Adding sub-program (M) complexity into prior probability: get a complexity measure of this sub-program, use it as the parameter for the dirichlet distribution
  - Approximately: 1/C_M, where C_M is the number of terms in program M. 0 < 1/C_M < 1, the more complicated program `M` gets, the smaller this value is.
  - Precisely: use the probability of generating this sub-program given the current program library.
- Batch processing with fallback: for n data point and a step 1 search, if none of the enumerated programs is consistent with all the data point, fall back to filter consistent programs that are consistent with a random data point => add to library => next iteration

## Tests

- Two sets of rules. Each consists of a `4 x 3` set up.
  - Rule set 1: (1) Red A makes R red, (2) Red A set R's size to the same saturation level of A, (3) Red A makes R square
  - Rule set 2: (1) Red A makes R red, (2) All A set R's size to the same saturation level of A, (3) Circled A makes R square
- Batch processing vs. incremental processing.
- Pick top 1, 2, 3 filtered programs, iternation = number of data points vs. sample 1 filtered program, iteration = 100.

## Results

- Incremental processing finds consistent programs for all the conditions, while the batch method fails for rule 1.2, rule set 1, and somehow rule 2.3?
- Bug in picking top n programs: when log probs are the same, programs were ranked alphabetically by python, hence top 3 selected ones are more likely to start with `BS` - categorizing observations based on the recipient object. Consider sampling from the equally-likely top ones.
- Our model can easily learn a complex if-else rule (because of incremenal processing & reuse). Example: `[BS,[S,[B,ifElse,isS3Sat],[S,[S,[B,ifElse,isS2Size],I],[C,[B,setShape,I],Square]]],[CB,[C,[B,ifElse,isTriangle],Stone(Red,S1,Square,S2)],[S,[S,[B,ifElse,isS3Sat],[C,[B,setShape,I],Square]],I]]]`
- Sampling with 100 iterations is not growing extra complex programs, but a tighter distribution over a couple of (short) possibilities (when the ground truth is covered).
- Induced some very salient base terms and sub-programs. Eg. `isBlue`, `Red`, `setColor`, `[C,[B,setColor,I],Red]`
- The approximated complexity measure has almost identical performance as for the precise one and is computationally more efficient - recommend. Can think about putting more penalty with a parameter.

## TODOs

- Fix the top n selection bug => use sampling (among the top-ranked possibilities?)
- Number of iterations seems to predict how tight the distribution is (can be mediated by a softmax?)
- Plot size of intermediate filtered programs, complexity, percentage of use etc.
- Compare generalization predictions
- Develop pilot experiments

