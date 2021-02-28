
# Meeting notes (2021-02-22)

## Implemented

[Program generator](https://github.com/zhaobn/comlog/blob/main/get_programs.py): given a type signature (input types, output type) sample a program.

### Principles

- Right tree provides *one* argument for the corresponding left tree.
- A left node that has `n` input types should expand `n` times, each time the corresponding right tree fills a type in the left. This is right-associated.
- Whenever a left node has not been fully expanded, it can route any input variables to both sides.
- If a left node has been fully expanded, i.e. there is no unfilled input types, it stops. If there are still variables comming in (because of parent nodes), all of these variables are routed to the right.
- The type signature for any right tree is fully-defined: input types are what's being routed to the right, and output type is the one decided by the corresponding left tree.
- When the input type is empty, return a primitive base term (Red, Dotted, etc.).
- We can improve performance by using cached programs.

Therefore, we consider program generation with two functions recursively:

- `program_expansion`: expand a left tree until no unfilled input types.
- `program_generation`: for a given type signature generate a program. All the right trees are generated with this method.

### Steps

- Left tree: sample a program whose return type matches the current program, fully expand it until all input types are provided from corresponding right trees.
- When input contains variables and left tree has not been fully expanded, sample a router.
- Right tree: sample a program whose type signature matches the current setup.
- Do above steps recursively until a program is sampled or step exceeds max setup (`max_depth` = 5 in current implementation).

### Example

Generate a program for type signature `[['obj'],'obj']`, with an argument of type `'obj'`.

- `Left_1`: sample a program that the return type is `'obj'`. Got `obj, col -> obj` (`setColor`).
  - There is one free type in the left tree. Sample a router. Got `C`.
  - `Right_1`: sample a program with type signature `[[],'col']`. Got `Red`.
- `Left_2`: expand current left tree with one varible (coming from router `C`)
  - There is no more free spaces in the left tree, router can only be `B`.
  - `Right_2`: sample a program with type signature `[['obj'],'obj']`. Got `I`.
- Return program `[C [B setColor I] Red]`

## TODO

- Include full primitives into the starting library.

- **Find equivalent progrograms**
  - Liang: refactoring
  - DreamCoder: build version space
  - Brutal force: check input-output equivalence on an exhausive list of possible inputs (not scalable).
  - However, given our particular setup, we could try some sort of semantics check inspired by the brutal force method:
    - For programs that do not contain boolean checks, use abstract input to check program equivalence. Eg. use a stone xyzabc as input, and compare output status.
    - For programs that do contain boolean conditions, check both the booleans and return programs separately.

- Grow program library. This follows pretty straightforwardly once the equivalence problem is solved.
