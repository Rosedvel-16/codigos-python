import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import random
import time

# --- 1. DESCARGA DEL MODELO (Python 3.13) ---
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Preparando el núcleo mágico (Descargando modelo)...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )

# --- 2. CLASE DEL SISTEMA DE PARTÍCULAS ---
class Particle:
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.p_type = p_type  # 'bubble' o 'heart'
        self.life = 255
        
        if self.p_type == 'bubble':
            # Física de burbujas: flotan suavemente hacia arriba
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-5, -1)
            self.radius = random.randint(8, 18)
            self.color = (255, 230, 100)  # Cian/Agua en BGR
            self.decay = random.randint(4, 8)
        elif self.p_type == 'heart':
            # Física de corazones: explosión en todas direcciones con gravedad
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-10, 2)
            self.radius = random.randint(15, 25)
            self.color = (80, 80, 255)  # Rojo Carmesí/Rosa en BGR
            self.decay = random.randint(6, 12)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        if self.p_type == 'heart':
            self.vy += 0.5  # Efecto de gravedad para los corazones

    def draw(self, img):
        if self.life <= 0: return
        
        # Efecto de desvanecimiento (Alpha) simulado reduciendo el tamaño y brillo
        current_size = max(1, int(self.radius * (self.life / 255.0)))
        
        if self.p_type == 'bubble':
            # Dibujar burbuja hueca con un brillo
            cv2.circle(img, (int(self.x), int(self.y)), current_size, self.color, max(1, int(self.life/50)))
            # Reflejo kawaii de la burbuja
            cv2.circle(img, (int(self.x - current_size/3), int(self.y - current_size/3)), 
                       max(1, current_size//4), (255, 255, 255), -1)
                       
        elif self.p_type == 'heart':
            if current_size > 3:
                # Dibujar un corazón usando OpenCV (2 círculos y 1 triángulo)
                c1 = (int(self.x - current_size//2), int(self.y))
                c2 = (int(self.x + current_size//2), int(self.y))
                
                # Parte superior del corazón
                cv2.circle(img, c1, current_size//2, self.color, -1)
                cv2.circle(img, c2, current_size//2, self.color, -1)
                
                # Pico inferior del corazón
                pts = np.array([
                    [c1[0] - current_size//2 + 1, c1[1]], 
                    [c2[0] + current_size//2 - 1, c2[1]], 
                    [int(self.x), int(self.y + current_size + 2)]
                ], np.int32)
                cv2.fillPoly(img, [pts], self.color)

# --- 3. CONFIGURACIÓN DE IA Y CÁMARA ---
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=2, # ¡Soporte para dos manos a la vez!
    min_hand_detection_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

particles = []
tip_ids = [4, 8, 12, 16, 20]

# Crear un filtro oscuro (Vignette) para que resalten las partículas
vignette = np.zeros((720, 1280), dtype=np.uint8)
cv2.circle(vignette, (640, 360), 600, 255, -1)
vignette = cv2.GaussianBlur(vignette, (301, 301), 0)
vignette = cv2.cvtColor(vignette, cv2.COLOR_GRAY2BGR) / 255.0

print("🟢 LISTO: 1 Dedo = Burbujas | Seña de V (Amor y Paz) = Corazones")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    
    # Aplicar el filtro cinemático (oscurece bordes)
    img = cv2.convertScaleAbs(img * vignette)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    detection_result = detector.detect(mp_image)
    
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            lm_list = []
            h, w, c = img.shape
            
            for id, lm in enumerate(hand_landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
            
            # Dibujar un rastro estético en la mano (Aura)
            for point in lm_list:
                cv2.circle(img, (point[1], point[2]), 2, (255, 255, 255), -1)

            # Lógica de detección de dedos
            fingers = []
            # Pulgar
            if lm_list[tip_ids[0]][1] < lm_list[tip_ids[0] - 1][1]: fingers.append(1)
            else: fingers.append(0)
            # Otros 4 dedos
            for id in range(1, 5):
                if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]: fingers.append(1)
                else: fingers.append(0)

            # --- HECHIZOS ---
            x_index, y_index = lm_list[8][1], lm_list[8][2]
            
            # Hechizo 1: Burbujas de Agua (Solo dedo índice arriba)
            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                cv2.circle(img, (x_index, y_index), 15, (255, 230, 100), cv2.FILLED) # Foco de luz
                particles.append(Particle(x_index, y_index, 'bubble'))

            # Hechizo 2: Ráfaga de Corazones (Dedo índice y medio arriba, seña de 'V')
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                x_mid, y_mid = lm_list[12][1], lm_list[12][2]
                cx, cy = (x_index + x_mid) // 2, (y_index + y_mid) // 2
                cv2.circle(img, (cx, cy), 20, (100, 100, 255), 2) # Foco de recarga
                
                # Emitir varios corazones por frame para crear la explosión
                for _ in range(3):
                    particles.append(Particle(cx, cy, 'heart'))

    # --- RENDERIZAR FÍSICAS ---
    for p in particles[:]:
        p.update()
        p.draw(img)
        if p.life <= 0:
            particles.remove(p) # Limpiar memoria

    cv2.imshow("AR Magic Emitter - Tu propio filtro", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()