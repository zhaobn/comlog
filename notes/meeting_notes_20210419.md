# Meeting notes (2021-04-19)

## Updates

- **[Program library]** Extend primitives to include `isRed`, `isDotted` etc.
- **[Program library]** Use non-trivial boolean conditions. Instead of sampling from `[True, False]` for the `ifElse` program, use meaningful primitives like `isRed`.
- **[Program library]** Refactor `K` combinator. For a program `[KC, setColor, Red]` of type signature `obj -> obj -> obj`. refactor it to be `[C, setColor, Red]` of type signature `obj -> obj`.
- **Entropy** is not really applicable in our current setup as all the programs are determinstic - very program will determine one particular result object given a pair of agent and recipient.
- However, *data entropy* makes sense in terms of dis-ambiguity: some programs may make the same predictions given input data, and some data can distinguish these programs (see one-shot experiment example in the next section).

## Current experiments

### One-shot experiments

Given one data point, many programs are consistent with it, we rank them by complexity (as defined by the generative grammar).

| Task | Agent                                  | Recipient                          | Result                            | Winning Rule                                         |
|------|----------------------------------------|------------------------------------|-----------------------------------|------------------------------------------------------|
|    1 | Stone(Red,S1,Circle,S1,Dotted,S1)      | Stone(Red,S1,Circle,S1,Dotted,S1)  | Stone(Red,S1,Circle,S1,Dotted,S1) | `[BK,I,I]`; `[KB,I,I]`                               |
|    2 | Stone(Red,S1,Circle,S1,Dotted,S1)      | Stone(Blue,S1,Circle,S1,Dotted,S1) | Stone(Red,S1,Circle,S1,Dotted,S1) | `[BK,I,I]`                                           |
|    3 | Stone(Yellow,S1,Circle,S1,Dotted,S1)   | Stone(Blue,S1,Circle,S1,Dotted,S1) | Stone(Red,S1,Circle,S1,Dotted,S1) | `[KC,[B,setColor,I],Red]`; `[CK,[B,setColor,I],Red]` |
|    4 | Stone(Red,S1,Circle,S1,Dotted,S1)      | Stone(Blue,S2,Square,S1,Plain,S2)  | Stone(Red,S2,Square,S1,Plain,S2)  | `[CK,[B,setColor,I],Red]`                            |
|    5 | Stone(Yellow,S1,Circle,S1,Dotted,S1)   | Stone(Blue,S2,Square,S1,Plain,S2)  | Stone(Red,S2,Square,S1,Plain,S2)  | `[KC,[B,setColor,I],Red]`                            |
|    6 | Stone(Yellow,S2,Triangle,S1,Stripy,S1) | Stone(Blue,S2,Square,S1,Plain,S2)  | Stone(Red,S1,Circle,S1,Dotted,S1) | `[KK,I,Stone(Red,S1,Circle,S1,Dotted,S1)]`           |

### Conditionals

Target rule: Red agents make the recipient red

|   | Agent                                | Recipient                           | Result                              |
|---|--------------------------------------|-------------------------------------|-------------------------------------|
| 1 | Stone(Red,S1,Circle,S1,Dotted,S1)    | Stone(Yellow,S2,Square,S1,Plain,S1) | Stone(Red,S2,Square,S1,Plain,S1)    |
| 2 | Stone(Yellow,S1,Circle,S2,Dotted,S1) | Stone(Yellow,S2,Square,S1,Plain,S1) | Stone(Yellow,S2,Square,S1,Plain,S1) |
| 3 | Stone(Red,S1, Square,S1,Dotted,S2)   | Stone(Blue,S2,Square,S2,Dotted,S2)  | Stone(Red,S2,Square,S2,Dotted,S2)   |
| 4 | Stone(Red,S2,Circle,S1,Plain,S1)     | Stone(Blue,S1,Circle,S1,Plain,S2)   | Stone(Red,S1,Circle,S1,Plain,S2)    |
| 5 | Stone(Blue,S1,Square,S1,Dotted,S1)   | Stone(Blue,S1,Circle,S1,Plain,S2)   | Stone(Blue,S1,Circle,S1,Plain,S2)   |
| 6 | Stone(Blue,S2,Circle,S1,Plain,S2)    | Stone(Blue,S2,Square,S2,Dotted,S2)  | Stone(Blue,S2,Square,S2,Dotted,S2)  |

### Compositions

**Group 1**: Red agents make the recipient square

|   | Agent                                | Recipient                            | Result                              |
|---|--------------------------------------|--------------------------------------|-------------------------------------|
| 1 | Stone(Red,S1,Circle,S1,Dotted,S1)    | Stone(Yellow,S2,Circle,S1,Plain,S1)  | Stone(Yellow,S2,Square,S1,Plain,S1) |
| 2 | Stone(Red,S1,Circle,S1,Plain,S1)     | Stone(Blue,S1,Triangle,S1,Plain,S2)  | Stone(Blue,S1,Square,S1,Plain,S2)   |
| 3 | Stone(Red,S1, Square,S1,Dotted,S2)   | Stone(Blue,S2,Triangle,S1,Dotted,S2) | Stone(Blue,S2,Square,S1,Dotted,S2)  |
| 4 | Stone(Yellow,S1,Circle,S2,Dotted,S1) | Stone(Yellow,S2,Square,S1,Plain,S1)  | Stone(Yellow,S2,Square,S1,Plain,S1) |
| 5 | Stone(Blue,S1,Square,S1,Dotted,S1)   | Stone(Blue,S1,Circle,S1,Plain,S2)    | Stone(Blue,S1,Circle,S1,Plain,S2)   |
| 6 | Stone(Blue,S1,Circle,S1,Plain,S2)    | Stone(Blue,S2,Square,S1,Dotted,S2)   | Stone(Blue,S2,Square,S1,Dotted,S2)  |

**Group 2**: Redness determine recipients' size

|   | Agent                              | Recipient                           | Result                              |
|---|------------------------------------|-------------------------------------|-------------------------------------|
| 1 | Stone(Red,S2,Circle,S1,Dotted,S1)  | Stone(Yellow,S2,Square,S1,Plain,S1) | Stone(Yellow,S2,Square,S2,Plain,S1) |
| 2 | Stone(Red,S1,Circle,S1,Plain,S1)   | Stone(Blue,S1,Square,S1,Plain,S2)   | Stone(Blue,S1,Square,S1,Plain,S2)   |
| 3 | Stone(Red,S2, Square,S1,Dotted,S2) | Stone(Blue,S2,Square,S1,Dotted,S2)  | Stone(Blue,S2,Square,S2,Dotted,S2)  |
| 4 | Stone(Red,S1,Triangle,S1,Plain,S2) | Stone(Yellow,S2,Square,S2,Plain,S1) | Stone(Yellow,S2,Square,S1,Plain,S1) |
| 5 | Stone(Blue,S1,Square,S1,Dotted,S1) | Stone(Blue,S1,Circle,S1,Plain,S2)   | Stone(Blue,S1,Circle,S1,Plain,S2)   |
| 6 | Stone(Blue,S1,Circle,S1,Plain,S2)  | Stone(Blue,S2,Square,S1,Dotted,S2)  | Stone(Blue,S2,Square,S1,Dotted,S2)  |

(Sub-)Programs won:

- `[C,[B,setSize,I],S2]`
- `[BC,[B,setSize,I],getSaturation]`
- `[BC,[B,setSize,[C,[B,setSize,I],S2]],getSaturation]`

**Group mix**: mix data from Group 1 and Group 2, learn altogether

## Follow-up

- Ideas to collect data on "complexity of inference"
- Experiments that emphasize on sub-program reuse
