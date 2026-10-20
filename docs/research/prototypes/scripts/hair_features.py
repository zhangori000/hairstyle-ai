#!/usr/bin/env python
"""Describe the CURRENT hair from on-device outputs only: hair mask + landmarks -> color, length class,
volume, bangs, coverage. Throwaway heuristics; prints a table and writes out/hair_features.json."""
import sys, os, json, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mp_analyze as A
import mediapipe as mp

T = f'{A.ROOT}/testdata'
fl, hair, multi, fd, _ = A.build_models(4)
IMGS = ['portrait.jpg', 'business-person.png', 'biden.jpg', 'alex-lacamoire.png', 'faceparsing_116_ori.png',
        'extra/barbershop_15.png', 'extra/barbershop_117.png', 'extra/sadtalker_people_0.png', 'extra/sadtalker_art_5.png',
        'extra/openface_lennon1.jpg', 'extra/openface_clapton2.jpg', 'extra/openface_adams.jpg', 'extra/liveportrait_s1.jpg',
        'extra/liveportrait_s5.jpg', 'extra/liveportrait_s11.jpg', 'extra/liveportrait_s12.jpg', 'extra/dlib_tom_cruise.jpg',
        'extra/fr_kit_with_rose.jpg', 'extra/fr_johnsnow_test1.jpg', 'extra/gfpgan_blake_lively.jpg', 'extra/dlib_bald_guys.jpg',
        'extra/facealign_aflw.jpg', 'two_people.jpg']


def color_name(rgb):
    r, g, b = [float(v) for v in rgb]
    hsv = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV)[0, 0]
    lab = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2LAB)[0, 0]
    h, s, v = float(hsv[0]) * 2, float(hsv[1]) / 255, float(hsv[2]) / 255  # h in degrees
    L = float(lab[0]) * 100 / 255
    if s < 0.12 and L > 55: return 'grey/white', (h, s, v, L)
    if s < 0.18 and L > 35: return 'grey', (h, s, v, L)
    if L < 22: return 'black', (h, s, v, L)
    if L < 38: return 'dark brown', (h, s, v, L)
    if (h < 25 or h > 340) and s > 0.45: return 'red/auburn', (h, s, v, L)
    if L < 55: return 'brown', (h, s, v, L)
    if L < 68: return 'light brown/dark blonde', (h, s, v, L)
    return 'blonde', (h, s, v, L)


rows = []
for name in IMGS:
    rgb = A.load_rgb(f'{T}/{name}'); H, W = rgb.shape[:2]
    img = mp.Image(mp.ImageFormat.SRGB, rgb)
    r = fl.detect(img)
    hc = hair.segment(img).confidence_masks[1].numpy_view()[:, :, 0].copy()
    cat = multi.segment(img).category_mask.numpy_view()[:, :, 0].copy()
    hm = hc > 0.5
    lab, comps = A.hair_components(hm)
    for fi, lms in enumerate(r.face_landmarks):
        P = np.array([[l.x * W, l.y * H] for l in lms])
        x0, y0 = P.min(0); x1, y1 = P.max(0); fw, fh = x1 - x0, y1 - y0
        chin = P[152]; top = P[10]; face_len = np.linalg.norm(top - chin); C = np.linalg.norm(P[234] - P[454])
        # hair components overlapping the expanded head region
        sx0, sy0, sx1, sy1 = x0 - 0.7 * fw, y0 - 1.3 * fh, x1 + 0.7 * fw, y1 + 0.2 * fh
        sel = np.zeros_like(hm)
        for c in comps:
            if c['area'] < 0.002 * fw * fh: continue
            cx0, cy0, cx1, cy1 = c['x'], c['y'], c['x'] + c['w'], c['y'] + c['h']
            if min(cx1, sx1) > max(cx0, sx0) and min(cy1, sy1) > max(cy0, sy0):
                # keep only the part inside a generous window (hair can hang to the waist; other people's hair excluded sideways)
                comp = (lab == c['id'])
                win = np.zeros_like(hm); win[int(max(0, sy0)):H, int(max(0, x0 - 1.2 * fw)):int(min(W, x1 + 1.2 * fw))] = True
                sel |= comp & win
        area = int(sel.sum()); face_area = float(fw * fh)
        if area == 0:
            rows.append(dict(image=name, face=fi, hair_area_over_face_area=0.0, verdict='no hair detected (bald/very short/hat or model miss)'))
            print(f'{name[-26:]:28s} f{fi}  no hair detected'); continue
        ys, xs = np.where(sel)
        bottom = ys.max(); topy = ys.min()
        length_ratio = (bottom - chin[1]) / face_len           # how far below the chin the hair reaches, in face lengths
        height_ratio = (top[1] - topy) / face_len               # hair height above the mesh top
        width_ratio = (xs.max() - xs.min()) / C                 # widest hair extent over cheek width
        if length_ratio < -0.25: length = 'short (above jaw)'
        elif length_ratio < 0.15: length = 'chin-length / bob'
        elif length_ratio < 0.7: length = 'medium (neck/collar)'
        elif length_ratio < 1.4: length = 'long (shoulder/chest)'
        else: length = 'very long'
        # bangs: hair coverage of the forehead band between eyebrows (105/334 tops) and mesh top
        bx0, bx1 = int(P[105][0]), int(P[334][0]); by0, by1 = int(min(P[10][1], P[109][1])), int(min(P[105][1], P[334][1]))
        band = sel[max(0, by0):max(by0 + 1, by1), min(bx0, bx1):max(bx0, bx1) + 1]
        bangs = float(band.mean()) if band.size else 0.0
        # color: median of eroded hair pixels (avoid edge mixing), in the upper half of the hair (less shadowed)
        er = cv2.erode(sel.astype(np.uint8), np.ones((7, 7), np.uint8))
        ey, ex = np.where(er > 0)
        if ey.size > 50:
            keep = ey < np.percentile(ey, 60)
            med = np.median(rgb[ey[keep], ex[keep]], axis=0)
        else:
            med = np.median(rgb[ys, xs], axis=0)
        cname, (h, s, v, L) = color_name(med)
        vol = area / face_area
        row = dict(image=name, face=fi, hair_area_over_face_area=round(vol, 2), length_ratio_below_chin=round(float(length_ratio), 2), length=length,
                   height_above_mesh_top_over_face_len=round(float(height_ratio), 2), width_over_cheek=round(float(width_ratio), 2),
                   bangs_coverage_of_forehead_band=round(bangs, 2), bangs=('yes' if bangs > 0.5 else ('partial' if bangs > 0.2 else 'no')),
                   median_rgb=[int(v_) for v_ in med], color=cname, hsv_L=[round(h), round(s, 2), round(v, 2), round(L)])
        rows.append(row)
        print(f"{name[-26:]:28s} f{fi}  vol={vol:4.2f} len={length_ratio:+5.2f} {length:22s} top={height_ratio:4.2f} width={width_ratio:4.2f}x bangs={bangs:4.2f}({row['bangs']:7s}) color={cname:24s} rgb={row['median_rgb']} L={L:.0f} s={s:.2f}")
json.dump(rows, open(f'{A.OUT}/hair_features.json', 'w'), indent=1)
for x in (fl, hair, multi, fd): x.close()
