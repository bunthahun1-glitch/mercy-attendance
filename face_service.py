"""
High-Precision Biometric Face Recognition Service for Mercy Dental Care.
Powered by:
- YuNet (Deep CNN Face Detector & 5-point facial landmark extractor)
- InsightFace ArcFace ResNet50 (w600k_r50) 512-dimensional deep biometric embedding engine
"""

import os
import cv2
import numpy as np
import base64
import onnxruntime as ort
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FACES_DIR = os.path.join(BASE_DIR, "uploads", "faces")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

YUNET_PATH = os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx")
ARCFACE_PATH = os.path.join(MODELS_DIR, "w600k_r50.onnx")
SFACE_PATH = os.path.join(MODELS_DIR, "face_recognition_sface_2021dec.onnx")

# Standard 112x112 ArcFace landmark reference points
ARCFACE_DST_PTS = np.array([
    [38.2946, 51.6963],  # left eye
    [73.5318, 51.5014],  # right eye
    [56.0252, 71.7366],  # nose
    [41.5493, 92.3655],  # left mouth
    [70.7299, 92.2041]   # right mouth
], dtype=np.float32)

# High-accuracy threshold:
# Same person: typically 0.60 to 0.95
# Other/different person: typically -0.10 to 0.25
ARCFACE_COSINE_THRESHOLD = 0.50

_detector = None
_arcface_session = None
_sface_recognizer = None

def get_detector():
    global _detector
    if _detector is None and os.path.exists(YUNET_PATH):
        try:
            _detector = cv2.FaceDetectorYN.create(YUNET_PATH, "", (320, 320), score_threshold=0.6, nms_threshold=0.3)
        except Exception as e:
            print("Failed to init YuNet detector:", e)
    return _detector

def get_arcface_session():
    global _arcface_session
    if _arcface_session is None and os.path.exists(ARCFACE_PATH):
        try:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            _arcface_session = ort.InferenceSession(ARCFACE_PATH, sess_options=opts, providers=['CPUExecutionProvider'])
        except Exception as e:
            print("Failed to init ArcFace session:", e)
    return _arcface_session

def get_sface_recognizer():
    global _sface_recognizer
    if _sface_recognizer is None and os.path.exists(SFACE_PATH):
        try:
            _sface_recognizer = cv2.FaceRecognizerSF.create(SFACE_PATH, "")
        except Exception as e:
            print("Failed to init SFace recognizer:", e)
    return _sface_recognizer

def base64_to_cv2(b64_str):
    if not b64_str:
        return None
    try:
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        print("Error decoding base64 image:", e)
        return None

def detect_single_face(img):
    detector = get_detector()
    if detector is None or img is None:
        return None, "មិនអាចដំណើរការប្រព័ន្ធស្កេនមុខបានទេ"

    h, w, _ = img.shape
    detector.setInputSize((w, h))
    _, faces = detector.detect(img)

    if faces is None or len(faces) == 0:
        return None, "រកមិនឃើញផ្ទៃមុខក្នុងកាមេរ៉ាទេ! សូមតម្រង់មុខអោយចំកាមេរ៉ា និងមានពន្លឺគ្រប់គ្រាន់"
    
    # Return highest confidence face
    return faces[0], "OK"

def align_face_112(img, face):
    landmarks = [
        [face[4], face[5]],
        [face[6], face[7]],
        [face[8], face[9]],
        [face[10], face[11]],
        [face[12], face[13]]
    ]
    src_pts = np.array(landmarks, dtype=np.float32).reshape((5, 2))
    tform, _ = cv2.estimateAffinePartial2D(src_pts, ARCFACE_DST_PTS)
    if tform is None:
        return cv2.resize(img, (112, 112))
    return cv2.warpAffine(img, tform, (112, 112), borderValue=0.0)

def extract_feature(img, face):
    """Extracts normalized 512-d ArcFace feature vector, or 128-d SFace as fallback."""
    arcface = get_arcface_session()
    if arcface is not None and face is not None:
        try:
            aligned = align_face_112(img, face)
            blob = cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB).astype(np.float32)
            blob = (blob - 127.5) / 127.5
            blob = np.transpose(blob, (2, 0, 1))
            blob = np.expand_dims(blob, axis=0)
            feat = arcface.run(None, {'input.1': blob})[0][0]
            norm = np.linalg.norm(feat)
            if norm > 0:
                return feat / norm
        except Exception as e:
            print("ArcFace extraction error:", e)

    # Fallback to SFace
    sface = get_sface_recognizer()
    if sface is not None and face is not None:
        try:
            aligned = sface.alignCrop(img, face)
            feat = sface.feature(aligned)
            if feat is not None:
                feat = feat.flatten()
                norm = np.linalg.norm(feat)
                return feat / norm if norm > 0 else feat
        except Exception as e:
            print("SFace fallback extraction error:", e)

    return None

def get_registered_face_path(emp_id):
    path = os.path.join(FACES_DIR, f"staff_{emp_id}_registered.jpg")
    if os.path.exists(path):
        return path
    emp = database.get_employee_by_id(emp_id)
    if emp and emp.get("avatar_path") and os.path.exists(emp["avatar_path"]):
        return emp["avatar_path"]
    return None

def register_face(emp_id, img):
    """Enrolls the benchmark reference face for an employee."""
    face, err = detect_single_face(img)
    if face is None:
        return False, err

    feat = extract_feature(img, face)
    if feat is None:
        return False, "មិនអាចទាញយកទិន្នន័យ Biometric ផ្ទៃមុខបានទេ"

    ref_path = os.path.join(FACES_DIR, f"staff_{emp_id}_registered.jpg")
    feat_path = os.path.join(FACES_DIR, f"staff_{emp_id}_feature.npy")
    try:
        cv2.imwrite(ref_path, img)
        np.save(feat_path, feat)
        conn = database.get_connection()
        conn.cursor().execute("UPDATE employees SET avatar_path = ? WHERE id = ?", (ref_path, emp_id))
        conn.commit()
        conn.close()
        return True, "✅ បានកត់សម្គាល់ផ្ទៃមុខដំបូងដោយជោគជ័យ!"
    except Exception as e:
        return False, f"កំហុសក្នុងការរក្សាទុកមុខ៖ {e}"

def verify_face(emp_id, live_img):
    """
    Compares live_img with registered face for emp_id using ArcFace 512-d embeddings.
    If no registered face exists yet, auto-enrolls the first face.
    Returns: (is_matched: bool, score: float, message: str)
    """
    ref_path = get_registered_face_path(emp_id)
    feat_path = os.path.join(FACES_DIR, f"staff_{emp_id}_feature.npy")

    live_face, err = detect_single_face(live_img)
    if live_face is None:
        return False, 0.0, err

    live_feat = extract_feature(live_img, live_face)
    if live_feat is None:
        return False, 0.0, "មិនអាចទាញយកទិន្នន័យ Biometric លើផ្ទៃមុខផ្ទាល់បានទេ"

    # Auto-enrollment on first scan
    if not ref_path or not os.path.exists(ref_path) or not os.path.exists(feat_path):
        ok, msg = register_face(emp_id, live_img)
        if ok:
            return True, 1.0, "✅ បានកត់សម្គាល់ផ្ទៃមុខដំបូងដោយជោគជ័យ! (First-Time Face Enrolled)"
        else:
            return False, 0.0, msg

    # Load enrolled feature
    try:
        ref_feat = np.load(feat_path)
    except Exception:
        ref_feat = None

    if ref_feat is None or len(ref_feat) != len(live_feat):
        # Re-compute reference feature from saved photo
        ref_img = cv2.imread(ref_path)
        ref_face, _ = detect_single_face(ref_img)
        if ref_face is not None:
            ref_feat = extract_feature(ref_img, ref_face)
            if ref_feat is not None:
                np.save(feat_path, ref_feat)

    if ref_feat is None or len(ref_feat) != len(live_feat):
        ok, msg = register_face(emp_id, live_img)
        return ok, 1.0, "✅ បានកត់សម្គាល់ផ្ទៃមុខឡើងវិញដោយជោគជ័យ!"

    # Calculate Normalized Cosine Similarity (Dot product of unit vectors)
    score = float(np.dot(ref_feat, live_feat))

    # Threshold for ArcFace: 0.50 (50%)
    if score >= ARCFACE_COSINE_THRESHOLD:
        pct = min(100, int(score * 100))
        return True, score, f"✅ ផ្ទៀងផ្ទាត់មុខត្រឹមត្រូវ (កម្រិតភាពដូចគ្នា {pct}%)"
    else:
        pct = max(0, int(score * 100))
        return False, score, f"❌ ផ្ទៃមុខមិនត្រូវគ្នានឹងទិន្នន័យបុគ្គលិកនេះទេ (Other Face)! (ភាពដូចគ្នាតែ {pct}% < កំណត់ 50%)"

def reset_employee_face(emp_id):
    """Deletes registered face files for an employee to allow clean re-enrollment."""
    ref_path = os.path.join(FACES_DIR, f"staff_{emp_id}_registered.jpg")
    feat_path = os.path.join(FACES_DIR, f"staff_{emp_id}_feature.npy")
    try:
        if os.path.exists(ref_path):
            os.remove(ref_path)
        if os.path.exists(feat_path):
            os.remove(feat_path)
        conn = database.get_connection()
        conn.cursor().execute("UPDATE employees SET avatar_path = NULL WHERE id = ?", (emp_id,))
        conn.commit()
        conn.close()
        return True, "បានសម្អាតទិន្នន័យផ្ទៃមុខជោគជ័យ!"
    except Exception as e:
        return False, f"កំហុសក្នុងការសម្អាត៖ {e}"

if __name__ == "__main__":
    print("ArcFace model ready:", os.path.exists(ARCFACE_PATH))
    print("YuNet model ready:", os.path.exists(YUNET_PATH))
    s = get_arcface_session()
    print("ArcFace session initialized:", s is not None)
