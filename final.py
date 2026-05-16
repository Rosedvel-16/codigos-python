import cv2
import numpy as np
import math
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import random

# --- 1. NÚCLEO DE INTELIGENCIA ARTIFICIAL ---
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("⏳ Inicializando matriz neuronal... Descargando pesos del modelo...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        model_path
    )

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options, 
    num_hands=1, 
    min_hand_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
detector = vision.HandLandmarker.create_from_options(options)

# --- 2. SISTEMA DE PARTÍCULAS Y PROYECTILES ---
class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 25
        # Disparo con trayectoria calculada por trigonometría
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.trail = [] # Para el efecto de estela
        self.life = 20

    def update(self):
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, img):
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                thickness = int((i / len(self.trail)) * 8)
                cv2.line(img, self.trail[i-1], self.trail[i], (50, 50, 255), thickness)
        cv2.circle(img, (int(self.x), int(self.y)), 6, (200, 200, 255), -1)

# --- 3. RENDERIZADOR DEL HUD Y ESCUDO ---
class CyberHUD:
    def __init__(self):
        self.angle_shield = 0
        self.projectiles = []
        self.last_shot_time = 0

    def draw_grid(self, img, w, h):
        # Fondo cuadriculado táctico
        overlay = img.copy()
        step = 50
        for x in range(0, w, step):
            cv2.line(overlay, (x, 0), (x, h), (0, 30, 0), 1)
        for y in range(0, h, step):
            cv2.line(overlay, (0, y), (w, y), (0, 30, 0), 1)
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

    def draw_telemetry(self, img, fps, mode, cx, cy):
        # Interfaz de Usuario (UX/UI)
        cv2.putText(img, f"SYS.FPS: {int(fps)}", (30, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.putText(img, f"TARGET: [{cx}, {cy}]", (30, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # Estado del sistema
        color = (0, 255, 255) if mode == "IDLE" else (0, 150, 255) if mode == "SHIELD" else (50, 50, 255)
        cv2.putText(img, f"MODE: {mode}", (30, 130), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)
        
        # Decoración Sci-Fi
        cv2.rectangle(img, (20, 20), (350, 150), (0, 255, 0), 1)
        cv2.line(img, (20, 150), (60, 190), (0, 255, 0), 1)

    def render_shield(self, img, center):
        # Matemáticas complejas para dibujar un escudo rotativo
        self.angle_shield += 5
        cx, cy = center
        
        # Aro exterior dentado
        for i in range(0, 360, 30):
            start_x = int(cx + math.cos(math.radians(i + self.angle_shield)) * 100)
            start_y = int(cy + math.sin(math.radians(i + self.angle_shield)) * 100)
            end_x = int(cx + math.cos(math.radians(i + 15 + self.angle_shield)) * 100)
            end_y = int(cy + math.sin(math.radians(i + 15 + self.angle_shield)) * 100)
            cv2.line(img, (start_x, start_y), (end_x, end_y), (255, 200, 0), 3)

        # Aro interior marea (Nami style)
        cv2.ellipse(img, (cx, cy), (70, 70), -self.angle_shield, 0, 270, (255, 255, 0), 4)
        cv2.circle(img, (cx, cy), 110, (255, 100, 0), 1)
        
        # Hexágono central pulsante
        pulse = int(math.sin(time.time() * 10) * 10) + 40
        pts = []
        for i in range(6):
            px = int(cx + math.cos(math.radians(i * 60)) * pulse)
            py = int(cy + math.sin(math.radians(i * 60)) * pulse)
            pts.append([px, py])
        cv2.polylines(img, [np.array(pts, np.int32)], True, (255, 255, 150), 2)

    def process_projectiles(self, img):
        for p in self.projectiles[:]:
            p.update()
            p.draw(img)
            if p.life <= 0 or p.x < 0 or p.x > 1280 or p.y < 0 or p.y > 720:
                self.projectiles.remove(p)

# --- 4. CONFIGURACIÓN DE CÁMARA Y LOOP PRINCIPAL ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

hud = CyberHUD()
pTime = 0
tip_ids = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    
    # Oscurecer imagen base para contraste
    img = cv2.convertScaleAbs(img, alpha=0.7, beta=0)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    results = detector.detect(mp_image)
    
    mode = "IDLE"
    cx, cy = 0, 0

    hud.draw_grid(img, w, h)

    if results.hand_landmarks:
        for hand_lms in results.hand_landmarks:
            lmList = []
            for id, lm in enumerate(hand_lms):
                px, py = int(lm.x * w), int(lm.y * h)
                lmList.append([px, py])
            
            # Dibujar esqueleto robótico
            for i in range(len(lmList)):
                cv2.circle(img, (lmList[i][0], lmList[i][1]), 3, (0, 255, 0), cv2.FILLED)
            
            cx, cy = lmList[9][0], lmList[9][1] # Centro de la palma

            # Lógica de Dedos
            fingers = []
            if lmList[tip_ids[0]][0] > lmList[tip_ids[0] - 1][0]: fingers.append(1)
            else: fingers.append(0)
            for id in range(1, 5):
                if lmList[tip_ids[id]][1] < lmList[tip_ids[id] - 2][1]: fingers.append(1)
                else: fingers.append(0)

            # --- MODO 1: ESCUDO (Mano Abierta) ---
            if fingers.count(1) >= 4:
                mode = "SHIELD DEPLOYED"
                hud.render_shield(img, (cx, cy))

            # --- MODO 2: BLASTER ADC (Pistola: Pulgar e Índice arriba) ---
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                mode = "BLASTER ACTIVE"
                idx_tip = lmList[8]
                idx_base = lmList[5]
                
                # Calcular el ángulo del dedo índice usando arcotangente (Trigonometría)
                angle = math.atan2(idx_tip[1] - idx_base[1], idx_tip[0] - idx_base[0])
                
                # Dibujar mira láser
                end_x = int(idx_tip[0] + math.cos(angle) * w)
                end_y = int(idx_tip[1] + math.sin(angle) * w)
                cv2.line(img, (idx_tip[0], idx_tip[1]), (end_x, end_y), (0, 0, 255), 1)
                
                # Disparar controlando la cadencia (Fire rate)
                if time.time() - hud.last_shot_time > 0.1:
                    hud.projectiles.append(Projectile(idx_tip[0], idx_tip[1], angle))
                    hud.last_shot_time = time.time()

    # Actualizar y dibujar físicas
    hud.process_projectiles(img)

    # Calcular FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime

    hud.draw_telemetry(img, fps, mode, cx, cy)

    cv2.imshow("Sistema HUD Tactico - Proyecto Final", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()