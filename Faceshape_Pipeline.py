#!/usr/bin/env python
# coding: utf-8

# In[48]:


import os, cv2, numpy as np, tensorflow as tf, mediapipe as mp
from tensorflow.keras.models import load_model
from keras_facenet import FaceNet
from tensorflow.keras.layers import Rescaling
import tensorflow_hub as hub
from tensorflow.keras.saving import register_keras_serializable
from tensorflow import keras
import tensorflow as tf
from skimage.feature import hog


# In[49]:


# -------------------------------------------------
# 0. Globals ----------------------------------------------------------
CLASSES = ['Oblong', 'Heart', 'Square', 'Oval', 'Round']
MODEL_PATH = "faceshape_facenet.keras"      # change if you saved elsewhere
mp_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True, max_num_faces=1, refine_landmarks=True
)


# In[50]:


# ---------- helper: eye centres, geometry, HOG (exact copies) --------
def _eye_center(landmarks, idxs):
    pts = np.array([[landmarks[i].x, landmarks[i].y] for i in idxs])
    return pts.mean(axis=0)

def _align_no_scale(bgr, landmarks):
    h, w = bgr.shape[:2]
    l = _eye_center(landmarks, [33,133])
    r = _eye_center(landmarks, [362,263])
    dx, dy = r - l
    angle  = np.degrees(np.arctan2(dy, dx))
    mid    = ((l+r)/2)*np.array([w,h])
    M      = cv2.getRotationMatrix2D(tuple(mid), angle, 1.0)
    rot    = cv2.warpAffine(bgr, M, (w,h),
                             flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
    return rot, tuple(mid.astype(int))

def _extract_features(img_bgr):
    """returns (*handcrafted*, crop160, yaw_angle_deg or None)"""
    res = mp_mesh.process(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    if not res.multi_face_landmarks:
        return None, None, None          # no face
    lm0 = res.multi_face_landmarks[0].landmark
    rot, mid = _align_no_scale(img_bgr, lm0)

    res2 = mp_mesh.process(cv2.cvtColor(rot, cv2.COLOR_BGR2RGB))
    if not res2.multi_face_landmarks:
        return None, None, None
    lm = res2.multi_face_landmarks[0].landmark
    h,w = rot.shape[:2]
    

    # fixed crop around eyes
    ew=int(min(w,h)*0.8); eh=int(ew*1.2)
    x0=max(0, mid[0]-ew//2); y0=max(0, mid[1]-int(eh*0.4))
    crop = rot[y0:y0+eh, x0:x0+ew]
    if crop.size==0: return None,None,None
    crop160 = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB),
                         (160,160)).astype(np.float32)/255.0

    # Rough yaw estimate: difference between left & right eye visibility
    left_vis  = lm[33].visibility + lm[133].visibility
    right_vis = lm[362].visibility+ lm[263].visibility
    yaw = right_vis-left_vis           # heuristic in (-2..2)
    return crop160, yaw


# In[51]:


# -------------- Side-face heuristic -----------------
def _is_side_face(yaw_vis, thresh=0.6):
    """visibility diff heuristic -> side face yes/no"""
    return abs(yaw_vis) > thresh


# In[52]:


import pickle
from tensorflow import keras
import tensorflow as tf
import tensorflow as tf
tf.config.run_functions_eagerly(False) # To enable eager execution

# tolerant helper: works for 3.8, 3.9, future releases
def scaling(x, *args, scale=1.0, **kwargs):
    """
    Accepts:
        • scaling(x, 0.1666)              (old positional style)
        • scaling(x, scale=0.1666)        (new keyword style)
        • scaling(x)                      (nothing supplied)
        • extra kwargs like mask, training …
    """
    if args:          # old style: scale is first positional arg
        scale = args[0]
    return x * scale

def l2_normalize(x, axis=-1, *_, **kwargs):
    return tf.math.l2_normalize(x, axis=axis)



class FaceShapePredictor:
    def __init__(self, path="faceshape_facenet_v3.keras"):        

        self.model = keras.models.load_model('faceshape_facenet_v3.keras',
                                compile=False,          # inference only
                                custom_objects={
                                    "scaling": scaling,             # new tolerant version
                                    "l2_normalize": l2_normalize,   # idem
                                    "Rescaling": Rescaling,
                                    "KerasLayer": hub.KerasLayer   # TF-Hub FaceNet backbone)
                                })
    def predict(self, img_path_or_bgr):
        # 1) load image
        if isinstance(img_path_or_bgr, str):
            bgr = cv2.imread(img_path_or_bgr)
            if bgr is None:
                return {"error": "Image could not be read"}
        else:
            bgr = img_path_or_bgr.copy()

        # 2) feature extraction
        crop160, yaw = _extract_features(bgr)
        if crop160 is None:
            return {"error": "No face detected in image"}

        img_batch  = np.expand_dims(crop160, axis=0)

        probs = self.model.predict(img_batch, verbose=0)[0]
        top1  = CLASSES[int(np.argmax(probs))]

        return {
            "face_shape" : top1,
            "scores"     : dict(zip(CLASSES, probs.round(4).tolist())),
            "is_side_face": _is_side_face(yaw),
        }


# In[53]:


# ---------------- quick CLI test --------------------
if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("Usage: python faceshape_pipeline.py <image_path>")
        sys.exit(0)
    path = "/Users/dikshatiwari/.cache/kagglehub/datasets/niten19/face-shape-dataset/versions/2/FaceShape Dataset/training_set/Oblong"
    ls = os.listdir(path)
    img = cv2.imread(path+"/"+ls[0])
    predictor = FaceShapePredictor()          # loads model
    result = predictor.predict(img)
    print(json.dumps(result, indent=2))


# In[ ]:




