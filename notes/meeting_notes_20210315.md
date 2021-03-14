# Meeting notes (2021-03-15)

## Implemented

**Program enumerator**: breadth-first search (BFS) with step 1; prob is given according to current counts (in log format).

- For the enumerated programs, prior can be calculated directly in the enumeration process
- There is also an adaptor grammar implementation of prior prob for generated programs

## Plan

Approximate n-step search with iterated 1-step enumeration:

- For the first data point:
  - Enumerate all the 1-step programs
  - Filter out all the inconsistent programs; rank consistent ones according to the prior (MAP estiamtes)
  - List all the sub-programs for re-use (how to assign proper priors for these ones?)
  - Use this updated program library for the next data point

Questions:

- How to assign priors after we take out sub-programs for reuse? Do some fake count?
- Is it necessary to ``forget'' what's learned in a data point when sweeping through it again?

Notes:

- Can I run experiments on Ebby?
- Side discovery: match rules (`[BC,[B,setColor,I],getColor]`) are easier than set-to-constant-values rules (`[BC,[B,[[ifElse, True],[C,[B,setColor,I],Red]],I]`) if we consider the latter implicitly encode a universal condition check
