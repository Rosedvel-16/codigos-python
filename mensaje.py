import cv2
import mediapipe as mp
import math
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            if len(lmList) != 0:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                dist_ok = math.hypot(x2 - x1, y2 - y1)
                medio_arriba = lmList[12][2] < lmList[10][2]
                anular_arriba = lmList[16][2] < lmList[14][2]
                menique_arriba = lmList[20][2] < lmList[18][2]
                if dist_ok < 30 and medio_arriba and anular_arriba and menique_arriba:
                    cv2.putText(img, "Eres jochis", (100, 200), 
                                cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
                    cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
    cv2.imshow("Detector Jochis", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()