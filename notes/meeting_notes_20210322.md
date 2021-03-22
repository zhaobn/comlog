# Meeting notes (2021-03-22)

## Implemented

- `K` combinator
- Use **placeholder** in breadth-first search & filtering
  - Color, shape, pattern, scale, objects are all stored as placeholders and only get unpacked during consistency check
  - For the `ifElse` primitive, if the boolean condition is a plain `true` or `false`, only the corresponding return condition is unpacked
  - Ignore `ifElse (eqObject, stone1, stone2) ret1 ret2` programs - not useful and too many. However we do keep all the `ifElse (eqObject, stone1, I) ret1 ret2` kind of programs (because comparing an argument to a specific stone is meaningful)
  - Placeholders do improve efficienct a lot. From 22k programs => 132 frames => 77 (meaningful) consistent programs
  - **TODO**: do placeholder replacement for composite programs (where a subtree is another program)
- **Program extractor**: extract base terms, primitives, sub programs, get corresponding type signature & count
- Draft EC process: loop through data point, do BFS, filter consistent programs, extract and add to library

## Discussion points

- Prior prob
- Df gets too large need an efficent way to read & write
- Run synthetic data experiments (on Eddie & hopefully Ebby). For now, the BFS result for the second data point (using generated programs in the program library) is pretty huge. Will consider using placeholder in this process.
  - Downweighting
  - Practical truncation
  - Compare with a pure generative process? (no enumeration)
- About the magic stone draft: recipient vs patient
