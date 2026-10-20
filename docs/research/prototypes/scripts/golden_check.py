#!/usr/bin/env python
"""Compare this pipeline's output on portrait.jpg to MediaPipe's own golden test assets
(storage.googleapis.com/mediapipe-assets): 478 golden landmarks, golden hair mask, golden detection box."""
import re, numpy as np, cv2
from PIL import Image as PILImage
import mediapipe as mp
vision = mp.tasks.vision; BaseOptions = mp.tasks.BaseOptions
ROOT = '<scratchpad>'
M = f'{ROOT}/testdata/models'; G = f'{ROOT}/testdata/golden'; OUT = f'{ROOT}/proto/out'

rgb = np.ascontiguousarray(np.asarray(PILImage.open(f'{ROOT}/testdata/portrait.jpg').convert('RGB')))
H, W = rgb.shape[:2]
img = mp.Image(mp.ImageFormat.SRGB, rgb)

fl = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=f'{M}/face_landmarker.task'), num_faces=1))
r = fl.detect(img)
mine = np.array([[l.x, l.y] for l in r.face_landmarks[0]])
txt = open(f'{G}/portrait_expected_face_landmarks.pbtxt').read()
gx = [float(v) for v in re.findall(r'x:\s*([-\d.e]+)', txt)]; gy = [float(v) for v in re.findall(r'y:\s*([-\d.e]+)', txt)]
gold = np.array(list(zip(gx, gy)))
err = np.linalg.norm((mine - gold) * [W, H], axis=1)
print(f'landmarks vs golden: n={len(gold)} mean err {err.mean():.2f}px, median {np.median(err):.2f}px, max {err.max():.2f}px (image {W}x{H}); '
      f'face oval pts mean err {err[[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]].mean():.2f}px')

hair = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=f'{M}/hair_segmenter.tflite'), output_confidence_masks=True, output_category_mask=True))
hr = hair.segment(img)
conf = hr.confidence_masks[1].numpy_view()[:, :, 0]
cat = hr.category_mask.numpy_view()[:, :, 0]
g = np.asarray(PILImage.open(f'{G}/portrait_hair_expected_mask.jpg').convert('L')) > 127
for name, m in (('conf>0.5', conf > 0.5), ('category_mask==1', cat == 1), ('conf>0.3', conf > 0.3), ('conf>0.7', conf > 0.7)):
    inter = (m & g).sum(); union = (m | g).sum()
    print(f'hair mask {name}: IoU vs golden {inter/union:.3f}  mine area {m.mean():.4f} golden area {g.mean():.4f}')
# golden mask is a JPEG (lossy); report how soft it is
gl = np.asarray(PILImage.open(f'{G}/portrait_hair_expected_mask.jpg').convert('L'))
print(f'golden mask grey-level fraction in (30,225): {((gl > 30) & (gl < 225)).mean():.4f} of image')

fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=BaseOptions(model_asset_path=f'{M}/blaze_face_short_range.tflite')))
d = fd.detect(img).detections[0].bounding_box
print(f'detection box mine: ({d.origin_x},{d.origin_y},{d.width},{d.height})  golden: (283,115,234,234)')
# side-by-side visual: golden vs mine hair mask
vis = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR).copy()
vis[g & ~(conf > 0.5)] = (0, 0, 255)     # golden only: red
vis[(conf > 0.5) & ~g] = (255, 0, 0)     # mine only: blue
vis[(conf > 0.5) & g] = (vis[(conf > 0.5) & g] * 0.5 + np.array([0, 255, 0]) * 0.5).astype(np.uint8)
cv2.imwrite(f'{OUT}/portrait_hair_vs_golden.png', vis[:560, 150:680])
print('wrote', f'{OUT}/portrait_hair_vs_golden.png (green=agree, red=golden only, blue=mine only)')
for m_ in (fl, hair, fd): m_.close()
