
# Meeting notes (2021-02-22)

Demo code: https://github.com/zhaobn/comlog/blob/main/demo.py

Chris sketches: https://www.overleaf.com/read/mydmcyqmpdrh

Bonan earlier notes: https://www.overleaf.com/read/wqdptkxvmynt

## Implemented
### Summary

- Define everything with `class`: base types, primitives, routers, programs
- Define `program.run([objs])` recursively => manage to run all the examples in Bonan & Chris' notes :white_check_mark:

### Not sure

- Hand-crafted functions for each primitive term. Should it be automated?
- Used lists to represent terms in a program. Other option: binary tree?
- Not much error-handling (should I worry about it?), e.g. when running a function, I'm not checking whether argument types satisfy the requirement from the function.

## To implement

- **Program generator**. How do I handle sampling the right type? Need a type calculator?
- How to **approximate posterior**? Not sure how version space works for now; start with whatever prior programs => posterior distribution over them? Basically `\propto P(d|h)P(h)`, if starting with a finite sample of `H`.
- How to **grow a library**? Add (which) subtrees to the library. Seems very much related with the type calculator.
