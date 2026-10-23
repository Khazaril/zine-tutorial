"""Sweep hips/ankles through the gait range and look for collisions."""
from duckling import *
from build123d import Pos, Rot
P = {k: v[0] for k, v in parts().items()}
def pose(side, hip, ankle):
    foot_ = Pos(0, side*HIP_Y, ANKLE_Z) * Rot(ankle, 0, 0) * Pos(0, -side*HIP_Y, -ANKLE_Z) * P["foot_left" if side > 0 else "foot_right"]
    leg = P["leg_left" if side > 0 else "leg_right"]
    hipT = Pos(0, side*HIP_Y, 0) * Rot(0, 0, hip) * Pos(0, -side*HIP_Y, 0)
    return hipT * leg, hipT * foot_
worst = 0
for hL, hR, aL, aR in [(30,30,30,30),(-30,-30,-30,-30),(30,-30,30,-30),(-30,30,-30,30),(30,30,-30,30),(0,0,35,-35),(0,0,-35,35)]:
    lL, fL = pose(1, hL, aL); lR, fR = pose(-1, hR, aR)
    pairs = {"legL-chassis": (lL, P["chassis"]), "legR-chassis": (lR, P["chassis"]),
             "footL-legL": (fL, lL), "footR-legR": (fR, lR), "footL-footR": (fL, fR),
             "legL-legR": (lL, lR), "footL-chassis": (fL, P["chassis"])}
    for n, (a, b) in pairs.items():
        v = (a & b).volume
        if v > 0.5:
            print(f"hips {hL:+},{hR:+} ankles {aL:+},{aR:+}: {n} {v:.0f} mm3"); worst += 1
print("motion clashes:", worst)
