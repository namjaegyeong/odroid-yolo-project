import cv2

cap = cv2.VideoCapture(0)

ret, frame = cap.read()

print(ret)

if ret:
    cv2.imwrite("test.jpg", frame)
    print("saved test.jpg")

cap.release()