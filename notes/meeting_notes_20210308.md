# Meeting notes (2021-03-08)

## Current status

- Finished the full program generator and program executor, with all the pre-defined primitives
- When generating a new program, use cache with probability (parameter) and cache generated subtrees

**Side comments**

- We are doing a tail-recursion style of program generation, where the intermediate types are sampled in a way that the left tree's type signature is guaranteed to be found in the library
- There are some restrictions in routing arguments and expanding the left tree, in order to make sure the final program is of a legitimate format. If we do not apply these restrictions, we may end up with ill-formed programs. Example:
  - Type signature `o -> o -> o`: take two objects, return one object
  - Sample a left subtree `o -> c -> o`
  - Sample a router `CC`
  - If left subtree can freely take any routed arguments, we end up with a already fulfilled left tree - `c` is provided from the right, one `o` can be taken from the routed arguments - and the other routed argument has no where to be put

## Doing inference

- Prior on program => generate it together with the program? Can we use some analytical definitions, like `1/(x^number_of_subtrees)`?
- Likelihood: consistent with data => 1, otherwise => 0
- Posterior approximation: MCMC MH?
  - Proposal distribution: subtree regrowth (with appeared feature values?)
  - Acceptance: if the new sample is not consistent with observations, drop it; if both the old and new samples are consistent with observations, hasting ratio `H = P(new|old)/P(old|new)`, compare with a random number u ~ U(0,1) for acceptance.
  - Question: what is the transition probability `P(new|old)` here if we take a subtree regeneration approach - similar to the prior but restricted with whatever has been generated?

## Further notes

- Generalization decisions: apply whatever learned v.s. some creation on the spot?
- Zach Davis process model principles: biased starting point, limited resources
