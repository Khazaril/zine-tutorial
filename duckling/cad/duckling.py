"""Duckling v0.1 - parametric CAD (build123d).

World frame: X forward (beak), Y left, Z up. Units: mm.
Run:  python3 duckling.py   -> writes STLs to ../stl/

Every servo pocket is built from one SG90/MG90S model (servo_* constants), so
if your servos measure differently, change them here and re-export.
"""
from pathlib import Path
from build123d import (Box, Cylinder, Sphere, Polygon, extrude, scale, mirror,
                       Pos, Rot, Plane, Align, Part, export_stl)

OUT = Path(__file__).resolve().parent.parent / "stl"
C = (Align.CENTER, Align.CENTER, Align.CENTER)
MIN = (Align.MIN, Align.MIN, Align.MIN)

# ---------------------------------------------------------------- tolerances
CLR = 0.25          # pocket clearance per side (tuned for Bambu A1, 0.4 nozzle)

# ------------------------------------------- SG90 / MG90S, local servo frame
# Origin on the shaft axis at the servo's bottom face; shaft points +Z,
# the body's long axis is X and extends towards -X from the shaft.
S_L, S_W, S_H = 22.8, 12.4, 22.7   # body
S_SHAFT_OFF = 5.6                  # shaft axis to body centre (along X)
S_TAB_L, S_TAB_Z0, S_TAB_Z1 = 32.4, 15.6, 18.1
S_TAB_HOLE = 13.9                  # tab screw holes from body centre
S_BOSS_TOP = 26.7                  # top of the round boss under the spline
S_SPLINE_TOP = 29.7

def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)

def servo_model():
    """Visual SG90 for renders / interference checks."""
    cx = -S_SHAFT_OFF
    body = box(cx - S_L/2, cx + S_L/2, -S_W/2, S_W/2, 0, S_H)
    tabs = box(cx - S_TAB_L/2, cx + S_TAB_L/2, -S_W/2, S_W/2, S_TAB_Z0, S_TAB_Z1)
    boss = Pos(0, 0, S_H) * Cylinder(5.9, S_BOSS_TOP - S_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    spline = Pos(0, 0, S_BOSS_TOP) * Cylinder(2.4, S_SPLINE_TOP - S_BOSS_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body + tabs + boss + spline

# Servo pocket extents in the local frame (with clearance)
P_BX0, P_BX1 = -S_SHAFT_OFF - S_L/2 - CLR, -S_SHAFT_OFF + S_L/2 + CLR
P_TX0, P_TX1 = -S_SHAFT_OFF - S_TAB_L/2 - CLR, -S_SHAFT_OFF + S_TAB_L/2 + CLR
P_W = S_W/2 + CLR
TAB_REST = 2.5                      # plastic the tabs screw into

def servo_cut():
    """Pocket for a servo inserted from below (-Z), tabs stop on a ledge."""
    body = box(P_BX0, P_BX1, -P_W, P_W, -50, 60)
    tabs = box(P_TX0, P_TX1, -P_W, P_W, -50, S_TAB_Z1)
    holes = Part()
    for dx in (-S_TAB_HOLE, S_TAB_HOLE):
        holes += Pos(-S_SHAFT_OFF + dx, 0, S_TAB_Z1) * Cylinder(0.9, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body + tabs + holes

# ------------------------------------------------------------- servo horns
HORN_HUB_D = 7.8
HORN_ARM_W = 6.4
HORN_DEPTH = 4.0
HORN_FLOOR = 2.5
HORN_SCREW_D = 2.4

def horn_pocket(arm_len_pos, arm_len_neg, along="X"):
    """Pocket opening towards -Z from z=0, going up to +HORN_DEPTH.
    arm_len_* = how far the arm slot reaches from the hub centre each way."""
    hub = Cylinder(HORN_HUB_D/2, HORN_DEPTH + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    arm = box(-arm_len_neg, arm_len_pos, -HORN_ARM_W/2, HORN_ARM_W/2, 0, HORN_DEPTH)
    if along == "Y":
        arm = Rot(0, 0, 90) * arm
    screw = Cylinder(HORN_SCREW_D/2, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, -0.01) * (hub + arm + screw)

# =================================================================== layout
HIP_Y = 25.0               # hip shaft distance from centreline
DECK_T = 3.0
BODY_A, BODY_B, BODY_C = 50.0, 40.0, 60.0   # body ellipsoid semi-axes
WALL = 2.0
SHELL_Z0 = DECK_T

# hip servo: inverted (shaft down), tabs resting on the deck top
HIP_SERVO_Z = DECK_T + S_TAB_Z1          # world z of the servo's bottom face
def hip_loc(side):                         # local servo frame -> world
    return Pos(0, side * HIP_Y, HIP_SERVO_Z) * Rot(180, 0, 0)
HIP_BOSS_Z = HIP_SERVO_Z - S_BOSS_TOP     # = -5.6
LEG_TOP_Z = HIP_BOSS_Z - 0.9

# --------------------------------------------------------------------- leg
# Leg = holder block for the ankle servo. The servo stands upright with its
# shaft near the BOTTOM of the leg (low ankle pivot = small sideways foot swing)
# and pointing backwards (-X).
LEG_Y_HALF = 9.5
LEG_X_HORN = P_TX0 - HORN_DEPTH - HORN_FLOOR      # local x of the hip-horn face (top)
LEG_X_FAR = P_TX1 + 3.0                            # local x of the bottom face
LEG_Z1 = S_TAB_Z1 + TAB_REST                       # local z (towards the foot)
HIP_SCREW_LZ = 9.5                                 # local z of the hip axis
LEG_FLANGE = 20.0                                  # hip horn flange half-length

def leg_local():
    blk = box(LEG_X_HORN, LEG_X_FAR, -LEG_Y_HALF, LEG_Y_HALF, 0, LEG_Z1)
    flange = box(LEG_X_HORN, P_TX0, -7, 7, HIP_SCREW_LZ - LEG_FLANGE, HIP_SCREW_LZ + LEG_FLANGE)
    leg = blk + flange
    leg -= servo_cut()
    # hip horn pocket on the top face, double-arm horn along the flange
    leg -= Pos(LEG_X_HORN, 0, HIP_SCREW_LZ) * Rot(0, 90, 0) * horn_pocket(18.5, 18.5, "X")
    # screwdriver access to the hip horn screw, through the bottom face
    leg -= Pos(LEG_X_FAR + 1, 0, HIP_SCREW_LZ) * Rot(0, -90, 0) * Cylinder(2.2, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return leg

ANKLE_Z = LEG_TOP_Z + LEG_X_HORN                   # world z of ankle axis
LEG_BOTTOM_Z = ANKLE_Z - LEG_X_FAR

def leg_loc(side):
    # local x -> world -Z, local y -> world -Y, local z -> world -X
    return Pos(HIP_SCREW_LZ, side * HIP_Y, ANKLE_Z) * Rot(180, 0, 0) * Rot(0, -90, 0)

ANKLE_BOSS_X = HIP_SCREW_LZ - S_BOSS_TOP           # world x of boss end

# -------------------------------------------------------------------- foot
FOOT_PLATE_X0 = ANKLE_BOSS_X - 1.6                 # front face of the plate
FOOT_PLATE_T = HORN_DEPTH + HORN_FLOOR
SOLE_T = 3.0
SOLE_TOP = LEG_BOTTOM_Z - 3.5
SOLE_Z0 = SOLE_TOP - SOLE_T

def foot(side):
    xb = FOOT_PLATE_X0 - FOOT_PLATE_T
    pts = [(xb, -9), (5, -11), (29, -12), (23, -5), (33, 0),
           (23, 5), (29, 12), (5, 11), (xb, 9)]
    sole = Pos(0, 0, SOLE_Z0) * extrude(Polygon(*pts, align=None), SOLE_T)
    plate = box(xb, FOOT_PLATE_X0, -9, 9, SOLE_Z0, ANKLE_Z + 8)
    f = sole + plate
    # single-arm horn pointing down, pocket faces forward (+X)
    pocket = Pos(FOOT_PLATE_X0, 0, ANKLE_Z) * Rot(0, -90, 0) * horn_pocket(0.5, 17.5, "X")
    f -= pocket
    # counterbore for the horn screw head at the back
    f -= Pos(xb - 0.01, 0, ANKLE_Z) * Rot(0, 90, 0) * Cylinder(2.6, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    f = Pos(0, side * HIP_Y, 0) * f        # feet are symmetric, no mirror needed
    return f

# ---------------------------------------------------------------- chassis
BOSS_PTS = [(30, 20), (30, -20), (-38, 10), (-38, -10)]   # shell screw bosses
TRAY_POSTS = [(25, 14), (25, -14), (-28, 16), (-28, -16)]
TRAY_Z = 27.0
SWITCH_POS = (-42, 0)

def chassis():
    deck = scale(Cylinder(1, DECK_T, align=(Align.CENTER, Align.CENTER, Align.MIN)), by=(BODY_A, BODY_B, 1))
    for s in (1, -1):
        deck -= hip_loc(s) * servo_cut()
    for x, y in BOSS_PTS:          # M3 clearance + head counterbore from below
        deck -= Pos(x, y, -1) * Cylinder(1.7, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
        deck -= Pos(x, y, -1) * Cylinder(3.1, 2.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in TRAY_POSTS:        # posts for the electronics tray
        deck += Pos(x, y, DECK_T) * Cylinder(3.0, TRAY_Z - DECK_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        deck -= Pos(x, y, TRAY_Z - 8) * Cylinder(0.9, 9, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # ankle-servo cable holes, just in front of each hip
    for side in (1, -1):
        deck -= Pos(15, side * HIP_Y, -1) * Cylinder(3.5, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # slide switch slot (SS12D00) - lever pokes out underneath
    deck -= Pos(*SWITCH_POS, -1) * Box(9.5, 4.5, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # battery holder locating rails
    for y in (11.2, -11.2):
        deck += box(-33, 40, y - 1, y + 1, DECK_T, DECK_T + 3)
    return deck

def tray():
    t = Pos(-3, 0, TRAY_Z) * scale(Cylinder(1, 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN)), by=(36, 27, 1))
    for x, y in TRAY_POSTS:
        t -= Pos(x, y, TRAY_Z - 1) * Cylinder(1.2, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in ((8, 0), (-20, 0)):  # wire pass-throughs
        t -= Pos(x, y, TRAY_Z - 1) * Box(14, 8, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return t

# ------------------------------------------------------------------- shell
NECK_X = 20.0
COLLAR_R = 22.0
COLLAR_CX = NECK_X - S_SHAFT_OFF - 3.0
COLLAR_TOP = SHELL_Z0 + BODY_C + 2.0
NECK_SERVO_Z = COLLAR_TOP - (S_TAB_Z1 + TAB_REST)   # servo bottom face (world)
def neck_loc():
    return Pos(NECK_X, 0, NECK_SERVO_Z)

def ellipsoid(a, b, c):
    return scale(Sphere(1), by=(a, b, c))

def shell():
    outer = Pos(0, 0, SHELL_Z0) * ellipsoid(BODY_A, BODY_B, BODY_C)
    # tail and wings
    outer += Pos(-46, 0, SHELL_Z0 + 34) * Rot(0, 35, 0) * ellipsoid(16, 9, 7)
    for s in (1, -1):
        outer += Pos(-6, s * 35, SHELL_Z0 + 24) * Rot(0, -12, 0) * ellipsoid(30, 7, 15)
    collar = Pos(COLLAR_CX, 0, SHELL_Z0 + 30) * Cylinder(COLLAR_R, COLLAR_TOP - SHELL_Z0 - 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    s = outer + collar
    s -= Pos(0, 0, SHELL_Z0) * ellipsoid(BODY_A - WALL, BODY_B - WALL, BODY_C - WALL)
    s -= box(-200, 200, -200, 200, -200, SHELL_Z0)          # flat bottom
    # screw bosses from the rim up into the dome
    for x, y in BOSS_PTS:
        b = Pos(x, y, SHELL_Z0) * Cylinder(3.5, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
        b &= Pos(0, 0, SHELL_Z0) * ellipsoid(BODY_A, BODY_B, BODY_C)
        b -= Pos(x, y, SHELL_Z0 - 1) * Cylinder(1.25, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
        s += b
    # neck servo pocket (inserted from inside, shaft up)
    s -= neck_loc() * servo_cut()
    # hollow the underside of the collar so the servo can be inserted
    s -= Pos(NECK_X, 0, SHELL_Z0) * box(P_TX0 - 1, P_TX1 + 1, -P_W - 1, P_W + 1, 0, NECK_SERVO_Z - SHELL_Z0)
    # head wire hole through the collar
    s -= Pos(COLLAR_CX, 13, SHELL_Z0) * Cylinder(3.5, 80, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # rear USB-C slots: charger (right) and ESP32 (left)
    for y in (-10, 12):
        s -= Pos(-50, y, TRAY_Z + 1) * Box(16, 12.5, 7.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # speaker grille on the back, behind the neck
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 5:
                s -= Pos(-22 + i * 4.2, j * 4.2, SHELL_Z0 + 30) * Cylinder(1.1, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s

# -------------------------------------------------------------------- head
HEAD_R, HEAD_WALL = 30.0, 2.0
HEAD_BOTTOM = NECK_SERVO_Z + S_BOSS_TOP + 0.9
HEAD_CZ = HEAD_BOTTOM + 18.0
HEAD_CX = NECK_X + 6.0
FACE_X = HEAD_CX + 21.0
SPLIT_Z = HEAD_BOTTOM + HORN_DEPTH + HORN_FLOOR
WIN_W, WIN_H, WIN_Z = 24.0, 13.0, HEAD_CZ + 4.0
BEAK_Z = HEAD_CZ - 10.0
# lip sits inside the shell's opening at the split plane
LIP_R = ((HEAD_R - HEAD_WALL) ** 2 - (HEAD_CZ - SPLIT_Z) ** 2) ** 0.5 - 0.3

def head_outer():
    h = Pos(HEAD_CX, 0, HEAD_CZ) * Sphere(HEAD_R)
    h -= box(FACE_X, 300, -100, 100, -100, 300)
    h -= box(-300, 300, -100, 100, -300, HEAD_BOTTOM)
    return h

def head_inner():
    h = Pos(HEAD_CX, 0, HEAD_CZ) * Sphere(HEAD_R - HEAD_WALL)
    h -= box(FACE_X - HEAD_WALL, 300, -100, 100, -100, 300)
    return h

def head_base():
    b = head_outer() & box(-300, 300, -100, 100, HEAD_BOTTOM, SPLIT_Z)
    # locating lip that slips inside the head shell
    lip_r = LIP_R
    lip = Pos(HEAD_CX, 0, SPLIT_Z) * Cylinder(lip_r, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lip -= Pos(HEAD_CX, 0, SPLIT_Z) * Cylinder(lip_r - 1.6, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lip -= box(FACE_X - HEAD_WALL - 0.3, 300, -100, 100, -100, 300)
    b += lip
    b -= Pos(NECK_X, 0, HEAD_BOTTOM) * horn_pocket(18.5, 18.5, "Y")
    b -= Pos(HEAD_CX - 14, 0, HEAD_BOTTOM - 1) * Cylinder(4.0, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # M2 screw holes through the lip (screwed from outside the shell)
    for s in (1, -1):
        b -= Pos(HEAD_CX, s * lip_r, SPLIT_Z + 1.5) * Rot(90, 0, 0) * Cylinder(0.8, 6, align=C)
    return b

def head_shell():
    h = head_outer() - head_inner()
    h -= box(-300, 300, -100, 100, -300, SPLIT_Z)
    h -= Pos(FACE_X, 0, WIN_Z) * Box(10, WIN_W, WIN_H, align=C)          # OLED window
    for s in (1, -1):
        h -= Pos(FACE_X, s * 6, BEAK_Z) * Rot(0, 90, 0) * Cylinder(1.65, 10, align=C)
    for s in (1, -1):
        h -= Pos(HEAD_CX, s * LIP_R, SPLIT_Z + 1.5) * Rot(90, 0, 0) * Cylinder(1.1, 12, align=C)
    return h

def beak():
    b = Pos(FACE_X + 7, 0, BEAK_Z) * ellipsoid(13, 13, 4.5)
    b -= box(-300, FACE_X, -100, 100, -100, 300)
    b -= box(-300, 300, -100, 100, -300, BEAK_Z - 2.0)   # flat bottom: prints without supports
    for s in (1, -1):
        b += Pos(FACE_X, s * 6, BEAK_Z) * Rot(0, -90, 0) * Cylinder(1.45, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b

# ================================================================== export
def parts():
    """name -> (solid in assembly position, print transform, colour)"""
    legL = leg_loc(1) * leg_local()
    legR = leg_loc(-1) * leg_local()
    return {
        "chassis":    (chassis(), "yellow"),
        "shell":      (shell(), "yellow"),
        "tray":       (tray(), "white"),
        "leg_left":   (legL, "yellow"),
        "leg_right":  (legR, "yellow"),
        "foot_left":  (foot(1), "orange"),
        "foot_right": (foot(-1), "orange"),
        "head_base":  (head_base(), "yellow"),
        "head_shell": (head_shell(), "yellow"),
        "beak":       (beak(), "orange"),
    }

def servos():
    return ([hip_loc(s) * servo_model() for s in (1, -1)]
            + [leg_loc(s) * servo_model() for s in (1, -1)]
            + [neck_loc() * servo_model()])

# How each part is laid on the A1 bed (applied to the assembly-positioned solid)
PRINT_ROT = {"leg_left": Rot(180, 0, 0), "leg_right": Rot(180, 0, 0)}

def for_print(name, solid):
    solid = PRINT_ROT.get(name, Rot(0, 0, 0)) * solid
    bb = solid.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * solid

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "assembly").mkdir(exist_ok=True)
    for name, (solid, colour) in parts().items():
        export_stl(solid, str(OUT / "assembly" / f"{name}.stl"))
        export_stl(for_print(name, solid), str(OUT / f"{name}.stl"))
        bb = solid.bounding_box().size
        print(f"{name:12s} {colour:7s} {solid.volume/1000:5.1f} cm3  {bb.X:5.1f} x {bb.Y:5.1f} x {bb.Z:5.1f} mm")
    for i, s in enumerate(servos()):
        export_stl(s, str(OUT / "assembly" / f"_servo{i}.stl"))
    print(f"height: {HEAD_CZ + HEAD_R - SOLE_Z0:.0f} mm")
