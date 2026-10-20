import time, sys
import numpy as np
from PIL import Image as PILImage
import mediapipe as mp
vision = mp.tasks.vision
BaseOptions = mp.tasks.BaseOptions

M='<scratchpad>/testdata/models'
T='<scratchpad>/testdata'

img = np.asarray(PILImage.open(f'{T}/portrait.jpg').convert('RGB'))
mpimg = mp.Image(mp.ImageFormat.SRGB, np.ascontiguousarray(img))
print('image', mpimg.width, mpimg.height, mpimg.channels)

t=time.perf_counter()
fl = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=f'{M}/face_landmarker.task'),
    num_faces=2, output_face_blendshapes=True, output_facial_transformation_matrixes=True))
print('landmarker load %.3fs' % (time.perf_counter()-t))
t=time.perf_counter(); r = fl.detect(mpimg); dt=time.perf_counter()-t
print('faces', len(r.face_landmarks), 'landmarks per face', [len(f) for f in r.face_landmarks], 'blendshapes', [len(b) for b in r.face_blendshapes], 'matrices', [m.shape for m in r.facial_transformation_matrixes], 'detect %.3fs'%dt)
lm = r.face_landmarks[0][0]; print('landmark0 fields', [a for a in dir(lm) if not a.startswith('_')], lm.x, lm.y, lm.z, lm.visibility, lm.presence)
bs = r.face_blendshapes[0][:3]; print('blendshape sample', [(b.category_name, round(b.score,3)) for b in bs])
print(r.facial_transformation_matrixes[0])

for name in ['hair_segmenter.tflite','selfie_multiclass_256x256.tflite']:
    t=time.perf_counter()
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=f'{M}/{name}'), output_confidence_masks=True, output_category_mask=True))
    print(name, 'load %.3fs' % (time.perf_counter()-t))
    print(' labels', seg.get_labels() if hasattr(seg,'get_labels') else [a for a in dir(seg) if 'label' in a])
    t=time.perf_counter(); res = seg.segment(mpimg); dt=time.perf_counter()-t
    cm = res.category_mask.numpy_view(); print(' category_mask', cm.shape, cm.dtype, np.unique(cm), 'segment %.3fs'%dt)
    print(' confidence masks', len(res.confidence_masks), [ (m.numpy_view().shape, m.numpy_view().dtype, float(m.numpy_view().min()), float(m.numpy_view().max())) for m in res.confidence_masks])

t=time.perf_counter()
fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=BaseOptions(model_asset_path=f'{M}/blaze_face_short_range.tflite')))
print('face detector load %.3fs' % (time.perf_counter()-t))
t=time.perf_counter(); d = fd.detect(mpimg); dt=time.perf_counter()-t
print('detections', len(d.detections), 'detect %.3fs'%dt)
for det in d.detections:
    print(' bbox', det.bounding_box, 'cats', [(c.category_name, round(c.score,3)) for c in det.categories], 'kps', len(det.keypoints or []))
