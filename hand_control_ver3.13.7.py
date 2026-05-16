import cv2
import numpy as np

# --- CONFIGURACIÓN DE LA CÁMARA ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# --- VALORES INICIALES PARA DETECTAR COLOR (Ejemplo: Azul) ---
# Ajusta estos valores con las barras deslizantes que aparecerán
h_min, h_max = 90, 130
s_min, s_max = 150, 255
v_min, v_max = 100, 255

def on_trackbar(val):
    pass

# Crear ventana de configuración
cv2.namedWindow("Configurar Color")
cv2.resizeWindow("Configurar Color", 640, 240)
cv2.createTrackbar("Hue Min", "Configurar Color", h_min, 179, on_trackbar)
cv2.createTrackbar("Hue Max", "Configurar Color", h_max, 179, on_trackbar)
cv2.createTrackbar("Sat Min", "Configurar Color", s_min, 255, on_trackbar)
cv2.createTrackbar("Sat Max", "Configurar Color", s_max, 255, on_trackbar)
cv2.createTrackbar("Val Min", "Configurar Color", v_min, 255, on_trackbar)
cv2.createTrackbar("Val Max", "Configurar Color", v_max, 255, on_trackbar)

# --- CLASES DEL JUEGO ---
class DragObject:
    def __init__(self, text, pos, color):
        self.text = text
        self.pos = pos
        self.w = 150
        self.h = 60
        self.color = color
        self.is_dragging = False

    def update(self, cursor_pos):
        # Si no hay cursor (no se detecta color), soltamos
        if cursor_pos is None:
            self.is_dragging = False
            return

        cx, cy = cursor_pos
        x, y = self.pos

        # Lógica de imán: Si el color pasa cerca, lo agarra
        dist = np.hypot(cx - (x + self.w//2), cy - (y + self.h//2))
        
        if dist < 50: # Si pasas cerca, lo agarras automáticamente
            self.is_dragging = True
        
        if self.is_dragging:
            self.pos[0] = cx - self.w // 2
            self.pos[1] = cy - self.h // 2

# Contenedores y Tareas
containers = [
    {"name": "TODO", "x": 50, "w": 300, "color": (50, 50, 50)},
    {"name": "DOING", "x": 400, "w": 300, "color": (100, 100, 50)},
    {"name": "DONE", "x": 750, "w": 300, "color": (50, 100, 50)}
]

tasks = [
    DragObject("Python 3.13", [70, 150], (200, 0, 200)),
    DragObject("Vision", [70, 250], (0, 200, 200)),
    DragObject("OpenCV", [70, 350], (0, 0, 200)),
]

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1) # Espejo
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Leer valores de los trackbars en tiempo real
    h_min = cv2.getTrackbarPos("Hue Min", "Configurar Color")
    h_max = cv2.getTrackbarPos("Hue Max", "Configurar Color")
    s_min = cv2.getTrackbarPos("Sat Min", "Configurar Color")
    s_max = cv2.getTrackbarPos("Sat Max", "Configurar Color")
    v_min = cv2.getTrackbarPos("Val Min", "Configurar Color")
    v_max = cv2.getTrackbarPos("Val Max", "Configurar Color")

    # Crear máscara de color
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Limpiar ruido (opcional pero recomendado)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Encontrar contornos (dónde está el color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cursor_pos = None

    if contours:
        # Tomar el contorno más grande (para ignorar ruiditos de fondo)
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500: # Solo si es un objeto grande
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w // 2, y + h // 2
            cursor_pos = (cx, cy)
            
            # Dibujar el "dedo" detectado
            cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), -1)

    # Actualizar lógica del juego
    for task in tasks:
        task.update(cursor_pos)

    # --- DIBUJAR INTERFAZ ---
    # Dibujar máscara en pequeño en la esquina para ver qué detectas
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    img[0:150, 0:200] = cv2.resize(mask_bgr, (200, 150))
    cv2.putText(img, "Mascara (Lo que ve la PC)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Dibujar Contenedores
    for c in containers:
        cv2.rectangle(img, (c["x"], 50), (c["x"] + c["w"], 600), c["color"], 2)
        cv2.putText(img, c["name"], (c["x"] + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, c["color"], 2)

    # Dibujar Tareas
    for task in tasks:
        cv2.rectangle(img, (task.pos[0], task.pos[1]), 
                      (task.pos[0] + task.w, task.pos[1] + task.h), task.color, -1)
        cv2.putText(img, task.text, (task.pos[0] + 10, task.pos[1] + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Control por Color (Python 3.13)", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()