# Meeting notes (2021-03-15)

## Implemented

- **Program enumerator**: breadth-first search (BFS) with step 1; prob is given according to current counts (in log format).
  - For the enumerated programs, prior can be calculated directly in the enumeration process
  - There is also an adaptor grammar implementation of prior prob for generated programs

- **MAP estimatse**: check whether a list of programs are consistent with a training data point & rank by prior

## Plan

Approximate n-step search with iterated 1-step enumeration:

- For the first data point:
  - Enumerate all the 1-step (or 2-step) programs
  - Filter out all the inconsistent programs
  - Add the consistent set of programs (base terms, primitives, sub-programs) to the program library (shall we consider the enumeration prior?)
  - Use this updated program library for the next data point

- Do this EC (Explore-Compression) style process for learning, and use the generated programs for generalization

Question:

- Is it necessary to ``forget'' what's learned in a data point when sweeping through it again?

Notes:

- The number of possible programs grows really fast as the number of base terms & steps increases. Full base terms with 1-step search => 326; minimal base terms with 2-step search => 33,279.
- Current design will only *grow* the program library and not take out anything (unlikely things just got assigned very tiny probs, but still there)
- Can I run experiments on Ebby?
- Side discovery: match rules (`[BC,[B,setColor,I],getColor]`) are easier than set-to-constant-values rules (`[BC,[B,[[ifElse, True],[C,[B,setColor,I],Red]],I]`) if we consider the latter implicitly encode a universal condition check
