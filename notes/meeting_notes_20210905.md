
# Notes (2021-09-05)

## Model sketch

* Task: `obj -> num -> num`

* Primitives: `getDot [obj -> num]`, `getStripe [obj -> num]`, `add [num -> num -> num]`, `sub [num -> num -> num]`, `mult [num -> num -> num]`

* Ground truth: `SC ((BB (sub (BC (B mult I) getStripe))) getDot)`

* Under complex info
  * Give up
  * Allow exceptions
  * Go deeper
  * Introduce a `sign [obj -> (obj -> num -> num)_3]` primitive to stack up depth-1 programs:
    ```
                   SS
                  /  \
                 /    \
                /      \
               SS        BC
              / \        / \
             /   \       B  getDot
           SS     KB    / \
           /\     / \   sub I
          /  \   I   I
         /    \
        BK    BC
        /\    /\
    sign  I  B getDot
            / \
          add  I
    ```
