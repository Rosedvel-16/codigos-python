import cv2
import mediapipe as mp
import math

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

mp_draw = mp.solutions.drawing_utils

tip_ids = [4, 8, 12, 16, 20]

def get_fingers_status(lm_list):
    """Devuelve una lista [0, 1, 0, 1, 1] indicando qué dedos están levantados"""
    fingers = []
    
    if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

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
    results = hands.process(img_rgb)
    
    msg = "" # Mensaje a mostrar

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            if len(lm_list) != 0:
                fingers = get_fingers_status(lm_list)
                
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

            cv2.rectangle(img, (20, 20), (450, 120), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, msg, (30, 100), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)

    cv2.imshow("Traductor de Senas (BETA)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()