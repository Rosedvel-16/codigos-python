import cv2
import mediapipe as mp
import numpy as np

# --- CONFIGURACIÓN INICIAL ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # Ancho
cap.set(4, 720)  # Alto

# Inicializar módulos de MediaPipe para manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,         # Solo una mano para evitar caos
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# --- CLASES Y OBJETOS ---

class DragObject:
    def __init__(self, text, pos, color):
        self.text = text
        self.pos = pos # [x, y]
        self.w = 150
        self.h = 60
        self.color = color
        self.is_dragging = False

    def update(self, cursor_pos, is_pinching):
        # cursor_pos es (x, y) de la punta del dedo índice
        x, y = self.pos
        cx, cy = cursor_pos

        # Verificar si el cursor está dentro del objeto
        if x < cx < x + self.w and y < cy < y + self.h:
            # Cambiar color visualmente si hacemos hover (opcional, aquí simplificado)
            if is_pinching:
                self.is_dragging = True
        
        # Si ya lo tenemos agarrado, que siga al dedo
        if self.is_dragging:
            if is_pinching:
                # Actualizar posición (centrado en el dedo)
                self.pos[0] = cx - self.w // 2
                self.pos[1] = cy - self.h // 2
            else:
                self.is_dragging = False # Soltamos el objeto

# Definir Contenedores (Zonas)
containers = [
    {"name": "POR HACER", "x": 50, "w": 350, "color": (50, 50, 50)},
    {"name": "EN PROCESO", "x": 450, "w": 350, "color": (100, 100, 50)},
    {"name": "TERMINADO", "x": 850, "w": 350, "color": (50, 100, 50)}
]

# Crear las tareas (objetos movibles)
tasks = [
    DragObject("Estudiar Python", [70, 150], (200, 0, 200)),
    DragObject("Deploy App", [70, 250], (0, 200, 200)),
    DragObject("Comer Pizza", [70, 350], (0, 0, 200)),
    DragObject("Gym", [70, 450], (200, 100, 50)),
]

def draw_ui(img, items):
    overlay = img.copy()
    
    # 1. Dibujar Contenedores (Columnas)
    h, w, _ = img.shape
    for c in containers:
        cv2.rectangle(overlay, (c["x"], 50), (c["x"] + c["w"], h - 50), c["color"], -1)
        cv2.putText(img, c["name"], (c["x"] + 20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Aplicar transparencia a los contenedores
    alpha = 0.4
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # 2. Dibujar Tareas (Cajas)
    for task in items:
        x, y = task.pos
        # Color diferente si se está moviendo
        box_color = (100, 255, 100) if task.is_dragging else task.color
        
        cv2.rectangle(img, (x, y), (x + task.w, y + task.h), box_color, -1)
        cv2.rectangle(img, (x, y), (x + task.w, y + task.h), (255, 255, 255), 2) # Borde blanco
        cv2.putText(img, task.text, (x + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return img

# --- BUCLE PRINCIPAL ---
while True:
    success, img = cap.read()
    if not success: break

    # Espejo (flip) para que sea intuitivo mover la mano
    img = cv2.flip(img, 1)
    
    # Convertir a RGB para MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    cursor_pos = (0, 0)
    is_pinching = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Dibujar los nodos de la mano
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Obtener coordenadas del dedo INDICE (punto 8) y PULGAR (punto 4)
            h, w, _ = img.shape
            idx_x = int(hand_landmarks.landmark[8].x * w)
            idx_y = int(hand_landmarks.landmark[8].y * h)
            thumb_x = int(hand_landmarks.landmark[4].x * w)
            thumb_y = int(hand_landmarks.landmark[4].y * h)
            
            # Calcular distancia entre indice y pulgar (detectar "Pinza")
            distance = np.hypot(idx_x - thumb_x, idx_y - thumb_y)
            
            # Punto medio entre dedos (será nuestro cursor)
            cx, cy = (idx_x + thumb_x) // 2, (idx_y + thumb_y) // 2
            cursor_pos = (cx, cy)

            # Si la distancia es menor a 40px, consideramos que estás "agarrando"
            if distance < 40:
                is_pinching = True
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED) # Cursor verde
            else:
                cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED) # Cursor rojo

    # Actualizar lógica de objetos
    if cursor_pos != (0, 0):
        for task in tasks:
            task.update(cursor_pos, is_pinching)

    # Dibujar todo
    img = draw_ui(img, tasks)

    cv2.imshow("Control Gestual - Libre Albedrio", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()