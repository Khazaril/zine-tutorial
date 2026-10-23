"""Interference check between assembled parts and servo models."""
import itertools
from duckling import parts, servos
from build123d import Rot, Pos
P = {k: v[0] for k, v in parts().items()}
S = {f"servo{i}": s for i, s in enumerate(servos())}
items = {**P, **S}
bad = 0
for (a, A), (b, B) in itertools.combinations(items.items(), 2):
    if not A.bounding_box().overlaps(B.bounding_box()):
        continue
    v = (A & B).volume
    if v > 0.5:
        bad += 1
        print(f"CLASH {a:11s} x {b:11s} {v:8.1f} mm3")
print("clashes:", bad)
