import cv2
import time
import mediapipe as mp
import serial
import math

CAMERA = 0
PORT = "COM23"

py_serial = serial.Serial(
    port=PORT,  
    baudrate=9600,
)

mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 1, 0.7, 0.5)
tipIds = [4, 8, 12, 16, 20]

cam_width, cam_height = 640, 480
FRAME = 100
 
cap = cv2.VideoCapture(CAMERA)
if not cap.isOpened():
    raise Exception("ValueError : Cannot make connection with CAMERA")
cap.set(3, cam_width)
cap.set(4, cam_height)

prev_state = True
pprev_state = False
 
while True:
    success, img = cap.read()
    if not success:
        raise Exception("ValueError : Cannot read Frame from CAM")
    # 손 찾기
    result_img = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if result_img.multi_hand_landmarks:
        for handLms in result_img.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # 위치 찾기
    xList = []
    yList = []
    landmarks = []  
    if result_img.multi_hand_landmarks:
        myHand = result_img.multi_hand_landmarks[0]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            xList.append(cx)
            yList.append(cy)
            landmarks.append([id, cx, cy])
            cv2.circle(img, (cx, cy), 6, (255, 255, 0), cv2.FILLED)
        xmin, xmax = min(xList), max(xList)
        ymin, ymax = min(yList), max(yList)
        cv2.rectangle(img, (min(xList)-20, min(yList)-20), (max(xList)+20, max(yList)+20), (0, 0, 255), 2)
        
    output = img.copy()

    if len(landmarks) != 0:
        # 검지 들기 판단
        x1, y1 = landmarks[8][1:]
        x2, y2 = landmarks[12][1:]

        fingers = []
        if landmarks[tipIds[0]][1] < landmarks[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1, 5):
            if landmarks[tipIds[id]][2] < landmarks[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        # 사각형 그리기
        cv2.rectangle(img, (FRAME, FRAME), (cam_width - FRAME, cam_height - FRAME), (205, 250, 255), -1)

        # 9분할된 영역에 색상 채우기
        cv2.rectangle(img, (FRAME, FRAME), (cam_width // 3, cam_height // 3), (205, 250, 255), -1)  # 상단 왼쪽 영역
        cv2.rectangle(img, (cam_width // 3, FRAME), (cam_width * 2 // 3, cam_height // 3), (0, 165, 255), -1)  # 상단 중앙 영역
        cv2.rectangle(img, (cam_width * 2 // 3, FRAME), (cam_width - FRAME, cam_height // 3), (205, 250, 255), -1)  # 상단 오른쪽 영역
        cv2.rectangle(img, (FRAME, cam_height // 3), (cam_width // 3, cam_height * 2 // 3), (0, 165, 255), -1)  # 중앙 왼쪽 영역
        cv2.rectangle(img, (cam_width // 3, cam_height // 3), (cam_width * 2 // 3, cam_height * 2 // 3), (205, 250, 255), -1)  # 중앙 중앙 영역
        cv2.rectangle(img, (cam_width * 2 // 3, cam_height // 3), (cam_width - FRAME, cam_height * 2 // 3), (0, 165, 255), -1)  # 중앙 오른쪽 영역
        cv2.rectangle(img, (FRAME, cam_height * 2 // 3), (cam_width // 3, cam_height - FRAME), (205, 250, 255), -1)  # 하단 왼쪽 영역
        cv2.rectangle(img, (cam_width // 3, cam_height * 2 // 3), (cam_width * 2 // 3, cam_height - FRAME), (0, 165, 255), -1)  # 하단 중앙 영역
        cv2.rectangle(img, (cam_width * 2 // 3, cam_height * 2 // 3), (cam_width - FRAME, cam_height - FRAME), (205, 250, 255), -1)  # 하단 오른쪽 영역
        
        img = cv2.addWeighted(img, 0.5, output, 1 - .5, 0, output)

        if fingers[1] == 1 and fingers[2] == 0:
            if 213 < x1 and x1 < 426:
                if y1 > 320:
                    print("down")
                    py_serial.write('b'.encode())
                elif y1 < 160:
                    print("up")
                    py_serial.write('a'.encode())
            elif 160 < y1 and y1 < 320:
                if x1 > 213:
                    print("left")
                    py_serial.write('c'.encode())
                elif x1 < 426:
                    print("right")
                    py_serial.write('d'.encode())
        
        if fingers[1] == 1 and fingers[2] == 1:
            x1, y1 = landmarks[8][1:]
            x2, y2 = landmarks[12][1:]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 3)
            cv2.circle(img, (x1, y1), 6, (0, 255, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 6, (0, 255, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 6, (0, 255, 255), cv2.FILLED)
        
            if math.hypot(x2-x1, y2-y1) < 20:
                if pprev_state == False:
                    pprev_state = True
                    continue
                if prev_state == False:
                    cv2.circle(img, (cx, cy), 6, (0, 255, 0), cv2.FILLED)
                    print("click!")
                    py_serial.write('e'.encode())
                    time.sleep(1)
                pprev_state = False
                prev_state = True
            else:
                if prev_state == True:
                    prev_state = False
 
    cv2.imshow("OpenCV / AI robotics", cv2.flip(img, 1))
    cv2.setWindowProperty("OpenCV / AI robotics", cv2.WND_PROP_TOPMOST, 1)
    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyAllWindows()
        break
  
