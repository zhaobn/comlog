
# Meeting notes (2021-05-31)

## Model updates

- Condition `col` accidentally learned the critical part of the ground truth
- Theoretically speaking, under current setup, ground-truth is not learnable, because none of the subparts can be composed from partial information
- To be able to learn the ground truth, here are several options
  - Present three rows (or columns) as sets, and then learn over the three sets
  - Enlarge depth = 3
  - Use type signature `obj->obj->num`
