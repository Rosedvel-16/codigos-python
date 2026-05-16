import cv2
import time
import numpy as np
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- 1. Descarga del modelo de MediaPipe ---
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Descargando el modelo de MediaPipe...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )

# --- Conexiones para dibujar la mano manualmente ---
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # Índice
    (5, 9), (9, 10), (10, 11), (11, 12),  # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),# Anular
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Meñique y base
]

# --- Configuración de la Cámara ---
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# --- 2. Configuración de la nueva API de MediaPipe ---
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=1, 
    min_hand_detection_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

# --- Configuración de Audio (Pycaw para Windows) ---
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    # Rango de volumen (usualmente va de -65.25dB a 0.0dB)
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
except Exception as e:
    print(f"No se pudo iniciar el control de audio: {e}")
    minVol, maxVol = -65, 0

volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    if not success:
        break
        
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # --- 3. Detección con la nueva API ---
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    detection_result = detector.detect(mp_image)
    
    # Lista para guardar las coordenadas de los dedos
    lmList = []
    
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            h, w, c = img.shape
            
            # Extraer puntos y dibujarlos
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                # Pequeño círculo rojo en cada articulación
                cv2.circle(img, (cx, cy), 4, (0, 0, 255), cv2.FILLED)
                
            # Dibujar las líneas de conexión
            for connection in HAND_CONNECTIONS:
                p1, p2 = connection[0], connection[1]
                cv2.line(img, (lmList[p1][1], lmList[p1][2]), (lmList[p2][1], lmList[p2][2]), (0, 255, 0), 2)

    if len(lmList) != 0:
        # Puntos clave: 4 (Punta del Pulgar) y 8 (Punta del Índice)
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        
        # Punto medio entre los dedos (para estética)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Dibujar los círculos en las puntas y la línea que los une
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED) # Pulgar
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED) # Índice
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED) # Centro

        # --- MATEMÁTICAS ---
        # Calcular la longitud de la línea (Distancia Euclidiana)
        length = math.hypot(x2 - x1, y2 - y1)

        # Convertir rango de longitud (ej. 30 a 250) a rango de volumen (-65 a 0)
        vol = np.interp(length, [30, 250], [minVol, maxVol])
        volBar = np.interp(length, [30, 250], [400, 150])
        volPer = np.interp(length, [30, 250], [0, 100])

        # Establecer volumen del sistema
        try:
            volume.SetMasterVolumeLevel(vol, None)
        except:
            pass

        # Feedback visual: Cambiar color del punto central si el volumen es bajo o alto
        if length < 30:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED) # Verde al cerrar

    # --- Interfaz Gráfica (Barra de Volumen en pantalla) ---
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3) # Marco
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED) # Relleno
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Control de Volumen IA", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()