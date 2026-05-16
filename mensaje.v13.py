import cv2
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# 1. Descarga del modelo si no existe (igual que en la pizarra)
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Descargando el modelo...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )

# 2. Conexiones de la mano para dibujarlas manualmente (reemplaza a mp.solutions.drawing_utils)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),# Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Meñique y palma
]

# 3. Configuración de la nueva API de MediaPipe
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=1, 
    min_hand_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Formato requerido por la nueva API
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    detection_result = detector.detect(mp_image)
    
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            lmList = []
            h, w, c = img.shape
            
            # Extraer puntos y dibujarlos en rojo
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                cv2.circle(img, (cx, cy), 4, (0, 0, 255), cv2.FILLED)

            # Dibujar las líneas de conexión en verde
            for connection in HAND_CONNECTIONS:
                p1, p2 = connection[0], connection[1]
                cv2.line(img, (lmList[p1][1], lmList[p1][2]), (lmList[p2][1], lmList[p2][2]), (0, 255, 0), 2)

            if len(lmList) != 0:
                # Coordenadas de la punta del pulgar (4) y la punta del índice (8)
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                
                dist_ok = math.hypot(x2 - x1, y2 - y1)
                
                # Verificar si los demás dedos están levantados
                medio_arriba = lmList[12][2] < lmList[10][2]
                anular_arriba = lmList[16][2] < lmList[14][2]
                menique_arriba = lmList[20][2] < lmList[18][2]
                
                # Si el pulgar y el índice están juntos (< 30) y los otros 3 dedos están arriba
                if dist_ok < 30 and medio_arriba and anular_arriba and menique_arriba:
                    cv2.putText(img, "Eres jochis", (100, 200), 
                                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
                    cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                    
    cv2.imshow("Detector Jochis", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()