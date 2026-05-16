import cv2
import numpy as np
import mediapipe as mp

brush_thickness = 15
eraser_thickness = 50
draw_color = (248, 213, 175) 

cap = cv2.VideoCapture(0)
cap.set(3, 1280) 
cap.set(4, 720) 

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

img_canvas = np.zeros((720, 1280, 3), np.uint8)

xp, yp = 0, 0 

print("🟢 LISTO: Índice arriba = DIBUJAR | Dos dedos = PAUSA | 'c' = LIMPIAR")

while True:
    success, img = cap.read()
    if not success: break
    
    img = cv2.flip(img, 1)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if len(lm_list) != 0:
                x1, y1 = lm_list[8][1:]
                x2, y2 = lm_list[12][1:]

                fingers = []
                if lm_list[8][2] < lm_list[6][2]: fingers.append(1)
                else: fingers.append(0)
                # Medio
                if lm_list[12][2] < lm_list[10][2]: fingers.append(1)
                else: fingers.append(0)
                if fingers[0] and fingers[1]:
                    xp, yp = 0, 0 
                    cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), draw_color, cv2.FILLED)

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
    
    # Teclas
    key = cv2.waitKey(1)
    if key & 0xFF == ord('c'): 
        img_canvas = np.zeros((720, 1280, 3), np.uint8)
    if key & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()