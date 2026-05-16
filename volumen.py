import cv2
import time
import numpy as np
import math
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Configuración de la Cámara y MediaPipe ---
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
# Usamos un nivel de confianza alto para evitar 'temblores' en el volumen
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Configuración de Audio (Pycaw para Windows) ---
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    # Rango de volumen (usualmente va de -65.25dB a 0.0dB)
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
except:
    print("No se pudo iniciar el control de audio (¿Quizás no estás en Windows?)")
    minVol, maxVol = -65, 0

volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    if not success:
        break
        
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    # Lista para guardar las coordenadas de los dedos
    lmList = []
    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            # Dibujar la estructura de la mano
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

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
        # print(length) # Descomenta para calibrar: mano cerrada ~30, mano abierta ~200

        # Convertir rango de longitud (ej. 30 a 250) a rango de volumen (-65 a 0)
        # Ajusta 30 y 250 según que tan cerca/lejos pones la mano de la cámara
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

    # Mostrar FPS
    cTime = time.time()
    # (Opcional cálculo de FPS aquí)
    
    cv2.imshow("Control de Volumen IA", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()