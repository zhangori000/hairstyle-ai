#!/usr/bin/env python
"""Throwaway prototype: MediaPipe Face Landmarker + Hair Segmenter + Selfie Multiclass on CPU.

Run with LD_LIBRARY_PATH pointing at stublibs/ (libEGL/libGLESv2 no-op stubs) because the
mediapipe 1.1.1 wheel links EGL/GLES unconditionally.

Outputs per image into OUT:
  <stem>_landmarks.png   tesselation + face oval + measurement lines + numbers
  <stem>_hair.png        hair segmenter mask as colored alpha composite (+ ambiguous band)
  <stem>_multiclass.png  selfie multiclass classes with legend
  <stem>_cropbox.png     head crop box (region we would send to a generator)
  <stem>_crop.png        the crop itself
  <stem>_sheet.png       contact sheet
  results.json           all numbers
Never prints image bytes.
"""
import os, sys, json, time, math, argparse, statistics
import numpy as np
import cv2
from PIL import Image as PILImage, ImageOps
import mediapipe as mp

vision = mp.tasks.vision
BaseOptions = mp.tasks.BaseOptions

ROOT = '<scratchpad>'
MODELS = f'{ROOT}/testdata/models'
OUT = f'{ROOT}/proto/out'

# --- landmark indices (MediaPipe Face Mesh canonical topology) ---------------------
IDX = {
    'chin': 152, 'forehead_top': 10, 'glabella': 9, 'nose_tip': 1,
    'cheek_l': 234, 'cheek_r': 454,          # widest points of the face oval (zygomatic / tragion level)
    'cheek2_l': 93, 'cheek2_r': 323,         # one step below on the oval
    'cheekbone_l': 116, 'cheekbone_r': 345,  # malar surface points (inside the oval)
    'jaw_l': 172, 'jaw_r': 397,              # gonion candidates (jaw angle)
    'jaw2_l': 58, 'jaw2_r': 288,             # alternative gonion candidates
    'temple_l': 54, 'temple_r': 284,         # upper temples
    'forehead_l': 103, 'forehead_r': 332,    # forehead width (upper)
    'forehead2_l': 67, 'forehead2_r': 297,   # forehead width (near mesh top)
    'eye_outer_l': 33, 'eye_outer_r': 263,
    'chin_l': 148, 'chin_r': 377,            # points flanking the chin (chin width)
    'chin2_l': 176, 'chin2_r': 400,
}
# ordered face oval (image-left side goes up from chin, over the top, down the right side)
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377,
             152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

MULTICLASS_PALETTE = {  # label index -> BGR
    0: (0, 0, 0),        # background
    1: (255, 0, 255),    # hair  (magenta)
    2: (0, 200, 255),    # body-skin (orange-ish)
    3: (0, 255, 255),    # face-skin (yellow)
    4: (255, 128, 0),    # clothes (blue)
    5: (0, 255, 0),      # others / accessories (green)
}


def load_rgb(path):
    im = PILImage.open(path)
    im = ImageOps.exif_transpose(im)
    im = im.convert('RGB')
    return np.ascontiguousarray(np.asarray(im))


def mp_image(rgb):
    return mp.Image(mp.ImageFormat.SRGB, rgb)


def build_models(num_faces, min_det=0.5):
    t0 = time.perf_counter()
    fl = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=f'{MODELS}/face_landmarker.task'),
        num_faces=num_faces, output_face_blendshapes=True, output_facial_transformation_matrixes=True,
        min_face_detection_confidence=min_det, min_face_presence_confidence=min_det))
    t1 = time.perf_counter()
    hair = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=f'{MODELS}/hair_segmenter.tflite'),
        output_confidence_masks=True, output_category_mask=True))
    t2 = time.perf_counter()
    multi = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=f'{MODELS}/selfie_multiclass_256x256.tflite'),
        output_confidence_masks=True, output_category_mask=True))
    t3 = time.perf_counter()
    fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=f'{MODELS}/blaze_face_short_range.tflite')))
    t4 = time.perf_counter()
    load_ms = {'face_landmarker': (t1 - t0) * 1e3, 'hair_segmenter': (t2 - t1) * 1e3,
               'selfie_multiclass': (t3 - t2) * 1e3, 'face_detector': (t4 - t3) * 1e3}
    return fl, hair, multi, fd, load_ms


def timed(fn, *a, repeats=3):
    ts = []
    out = None
    for _ in range(repeats):
        t = time.perf_counter()
        out = fn(*a)
        ts.append((time.perf_counter() - t) * 1e3)
    return out, statistics.median(ts), min(ts)


def rot_to_euler(R):
    # R: 3x3 rotation. yaw around y, pitch around x, roll around z (degrees). Convention for a camera-facing face.
    sy = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    if sy > 1e-6:
        pitch = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(-R[2, 0], sy)
        roll = math.atan2(R[1, 0], R[0, 0])
    else:
        pitch = math.atan2(-R[1, 2], R[1, 1]); yaw = math.atan2(-R[2, 0], sy); roll = 0
    return dict(pitch=math.degrees(pitch), yaw=math.degrees(yaw), roll=math.degrees(roll))


def angle_at(p, a, b):
    v1 = a - p; v2 = b - p
    c = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def walk_for_boundary(mask, start, direction, max_len, thresh=0.5, offsets=(0,), perp=None, width=1.0):
    """Walk from `start` along unit `direction` and return the distance to the first pixel where mask>thresh.
    Samples several parallel lines (offsets along `perp`, in px) and returns the median of the found ones."""
    H, W = mask.shape[:2]
    found = []
    for off in offsets:
        s = start + (perp * off if perp is not None else 0)
        d_found = None
        for d in range(0, int(max_len)):
            p = s + direction * d
            x, y = int(round(p[0])), int(round(p[1]))
            if x < 0 or y < 0 or x >= W or y >= H:
                break
            if mask[y, x] > thresh:
                d_found = d
                break
        if d_found is not None:
            found.append(d_found)
    if not found:
        return None, 0
    return float(statistics.median(found)), len(found)


# Ratios of MediaPipe's own canonical_face_model.obj with the same landmark pairs (computed in this prototype).
# The mesh's outer contour carries a strong template prior, so raw ratios cluster tightly around these values;
# we classify on deviation from canonical instead of on absolute anthropometric thresholds.
CANON = dict(LW_mesh=1.153, JC=0.775, FC=0.670, chinC=0.169, jaw_angle=132.2)


def classify_shape(m):
    """Rule-based face shape on canonical-relative ratios. Hand-chosen thresholds, NOT validated (n~25 sample faces).
    LW     = hairline-based face length / cheek width (length from hair mask, not the template)
    LW_rel = mesh length ratio / canonical;  JC_rel = jaw/cheek / canonical;  FC_rel = forehead/cheek / canonical
    dAng   = jaw angle - canonical jaw angle (negative = more angular)."""
    LW, LWr, JCr, FCr = m['LW'], m['LW_rel'], m['JC_rel'], m['FC_rel']
    dA = m['jaw_angle'] - CANON['jaw_angle']
    long_face = LW >= 1.55 or LWr >= 1.10
    short_face = LW <= 1.33 and LWr <= 0.98
    wide_jaw, narrow_jaw = JCr >= 1.05, JCr <= 0.97
    wide_forehead, narrow_forehead = FCr >= 1.06, FCr <= 0.97
    angular, soft = dA <= -6, dA >= 4
    why = f'LW={LW:.2f} LW_rel={LWr:.2f} JC_rel={JCr:.2f} FC_rel={FCr:.2f} dAng={dA:+.0f}'
    if wide_forehead and narrow_jaw:
        return 'heart', [f'forehead wider and jaw narrower than canonical ({why})']
    if narrow_forehead and narrow_jaw:
        return 'diamond', [f'forehead and jaw both narrower than canonical ({why})']
    if long_face and (wide_jaw or angular):
        return 'oblong', [f'long face with wide/angular jaw ({why})']
    if long_face:
        return 'oval-long', [f'long face, balanced widths ({why})']
    if short_face and (wide_jaw or angular):
        return 'square', [f'short face with wide/angular jaw ({why})']
    if short_face:
        return 'round', [f'short face with soft jaw ({why})']
    if wide_jaw and angular:
        return 'square', [f'wide angular jaw at medium length ({why})']
    if wide_jaw and not wide_forehead:
        return 'triangle', [f'jaw wider than canonical, forehead not ({why})']
    return 'oval', [f'medium length, widths within ~5% of canonical ({why})']


def row_run(mask_row, x_center, lo, hi):
    """Length of the contiguous True run in mask_row that contains x_center (searched within [lo, hi])."""
    W = mask_row.shape[0]
    xc = int(min(max(x_center, 0), W - 1))
    if not mask_row[xc]:
        # allow a small search for the nearest True pixel (hair/axis mismatch)
        for d in range(1, 12):
            if xc - d >= 0 and mask_row[xc - d]: xc = xc - d; break
            if xc + d < W and mask_row[xc + d]: xc = xc + d; break
        else:
            return 0
    l = xc
    while l - 1 >= max(0, int(lo)) and mask_row[l - 1]: l -= 1
    r = xc
    while r + 1 <= min(W - 1, int(hi)) and mask_row[r + 1]: r += 1
    return r - l + 1


def measure_face(lms, W, H, hair_conf, skin_conf, cat=None):
    """lms: list of NormalizedLandmark (478). Returns dict of measurements in px and ratios."""
    P = np.array([[l.x * W, l.y * H] for l in lms], dtype=np.float64)           # 2D px
    P3 = np.array([[l.x * W, l.y * H, l.z * W] for l in lms], dtype=np.float64)  # z is roughly in x-scale units

    def d2(a, b): return float(np.linalg.norm(P[IDX[a]] - P[IDX[b]]))
    def d3(a, b): return float(np.linalg.norm(P3[IDX[a]] - P3[IDX[b]]))

    m = {}
    m['mesh_length'] = d2('forehead_top', 'chin')           # top of mesh (upper forehead) to chin
    m['cheek_width'] = d2('cheek_l', 'cheek_r')
    m['cheek_width_3d'] = d3('cheek_l', 'cheek_r')
    m['cheekbone_width'] = d2('cheekbone_l', 'cheekbone_r')
    m['jaw_width'] = d2('jaw_l', 'jaw_r')
    m['jaw_width_3d'] = d3('jaw_l', 'jaw_r')
    m['jaw2_width'] = d2('jaw2_l', 'jaw2_r')
    m['forehead_width'] = d2('forehead_l', 'forehead_r')
    m['forehead_width_3d'] = d3('forehead_l', 'forehead_r')
    m['temple_width'] = d2('temple_l', 'temple_r')
    m['forehead2_width'] = d2('forehead2_l', 'forehead2_r')
    m['chin_width'] = d2('chin_l', 'chin_r')
    m['eye_outer_dist'] = d2('eye_outer_l', 'eye_outer_r')

    # jaw angle at gonion candidates: angle between (gonion->cheek) and (gonion->chin)
    chin = P[IDX['chin']]
    angs = {}
    for side in ('l', 'r'):
        g = P[IDX[f'jaw_{side}']]; c = P[IDX[f'cheek_{side}']]
        angs[f'jaw_angle_{side}'] = angle_at(g, c, chin)
        g2 = P[IDX[f'jaw2_{side}']]
        angs[f'jaw2_angle_{side}'] = angle_at(g2, c, chin)
    m.update(angs)
    m['jaw_angle'] = (angs['jaw_angle_l'] + angs['jaw_angle_r']) / 2
    m['jaw2_angle'] = (angs['jaw2_angle_l'] + angs['jaw2_angle_r']) / 2

    # data-driven gonion: the oval point between chin and cheek with the smallest interior angle (sharpest turn)
    for side, seq in (('l', [152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234]),
                      ('r', [152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454])):
        best = None
        for k in range(2, len(seq) - 2):
            a = angle_at(P[seq[k]], P[seq[0]], P[seq[-1]])
            if best is None or a < best[1]:
                best = (seq[k], a)
        m[f'gonion_auto_{side}'] = best[0]; m[f'gonion_auto_angle_{side}'] = best[1]

    # face axis: chin -> forehead_top unit vector; perpendicular for parallel sampling lines
    top = P[IDX['forehead_top']]
    axis = top - chin; axis_len = np.linalg.norm(axis); u = axis / (axis_len + 1e-9)
    perp = np.array([-u[1], u[0]])
    offs = [o * m['cheek_width'] for o in (-0.12, -0.06, 0.0, 0.06, 0.12)]
    # hairline: first hair pixel above the mesh top along the face axis (within 0.9 * mesh length)
    hd, nfound = walk_for_boundary(hair_conf, top, u, 0.9 * m['mesh_length'], 0.5, offs, perp)
    m['hairline_found_lines'] = nfound
    if hd is not None:
        m['hairline_offset_from_mesh_top'] = hd
        m['face_length_hairline'] = m['mesh_length'] + hd
        m['face_length_source'] = 'hair_mask'
    else:
        # bald / hat / undetected hair: use end of skin (face-skin OR body-skin) along the axis instead
        sd, nf2 = walk_for_boundary(1.0 - skin_conf, top, u, 0.9 * m['mesh_length'], 0.5, offs, perp)
        if sd is not None:
            m['hairline_offset_from_mesh_top'] = sd
            m['face_length_hairline'] = m['mesh_length'] + sd * 0.75  # crown is above the hairline-equivalent; damp
            m['face_length_source'] = 'skin_end_damped'
        else:
            m['hairline_offset_from_mesh_top'] = 0.12 * m['mesh_length']
            m['face_length_hairline'] = m['mesh_length'] * 1.12
            m['face_length_source'] = 'fallback_1.12x_mesh'
    L = m['face_length_hairline']; C = m['cheek_width']
    m['LW'] = L / C
    m['LW_mesh'] = m['mesh_length'] / C
    m['JC'] = m['jaw_width'] / C
    m['FC'] = m['forehead_width'] / C
    m['chinC'] = m['chin_width'] / C
    m['LW_rel'] = m['LW_mesh'] / CANON['LW_mesh']
    m['JC_rel'] = m['JC'] / CANON['JC']
    m['FC_rel'] = m['FC'] / CANON['FC']
    m['chinC_rel'] = m['chinC'] / CANON['chinC']
    m['jaw_angle_delta'] = m['jaw_angle'] - CANON['jaw_angle']

    # silhouette widths from the multiclass segmentation (256x256 model, so coarse): contiguous run of
    # face-skin pixels / of any-person pixels on the image row through each landmark pair
    if cat is not None:
        skin = (cat == 3)
        person = (cat != 0)
        hairm = (cat == 1)
        xc_axis = lambda y: float(chin[0] + u[0] * ((y - chin[1]) / (u[1] + 1e-9)))  # x of the face axis at row y
        for name, (a, b) in (('jaw', ('jaw_l', 'jaw_r')), ('cheek', ('cheek_l', 'cheek_r')), ('forehead', ('forehead_l', 'forehead_r'))):
            y = int(round((P[IDX[a]][1] + P[IDX[b]][1]) / 2)); y = min(max(y, 0), H - 1)
            xc = xc_axis(y)
            m[f'sil_skin_{name}'] = row_run(skin[y], xc, xc - 1.3 * C, xc + 1.3 * C)
            m[f'sil_person_{name}'] = row_run(person[y], xc, xc - 2.0 * C, xc + 2.0 * C)
        # hair volume: widest person-run in the band between the mesh top and the top of the hair
        ys = np.where(hairm.any(axis=1))[0]
        if ys.size:
            y_top = int(max(0, ys.min()))
            y_mesh_top = int(top[1])
            widest = 0
            for y in range(y_top, max(y_top + 1, y_mesh_top), max(1, (y_mesh_top - y_top) // 20 or 1)):
                xc = xc_axis(y)
                widest = max(widest, row_run(person[y], xc, xc - 2.5 * C, xc + 2.5 * C))
            m['sil_hair_widest_above_forehead'] = widest
            m['hair_height_above_mesh_top'] = float(y_mesh_top - y_top)
        else:
            m['sil_hair_widest_above_forehead'] = 0; m['hair_height_above_mesh_top'] = 0.0
        m['sil_skin_jaw_over_cheek'] = (m['sil_skin_jaw'] / m['sil_skin_cheek']) if m['sil_skin_cheek'] else None
        m['sil_skin_forehead_over_cheek'] = (m['sil_skin_forehead'] / m['sil_skin_cheek']) if m['sil_skin_cheek'] else None
        m['sil_person_cheek_over_landmark_cheek'] = m['sil_person_cheek'] / C
        m['sil_hair_widest_over_cheek'] = m['sil_hair_widest_above_forehead'] / C
    m['shape'], m['shape_reasons'] = classify_shape(m)
    m['_P'] = P; m['_u'] = u; m['_hairline_pt'] = (top + u * m['hairline_offset_from_mesh_top']).tolist()
    return m


def draw_landmarks(rgb, faces_lm, measures, out_path):
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    H, W = bgr.shape[:2]
    overlay = bgr.copy()
    tess = vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION
    for lms, m in zip(faces_lm, measures):
        P = m['_P']
        for c in tess:
            a = tuple(int(v) for v in P[c.start]); b = tuple(int(v) for v in P[c.end])
            cv2.line(overlay, a, b, (200, 200, 200), 1, cv2.LINE_AA)
    bgr = cv2.addWeighted(overlay, 0.35, bgr, 0.65, 0)
    th = max(1, int(round(min(W, H) / 400)))
    for lms, m in zip(faces_lm, measures):
        P = m['_P']
        pts = np.array([P[i] for i in FACE_OVAL], dtype=np.int32)
        cv2.polylines(bgr, [pts], True, (0, 255, 0), th, cv2.LINE_AA)
        for (a, b, col) in (('cheek_l', 'cheek_r', (0, 0, 255)), ('jaw_l', 'jaw_r', (255, 0, 0)),
                            ('forehead_l', 'forehead_r', (0, 255, 255)), ('forehead_top', 'chin', (255, 0, 255))):
            cv2.line(bgr, tuple(int(v) for v in P[IDX[a]]), tuple(int(v) for v in P[IDX[b]]), col, th + 1, cv2.LINE_AA)
        hp = tuple(int(v) for v in m['_hairline_pt'])
        cv2.circle(bgr, hp, th * 4, (255, 255, 0), -1, cv2.LINE_AA)
        cv2.line(bgr, hp, tuple(int(v) for v in P[IDX['forehead_top']]), (255, 255, 0), th, cv2.LINE_AA)
        for s in ('l', 'r'):
            cv2.circle(bgr, tuple(int(v) for v in P[m[f'gonion_auto_{s}']]), th * 3, (0, 165, 255), -1, cv2.LINE_AA)
        for i in (IDX['chin'], IDX['forehead_top'], IDX['cheek_l'], IDX['cheek_r'], IDX['jaw_l'], IDX['jaw_r']):
            cv2.circle(bgr, tuple(int(v) for v in P[i]), th * 2, (255, 255, 255), -1, cv2.LINE_AA)
    # numbers: one text panel per face, stacked at the top-left, on a dark background strip
    fs = max(0.45, min(W, H) / 1100); lh = int(30 * fs)
    y = 6
    for fi, m in enumerate(measures):
        lines = [f"face{fi} {m['shape']}  LW={m['LW']:.2f} LWrel={m['LW_rel']:.2f} JCrel={m['JC_rel']:.2f} FCrel={m['FC_rel']:.2f} jaw={m['jaw_angle']:.0f}",
                 f"  len={m['face_length_hairline']:.0f}px ({m['face_length_source']}) yaw={m['pose']['yaw']:.0f} pitch={m['pose']['pitch']:.0f} roll={m['pose']['roll']:.0f}"]
        for s in lines:
            (tw, _), _ = cv2.getTextSize(s, cv2.FONT_HERSHEY_SIMPLEX, fs, 1)
            cv2.rectangle(bgr, (4, y), (min(W - 1, 8 + tw), y + lh), (0, 0, 0), -1)
            cv2.putText(bgr, s, (6, y + lh - 8), cv2.FONT_HERSHEY_SIMPLEX, fs, (255, 255, 255), 1, cv2.LINE_AA)
            y += lh
    cv2.imwrite(out_path, bgr)
    return bgr


def draw_hair(rgb, hair_conf, out_path):
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    mask = hair_conf > 0.5
    band = (hair_conf > 0.2) & (hair_conf < 0.8)
    color = np.zeros_like(bgr); color[:, :] = (255, 0, 255)
    out = bgr.copy()
    a = 0.55
    out[mask] = (bgr[mask] * (1 - a) + color[mask] * a).astype(np.uint8)
    out[band] = (out[band] * 0.4 + np.array([0, 255, 255]) * 0.6).astype(np.uint8)
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, cnts, -1, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out_path, out)
    return out


def draw_multiclass(rgb, cat, labels, out_path):
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    color = np.zeros_like(bgr)
    for k, col in MULTICLASS_PALETTE.items():
        color[cat == k] = col
    out = cv2.addWeighted(bgr, 0.45, color, 0.55, 0)
    H, W = out.shape[:2]
    fs = max(0.4, min(W, H) / 1400); lh = int(26 * fs * 1.5)
    for k, name in enumerate(labels):
        y = 10 + k * lh
        cv2.rectangle(out, (10, y), (10 + lh - 6, y + lh - 6), MULTICLASS_PALETTE.get(k, (255, 255, 255)), -1)
        cv2.putText(out, f'{k} {name}', (10 + lh, y + lh - 10), cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, f'{k} {name}', (10 + lh, y + lh - 10), cv2.FONT_HERSHEY_SIMPLEX, fs, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out_path, out)
    return out


def hair_components(hair_mask):
    n, lab, stats, cent = cv2.connectedComponentsWithStats(hair_mask.astype(np.uint8), connectivity=8)
    comps = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        comps.append(dict(id=i, x=int(x), y=int(y), w=int(w), h=int(h), area=int(area)))
    return lab, comps


def crop_box_for_face(P, hair_mask, lab, comps, W, H, margin=0.25):
    """Union of face landmark bbox and hair components overlapping an expanded face bbox; add margin; square; clamp."""
    x0, y0 = P.min(axis=0); x1, y1 = P.max(axis=0)
    fw, fh = x1 - x0, y1 - y0
    # expanded search region: up by 1.2 face heights, sideways by 0.6 face widths, down by 0.3
    sx0, sy0, sx1, sy1 = x0 - 0.6 * fw, y0 - 1.2 * fh, x1 + 0.6 * fw, y1 + 0.3 * fh
    total_hair = sum(c['area'] for c in comps) or 1
    ux0, uy0, ux1, uy1 = x0, y0, x1, y1
    used = []
    for c in comps:
        if c['area'] < 0.01 * total_hair:
            continue
        cx0, cy0, cx1, cy1 = c['x'], c['y'], c['x'] + c['w'], c['y'] + c['h']
        ix0, iy0, ix1, iy1 = max(cx0, sx0), max(cy0, sy0), min(cx1, sx1), min(cy1, sy1)
        if ix1 > ix0 and iy1 > iy0:
            # only take the part of the component inside a generous window (long hair can run to the frame bottom)
            ys, xs = np.where(lab == c['id'])
            sel = (xs >= sx0 - 0.5 * fw) & (xs <= sx1 + 0.5 * fw) & (ys >= sy0 - 0.5 * fh) & (ys <= y1 + 1.0 * fh)
            if sel.any():
                ux0 = min(ux0, xs[sel].min()); ux1 = max(ux1, xs[sel].max())
                uy0 = min(uy0, ys[sel].min()); uy1 = max(uy1, ys[sel].max())
                used.append(c['id'])
    bw, bh = ux1 - ux0, uy1 - uy0
    cx, cy = (ux0 + ux1) / 2, (uy0 + uy1) / 2
    side = max(bw, bh) * (1 + 2 * margin)
    # bias the square downward a little so shoulders are included (generators like neck context)
    cy += 0.06 * side
    bx0, by0 = int(max(0, cx - side / 2)), int(max(0, cy - side / 2))
    bx1, by1 = int(min(W, cx + side / 2)), int(min(H, cy + side / 2))
    return dict(x0=bx0, y0=by0, x1=bx1, y1=by1, w=bx1 - bx0, h=by1 - by0, hair_components=used,
                face_bbox=[float(x0), float(y0), float(x1), float(y1)])


def contact_sheet(panels, out_path, height=480):
    ims = []
    for p in panels:
        h, w = p.shape[:2]
        s = height / h
        ims.append(cv2.resize(p, (int(w * s), height), interpolation=cv2.INTER_AREA))
    sheet = np.concatenate(ims, axis=1)
    cv2.imwrite(out_path, sheet)


def analyze(path, models, num_faces_hint, results):
    fl, hair, multi, fd = models
    stem = os.path.splitext(os.path.basename(path))[0]
    rgb = load_rgb(path)
    H, W = rgb.shape[:2]
    img = mp_image(rgb)
    rec = dict(image=os.path.basename(path), width=W, height=H, timings_ms={})

    r_lm, t_lm, tmin_lm = timed(fl.detect, img)
    r_hair, t_hair, tmin_hair = timed(hair.segment, img)
    r_multi, t_multi, tmin_multi = timed(multi.segment, img)
    r_fd, t_fd, tmin_fd = timed(fd.detect, img)
    rec['timings_ms'] = dict(face_landmarker=round(t_lm, 1), hair_segmenter=round(t_hair, 1),
                             selfie_multiclass=round(t_multi, 1), face_detector=round(t_fd, 1),
                             face_landmarker_min=round(tmin_lm, 1), hair_segmenter_min=round(tmin_hair, 1),
                             selfie_multiclass_min=round(tmin_multi, 1), face_detector_min=round(tmin_fd, 1))

    # hair segmenter: confidence masks are [background, hair]? check labels
    hair_labels = list(hair.labels)
    hair_idx = hair_labels.index('hair') if 'hair' in hair_labels else 1
    hair_conf = r_hair.confidence_masks[hair_idx].numpy_view()[:, :, 0].copy()
    multi_labels = list(multi.labels)
    cat = r_multi.category_mask.numpy_view()[:, :, 0].copy()
    mc_conf = [m.numpy_view()[:, :, 0].copy() for m in r_multi.confidence_masks]
    mc_hair_idx = multi_labels.index('hair') if 'hair' in multi_labels else 1
    skin_idx = [i for i, n in enumerate(multi_labels) if 'skin' in n]
    skin_conf = np.max(np.stack([mc_conf[i] for i in skin_idx]), axis=0) if skin_idx else np.zeros_like(hair_conf)
    rec['hair_segmenter_labels'] = hair_labels
    rec['multiclass_labels'] = multi_labels

    hair_mask = hair_conf > 0.5
    lab, comps = hair_components(hair_mask)
    comps_sorted = sorted(comps, key=lambda c: -c['area'])
    big = [c for c in comps_sorted if c['area'] >= 0.005 * max(1, hair_mask.sum())]
    mc_hair = cat == mc_hair_idx
    inter = np.logical_and(hair_mask, mc_hair).sum(); union = np.logical_or(hair_mask, mc_hair).sum()
    band = ((hair_conf > 0.2) & (hair_conf < 0.8)).sum()
    rec['hair_mask'] = dict(
        area_fraction=round(float(hair_mask.mean()), 4),
        n_components_total=len(comps), n_components_significant=len(big),
        largest_component_fraction=round(float(big[0]['area'] / max(1, hair_mask.sum())), 3) if big else 0.0,
        ambiguous_band_fraction_of_hair=round(float(band / max(1, hair_mask.sum())), 3),
        mean_conf_inside=round(float(hair_conf[hair_mask].mean()), 3) if hair_mask.any() else 0.0,
        touches_border=dict(top=bool(hair_mask[0].any()), bottom=bool(hair_mask[-1].any()),
                            left=bool(hair_mask[:, 0].any()), right=bool(hair_mask[:, -1].any())),
        iou_vs_multiclass_hair=round(float(inter / max(1, union)), 3),
        multiclass_hair_area_fraction=round(float(mc_hair.mean()), 4),
        multiclass_class_fractions={multi_labels[k]: round(float((cat == k).mean()), 4) for k in range(len(multi_labels))},
    )
    rec['face_detector'] = [dict(x=d.bounding_box.origin_x, y=d.bounding_box.origin_y, w=d.bounding_box.width,
                                 h=d.bounding_box.height, score=round(d.categories[0].score, 3)) for d in r_fd.detections]
    rec['n_faces_landmarker'] = len(r_lm.face_landmarks)

    faces = []
    measures = []
    for fi, lms in enumerate(r_lm.face_landmarks):
        m = measure_face(lms, W, H, hair_conf, skin_conf, cat)
        M = r_lm.facial_transformation_matrixes[fi] if r_lm.facial_transformation_matrixes else np.eye(4)
        m['pose'] = {k: round(v, 1) for k, v in rot_to_euler(np.array(M)[:3, :3]).items()}
        bs = {c.category_name: round(c.score, 3) for c in r_lm.face_blendshapes[fi]} if r_lm.face_blendshapes else {}
        top_bs = sorted(bs.items(), key=lambda kv: -kv[1])[:6]
        crop = crop_box_for_face(m['_P'], hair_mask, lab, comps, W, H)
        measures.append(m)
        faces.append(dict(
            face_index=fi, n_landmarks=len(lms), pose_deg=m['pose'], top_blendshapes=top_bs,
            px=dict(mesh_length=round(m['mesh_length'], 1), face_length_hairline=round(m['face_length_hairline'], 1),
                    hairline_offset_from_mesh_top=round(m['hairline_offset_from_mesh_top'], 1),
                    cheek_width_234_454=round(m['cheek_width'], 1), cheek_width_3d=round(m['cheek_width_3d'], 1),
                    cheekbone_width_116_345=round(m['cheekbone_width'], 1),
                    jaw_width_172_397=round(m['jaw_width'], 1), jaw_width_3d=round(m['jaw_width_3d'], 1),
                    jaw2_width_58_288=round(m['jaw2_width'], 1),
                    forehead_width_103_332=round(m['forehead_width'], 1), forehead_width_3d=round(m['forehead_width_3d'], 1),
                    temple_width_54_284=round(m['temple_width'], 1), forehead2_width_67_297=round(m['forehead2_width'], 1),
                    chin_width_148_377=round(m['chin_width'], 1), eye_outer_dist=round(m['eye_outer_dist'], 1)),
            jaw_angle_deg=dict(at_172_397=round(m['jaw_angle'], 1), at_58_288=round(m['jaw2_angle'], 1),
                               left_172=round(m['jaw_angle_l'], 1), right_397=round(m['jaw_angle_r'], 1),
                               auto_gonion=[m['gonion_auto_l'], m['gonion_auto_r']],
                               auto_gonion_angle=[round(m['gonion_auto_angle_l'], 1), round(m['gonion_auto_angle_r'], 1)]),
            face_length_source=m['face_length_source'], hairline_lines_found=m['hairline_found_lines'],
            ratios=dict(LW=round(m['LW'], 3), LW_mesh=round(m['LW_mesh'], 3), JC=round(m['JC'], 3), FC=round(m['FC'], 3),
                        chinC=round(m['chinC'], 3), LW_rel=round(m['LW_rel'], 3), JC_rel=round(m['JC_rel'], 3),
                        FC_rel=round(m['FC_rel'], 3), chinC_rel=round(m['chinC_rel'], 3), jaw_angle_delta=round(m['jaw_angle_delta'], 1)),
            silhouette_px={k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items() if k.startswith('sil_') or k == 'hair_height_above_mesh_top'},
            shape=m['shape'], shape_reasons=m['shape_reasons'], crop_box=crop,
            pose_warning=('yaw' if abs(m['pose']['yaw']) > 15 else '') + ('pitch' if abs(m['pose']['pitch']) > 15 else ''),
        ))
    rec['faces'] = faces

    # overlays
    p_lm = draw_landmarks(rgb, r_lm.face_landmarks, measures, f'{OUT}/{stem}_landmarks.png')
    p_hair = draw_hair(rgb, hair_conf, f'{OUT}/{stem}_hair.png')
    p_mc = draw_multiclass(rgb, cat, multi_labels, f'{OUT}/{stem}_multiclass.png')
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    p_crop = bgr.copy()
    th = max(2, int(round(min(W, H) / 300)))
    for f in faces:
        c = f['crop_box']
        cv2.rectangle(p_crop, (c['x0'], c['y0']), (c['x1'], c['y1']), (0, 255, 0), th)
        fb = [int(v) for v in c['face_bbox']]
        cv2.rectangle(p_crop, (fb[0], fb[1]), (fb[2], fb[3]), (0, 0, 255), max(1, th // 2))
    for d in rec['face_detector']:
        cv2.rectangle(p_crop, (d['x'], d['y']), (d['x'] + d['w'], d['y'] + d['h']), (255, 0, 0), max(1, th // 2))
    cv2.imwrite(f'{OUT}/{stem}_cropbox.png', p_crop)
    if faces:
        c = faces[0]['crop_box']
        cv2.imwrite(f'{OUT}/{stem}_crop.png', bgr[c['y0']:c['y1'], c['x0']:c['x1']])
    contact_sheet([bgr, p_lm, p_hair, p_mc, p_crop], f'{OUT}/{stem}_sheet.png')
    rec['outputs'] = [f'{OUT}/{stem}_{s}.png' for s in ('landmarks', 'hair', 'multiclass', 'cropbox', 'crop', 'sheet')]
    results.append(rec)

    # console summary (numbers only)
    print(f"\n=== {rec['image']} {W}x{H}  faces={len(faces)} detector={len(rec['face_detector'])}  "
          f"t_ms lm={t_lm:.0f} hair={t_hair:.0f} multi={t_multi:.0f} fd={t_fd:.0f}")
    hm = rec['hair_mask']
    print(f"  hair: area={hm['area_fraction']:.3f} comps={hm['n_components_significant']}/{hm['n_components_total']} "
          f"largest={hm['largest_component_fraction']:.2f} band={hm['ambiguous_band_fraction_of_hair']:.2f} "
          f"meanconf={hm['mean_conf_inside']:.2f} border={[k for k, v in hm['touches_border'].items() if v]} "
          f"IoU_vs_multiclass={hm['iou_vs_multiclass_hair']:.2f} multi_hair_area={hm['multiclass_hair_area_fraction']:.3f}")
    print(f"  multiclass fractions: {hm['multiclass_class_fractions']}")
    for f in faces:
        px = f['px']; r = f['ratios']; ja = f['jaw_angle_deg']
        print(f"  face{f['face_index']}: pose={f['pose_deg']} {f['pose_warning'] or ''}")
        print(f"    len mesh={px['mesh_length']} hairline={px['face_length_hairline']} ({f['face_length_source']}, lines={f['hairline_lines_found']}) "
              f"cheek={px['cheek_width_234_454']} (3d {px['cheek_width_3d']}) cheekbone116/345={px['cheekbone_width_116_345']} "
              f"jaw172/397={px['jaw_width_172_397']} jaw58/288={px['jaw2_width_58_288']} forehead103/332={px['forehead_width_103_332']} "
              f"temple54/284={px['temple_width_54_284']} forehead67/297={px['forehead2_width_67_297']} chin={px['chin_width_148_377']}")
        print(f"    jaw angle 172/397={ja['at_172_397']} 58/288={ja['at_58_288']} auto={ja['auto_gonion']} {ja['auto_gonion_angle']}")
        print(f"    ratios LW={r['LW']} (mesh {r['LW_mesh']}) JC={r['JC']} FC={r['FC']} chinC={r['chinC']} | rel-to-canonical LW={r['LW_rel']} JC={r['JC_rel']} FC={r['FC_rel']} chin={r['chinC_rel']} dAng={r['jaw_angle_delta']}")
        print(f"    -> {f['shape']}: {f['shape_reasons'][0]}")
        s = f['silhouette_px']
        print(f"    silhouette(multiclass): skin jaw/cheek/forehead={s.get('sil_skin_jaw')}/{s.get('sil_skin_cheek')}/{s.get('sil_skin_forehead')} "
              f"person cheek={s.get('sil_person_cheek')} ({s.get('sil_person_cheek_over_landmark_cheek')}x landmark cheek) "
              f"hair widest above forehead={s.get('sil_hair_widest_above_forehead')} ({s.get('sil_hair_widest_over_cheek')}x) hair height above mesh top={s.get('hair_height_above_mesh_top')}px")
        print(f"    top blendshapes: {f['top_blendshapes']}")
        c = f['crop_box']; print(f"    crop box: ({c['x0']},{c['y0']})-({c['x1']},{c['y1']}) {c['w']}x{c['h']} hair comps used={c['hair_components']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('images', nargs='+')
    ap.add_argument('--num-faces', type=int, default=6)
    ap.add_argument('--json', default=f'{OUT}/results.json')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--min-det', type=float, default=0.5)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    fl, hair, multi, fd, load_ms = build_models(a.num_faces, a.min_det)
    print('model load ms:', {k: round(v, 1) for k, v in load_ms.items()})
    print('hair labels:', list(hair.labels), 'multiclass labels:', list(multi.labels))
    results = []
    if a.append and os.path.exists(a.json):
        results = json.load(open(a.json))
    for p in a.images:
        try:
            analyze(p, (fl, hair, multi, fd), a.num_faces, results)
        except Exception as e:
            print(f'!! {p}: {type(e).__name__}: {e}')
    with open(a.json, 'w') as f:
        json.dump(dict(cpu=os.popen('nproc').read().strip(), model_load_ms=load_ms, results=results), f, indent=1, default=str)
    for mdl in (fl, hair, multi, fd):
        mdl.close()
    print('\nwrote', a.json)


if __name__ == '__main__':
    main()
