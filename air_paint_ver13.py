import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# 1. Descarga automática del modelo (Requerido por la nueva API de MediaPipe)
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Descargando el modelo de inteligencia artificial (esto solo pasa la primera vez)...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )
    print("✅ Modelo descargado con éxito.")

brush_thickness = 15
eraser_thickness = 50
draw_color = (248, 213, 175) 

cap = cv2.VideoCapture(0)
cap.set(3, 1280) 
cap.set(4, 720) 

# 2. Configuración de la nueva MediaPipe Tasks API
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=1, 
    min_hand_detection_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

img_canvas = np.zeros((720, 1280, 3), np.uint8)
xp, yp = 0, 0 

print("🟢 LISTO: Índice arriba = DIBUJAR | Dos dedos = PAUSA | 'c' = LIMPIAR")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convertir la imagen al formato que requiere la nueva API
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    
    # 3. Detectar las manos usando el nuevo método
    detection_result = detector.detect(mp_image)
    
    # Revisar si se detectaron manos
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            lm_list = []
            # Extraer las coordenadas exactas como lo hacías antes
            for id, lm in enumerate(hand_landmarks):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if len(lm_list) != 0:
                x1, y1 = lm_list[8][1:]
                x2, y2 = lm_list[12][1:]

                fingers = []
                # Dedo Índice
                if lm_list[8][2] < lm_list[6][2]: fingers.append(1)
                else: fingers.append(0)
                # Dedo Medio
                if lm_list[12][2] < lm_list[10][2]: fingers.append(1)
                else: fingers.append(0)

                # Ambos dedos arriba: Modo Pausa / Mover
                if fingers[0] and fingers[1]:
                    xp, yp = 0, 0 
                    cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), draw_color, cv2.FILLED)

                # Solo índice arriba: Modo Dibujar
                elif fingers[0] and not fingers[1]:
                    cv2.circle(img, (x1, y1), 15, draw_color, cv2.FILLED)
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1
                    
                    cv2.line(img, (xp, yp), (x1, y1), draw_color, brush_thickness)
                    cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
                    
                    xp, yp = x1, y1
                else:
                    xp, yp = 0, 0 

    img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
    
    _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    
    img = cv2.bitwise_and(img, img_inv)
    img = cv2.bitwise_or(img, img_canvas)

    cv2.imshow("Pizarra Magica - Tu Color", img)
    
    # Teclas de control
    key = cv2.waitKey(1)
    if key & 0xFF == ord('c'): 
        img_canvas = np.zeros((720, 1280, 3), np.uint8)
    if key & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()