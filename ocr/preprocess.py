from typing import Tuple
import cv2
import numpy as np

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def denoise(gray):
    return cv2.medianBlur(gray, 3)

def deskew(gray):
    coords = np.column_stack(np.where(gray > 0))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def threshold(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 11)

def upscale_dpi(gray, target_dpi=300) -> Tuple:
    # Heuristic: scale to approx 300 DPI by doubling size if too small
    h, w = gray.shape[:2]
    if max(h, w) < 1200:
        gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    return gray

def preprocess_bgr(bgr_img):
    gray = to_grayscale(bgr_img)
    gray = denoise(gray)
    gray = deskew(gray)
    gray = upscale_dpi(gray, 300)
    th = threshold(gray)
    return th

