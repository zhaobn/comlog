# Meeting notes (2021-03-22)

## Implemented

- `K` combinator
- Use place-holder in breadth-first search & filtering
- Program extractor: extract base terms, primitives, sub programs, get corresponding count
- Draft EC process: loop through data point, do BFS, filter consistent programs, extract and add to library

## Discussion points

- Prior prob
- Df gets too large need an efficent way to read & write
- Run synthetic data experiments (on Eddie & hopefully Ebby). For now, the BFS result for the second data point (using generated programs in the program library) is pretty huge. Will consider using placeholder in this process.
  - Downweighting
  - Practical truncation
  - Compare with a pure generative process? (no enumeration)
- About the magic stone draft: recipient vs patient
