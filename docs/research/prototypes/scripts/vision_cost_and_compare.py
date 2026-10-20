"""Throwaway helper for the proto-vision-llm lane.

1. Estimates image input tokens per test image under the standard-res rule
   (long edge downscaled to 1568px, then ~width*height/750 tokens) and the
   high-res rule (long edge 2576px). Pricing from the claude-api skill table
   (cached 2026-10-06).
2. Compares two analysis JSONs (A vs B) on face-shape label, alternatives,
   and suggestion-name overlap using a crude token-set Jaccard.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

OUT = Path(sys.argv[1])
TESTDATA = Path(sys.argv[2])

# $/MTok input, output -- from claude-api skill SKILL.md table (cached 2026-10-06)
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}

def image_tokens(w, h, long_edge_cap, area_cap_px=1_150_000):
    # Long-edge cap, then an area cap (~1.15 MP standard-res), then ~1 token per 750 px.
    scale = min(1.0, long_edge_cap / max(w, h))
    if w * h * scale * scale > area_cap_px:
        scale = min(scale, (area_cap_px / (w * h)) ** 0.5)
    sw, sh = w * scale, h * scale
    return int(round(sw * sh / 750)), (int(sw), int(sh))

def estimate_images():
    rows = []
    for name in ["business-person.png", "portrait.jpg", "obama.jpg",
                 "faceparsing_116_ori.png", "alex-lacamoire.png"]:
        im = Image.open(TESTDATA / name)
        w, h = im.size
        std, std_dims = image_tokens(w, h, 1568)
        hi, hi_dims = image_tokens(w, h, 2576)
        rows.append((name, (w, h), std, std_dims, hi, hi_dims))
    return rows

def jaccard(a, b):
    ta = set(re.findall(r"[a-z]+", a.lower()))
    tb = set(re.findall(r"[a-z]+", b.lower()))
    stop = {"with", "a", "the", "and", "of", "on", "to", "at", "in", "no", "kept", "current", "cut"}
    ta -= stop; tb -= stop
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def compare(fa, fb):
    A = json.load(open(fa)); B = json.load(open(fb))
    print(f"\n== Compare {Path(fa).name} vs {Path(fb).name} ==")
    sa, sb = A["face"]["shape"], B["face"]["shape"]
    print(f"face shape: A={sa['label']} ({sa['confidence']})  B={sb['label']} ({sb['confidence']})  "
          f"agree={sa['label'].split()[0]==sb['label'].split()[0]}")
    print("A alternatives:", [x["label"] for x in sa.get("alternatives", [])])
    print("B alternatives:", [x["label"] for x in sb.get("alternatives", [])])
    for key in ["length", "texture", "density"]:
        va = A["current_hair"][key]; vb = B["current_hair"][key]
        la = va["label"] if isinstance(va, dict) else va
        lb = vb["label"] if isinstance(vb, dict) else vb
        print(f"hair.{key}: A={la!r}  B={lb!r}")
    for key in ["part", "color", "hairline"]:
        print(f"hair.{key}: A={A['current_hair'][key][:60]!r}  B={B['current_hair'][key][:60]!r}")
    pa = A["photo_quality"]; pb = B["photo_quality"]
    print("request_better_photo:", pa.get("request_better_photo"), pb.get("request_better_photo"))
    print("flags A:", {k: pa[k]["flag"] for k in ["lighting","pose","resolution","occlusion"]})
    print("flags B:", {k: pb[k]["flag"] for k in ["lighting","pose","resolution","occlusion"]})
    for section in ["suggestions", ("refine", "adjusted_suggestions")]:
        if isinstance(section, tuple):
            la = A[section[0]][section[1]]; lb = B[section[0]][section[1]]; label = "refined"
        else:
            la = A[section]; lb = B[section]; label = "initial"
        print(f"-- {label} suggestions --")
        matched = 0
        for s in la:
            best = max(lb, key=lambda t: jaccard(s["name"], t["name"]))
            j = jaccard(s["name"], best["name"])
            flag = "MATCH" if j >= 0.34 else "     "
            if j >= 0.34: matched += 1
            print(f"  {flag} {j:.2f}  A:{s['name'][:55]!r:60} B:{best['name'][:55]!r}")
        print(f"  overlap: {matched}/{len(la)} A-items have a B counterpart (jaccard>=0.34)")
        ba = sorted(s["boldness"] for s in la); bb = sorted(s["boldness"] for s in lb)
        print(f"  boldness spread A={ba} B={bb}")

if __name__ == "__main__":
    mode = sys.argv[3] if len(sys.argv) > 3 else "cost"
    if mode == "cost":
        rows = estimate_images()
        print(f"{'image':28} {'px':12} {'std_tok':>8} {'std_dims':>12} {'hi_tok':>8} {'hi_dims':>12}")
        tot_std = tot_hi = 0
        for name, px, std, sd, hi, hd in rows:
            tot_std += std; tot_hi += hi
            print(f"{name:28} {str(px):12} {std:8d} {str(sd):>12} {hi:8d} {str(hd):>12}")
        print(f"{'TOTAL(5)':28} {'':12} {tot_std:8d} {'':>12} {tot_hi:8d}")
        print("\nmean std tokens/image:", tot_std / len(rows))
    else:
        compare(sys.argv[4], sys.argv[5])
