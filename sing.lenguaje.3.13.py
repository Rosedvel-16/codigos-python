import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# 1. Descargar el modelo de MediaPipe si no existe
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Descargando el modelo...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )

# 2. Conexiones manuales de los dedos (Reemplaza mp.solutions.drawing_utils)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),# Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Meñique y base
]

# 3. Configurar el detector con la nueva API
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=1, 
    min_hand_detection_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

tip_ids = [4, 8, 12, 16, 20]

def get_fingers_status(lm_list):
    """Devuelve una lista [0, 1, 0, 1, 1] indicando qué dedos están levantados"""
    fingers = []
    
    # Pulgar
    if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 Dedos restantes
    for id in range(1, 5):
        if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return fingers

while True:
    success, img = cap.read()
    if not success: break
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Formato requerido por la nueva API
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    detection_result = detector.detect(mp_image)
    
    msg = "" # Mensaje a mostrar

    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            lm_list = []
            h, w, c = img.shape
            
            # Extraer puntos y dibujar círculos
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                cv2.circle(img, (cx, cy), 4, (0, 0, 255), cv2.FILLED)

            # Dibujar líneas de conexión manualmente
            for connection in HAND_CONNECTIONS:
                p1, p2 = connection[0], connection[1]
                cv2.line(img, (lm_list[p1][1], lm_list[p1][2]), (lm_list[p2][1], lm_list[p2][2]), (0, 255, 0), 2)

            if len(lm_list) != 0:
                fingers = get_fingers_status(lm_list)
                
                # Lógica del traductor
                if fingers == [0, 0, 0, 0, 0] or fingers == [1, 0, 0, 0, 0]:
                    msg = "A (O Piedra)"
                
                elif fingers == [0, 1, 1, 1, 1] or fingers == [1, 1, 1, 1, 1]:
                    msg = "B (Hola)"
                
                elif fingers == [1, 1, 0, 0, 0]:
                    msg = "L (Loser/Love)"
                
                elif fingers == [0, 1, 1, 0, 0]:
                    msg = "V (Victoria)"
                
                elif fingers == [1, 0, 0, 0, 1]:
                    msg = "Y (Call Me)"
                
                elif fingers == [0, 1, 0, 0, 0]:
                    msg = "1 (Uno)"
                    
                else:
                    msg = "..."

            # Dibujar fondo negro y texto
            cv2.rectangle(img, (20, 20), (450, 120), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, msg, (30, 100), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)

    cv2.imshow("Traductor de Senas (BETA)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()