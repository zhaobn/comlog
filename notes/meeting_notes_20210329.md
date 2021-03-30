# Meeting notes (2021-03-29)

## Implemented

- Each type signature (including base types and primitives) is treated as a Dirichlet distribution with parameter alpha (alpha = 0.1 for now)
  - When enumerating, use type signature placeholder (~ conditional probability)
  - When evaluating, unfold placeholders with relevant probabilities (dirichlet, turn counts into probabilities)
- Extract top n (n = 2) programs according to MAP estimates and add to library
  - Likelihood: consistency with observed data, 0 or 1
  - Rank consistent programs according to MAP estimates
  - Extract programs, sub-programs, base terms and primitives and update their counts in the library
- Loop through learning data points and get updated libraries

## Tests run

- Keep top 1 program, treat data points independently
- Keep top 2 programs, treat data points independently
- Keep top 2 programs, treat data points incrementally (best)

## For discussion

- Generalization prediction: take a sampling approach
- One performance improve I can make if we are happy with only keeping top n programs: ignore folded programs if `log_prob` is too low (not worthy)
- Does it still make sense to loop through learning data multiple times (if we are only keeping the top n)?
- Ready to run on potential experiment designs

## Manuscript submission ([CB&B](https://www.springer.com/journal/42113/submission-guidelines))

- Use "entities" or stick with "objects"?
- Model names. We have **UnCaLa** (universal causal laws), **LoCaLa** (local causal laws) and **LoCaLaPro** for now.
- Template choice - two column or single column for submission?
- [Additional info](https://docs.google.com/document/d/1TWOqpus6UPS3F8BwIZsfX3abD5ZFdlDQkMYbHKE6MwE/edit?usp=sharing): funding, consent, conflicts of interest, suggested reviewers
