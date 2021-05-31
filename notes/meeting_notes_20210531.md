
# Meeting notes (2021-05-31)

Stimuli summary: https://docs.google.com/presentation/d/1uTY-Tnpu7i1vSZGUGWzDuUZ6rHr-V6f_25ykbu_uYyY/edit?usp=sharing

## Model updates

Ground truth: `[BC,[B,addnn,getLength],[B,[addnn,-2],getEdge]]`

- Under current setup, ground truth can't really be learned from information presentation, because there is no partial information combo that gives rise to the subparts directly
- Modelwise, we could force learning the ground truth by perhaps:
  1. Enlarge depth = 3 (so that we included groud truth in the set). Or
  2. Use type signature `obj->obj->num` (include ground truth with depth = 2)
- One observation: condition `col` learned the critical part of the ground truth `[B,[addnn,-2],getEdge]` by accident
- For people, maybe we can present three rows (or columns) as three indpendent sets, and then encourage people to generalize over the three sets

## Experiment interface

See demo
