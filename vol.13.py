import cv2
import time
import numpy as np
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Configuración de la Cámara ---
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# --- NUEVA CONFIGURACIÓN DE MEDIAPIPE (Tasks API para Python 3.13) ---
# OJO: Asegúrate de que 'hand_landmarker.task' esté en la misma carpeta
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

# Conexiones de la mano para dibujar la estructura manualmente (ya que 'solutions' no existe)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), 
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), 
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)
]

# --- Configuración de Audio (Pycaw para Windows) ---
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
except Exception as e:
    print(f"Error de audio: {e}")
    minVol, maxVol = -65, 0

volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    if not success:
        break
        
    # La nueva API requiere un objeto de imagen propio de MediaPipe
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    
    # Procesar la imagen con el nuevo detector
    detection_result = detector.detect(mp_image)
    
    lmList = []
    
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            h, w, c = img.shape
            
            # Extraer coordenadas
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                # Dibujar los puntos de la mano
                cv2.circle(img, (cx, cy), 3, (0, 0, 255), cv2.FILLED)

            # Dibujar las conexiones (esqueleto)
            for connection in HAND_CONNECTIONS:
                p1 = lmList[connection[0]][1:]
                p2 = lmList[connection[1]][1:]
                cv2.line(img, tuple(p1), tuple(p2), (0, 255, 0), 2)

    # --- LÓGICA DE CONTROL DE VOLUMEN ---
    if len(lmList) >= 9: # Asegurarnos de tener los puntos 4 y 8
        x1, y1 = lmList[4][1], lmList[4][2] # Pulgar
        x2, y2 = lmList[8][1], lmList[8][2] # Índice
        
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        # Distancia Euclidiana
        length = math.hypot(x2 - x1, y2 - y1)

        # Interpolar valores
        vol = np.interp(length, [30, 250], [minVol, maxVol])
        volBar = np.interp(length, [30, 250], [400, 150])
        volPer = np.interp(length, [30, 250], [0, 100])

        try:
            volume.SetMasterVolumeLevel(vol, None)
        except:
            pass

        if length < 30:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    # --- Interfaz Gráfica ---
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Control de Volumen IA - Python 3.13", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()