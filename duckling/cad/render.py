"""Render assembly previews from the exported STLs (matplotlib, no GPU)."""
import sys
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parent.parent
ASM = ROOT / "stl" / "assembly"
COL = {"yellow": "#f6c945", "orange": "#f28c28", "white": "#e8e8e8", "servo": "#3a6fd8"}
PARTS = {"chassis": "yellow", "shell": "yellow", "tray": "white", "leg_left": "yellow",
         "leg_right": "yellow", "foot_left": "orange", "foot_right": "orange",
         "head_base": "yellow", "head_shell": "yellow", "beak": "orange"}

def load(hide=()):
    out = []
    for name, c in PARTS.items():
        if name not in hide:
            out.append((trimesh.load(ASM / f"{name}.stl"), COL[c]))
    for p in sorted(ASM.glob("_servo*.stl")):
        out.append((trimesh.load(p), COL["servo"]))
    return out

def draw(meshes, elev, azim, path, title=""):
    fig = plt.figure(figsize=(7, 7), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)
    for m, c in meshes:
        tris = m.vertices[m.faces]
        shade = 0.45 + 0.55 * np.clip(m.face_normals @ light, 0, 1)
        base = np.array(matplotlib.colors.to_rgb(c))
        pc = Poly3DCollection(tris, facecolors=np.clip(base[None] * shade[:, None], 0, 1), linewidths=0)
        ax.add_collection3d(pc)
    allv = np.vstack([m.vertices for m, _ in meshes])
    mid = (allv.max(0) + allv.min(0)) / 2; r = (allv.max(0) - allv.min(0)).max() / 2
    ax.set_xlim(mid[0]-r, mid[0]+r); ax.set_ylim(mid[1]-r, mid[1]+r); ax.set_zlim(mid[2]-r, mid[2]+r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev, azim); ax.set_axis_off()
    ax.set_title(title)
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    out = ROOT / "renders"; out.mkdir(exist_ok=True)
    full = load()
    draw(full, 18, -50, out / "duckling_front34.png", "Duckling v0.1")
    draw(full, 10, -90, out / "duckling_side.png", "side")
    draw(full, 5, 0, out / "duckling_front.png", "front")
    draw(load(hide=("shell", "head_shell", "beak")), 25, -60, out / "duckling_internals.png", "internals (shell hidden)")
