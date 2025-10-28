import cv2
import dlib
from scipy.spatial import distance
import serial
import time

# --- SERIAL SETUP ---
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

# --- DLIB SETUP ---
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    r"C:\Users\abink\OneDrive\Desktop\EC\microproject\shape_predictor_68_face_landmarks.dat"
)

LEFT_EYE = list(range(36, 42))
RIGHT_EYE = list(range(42, 48))

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# --- CONSTANTS ---
EAR_THRESHOLD = 0.23
CONSEC_FRAMES = 15

closed_frames = 0
drowsy = False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

        left_eye = [landmarks_points[i] for i in LEFT_EYE]
        right_eye = [landmarks_points[i] for i in RIGHT_EYE]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        if ear < EAR_THRESHOLD:
            closed_frames += 1
            if closed_frames >= CONSEC_FRAMES and not drowsy:
                print("DROWSY 😴")
                arduino.write(b'DROWSY\n')
                drowsy = True
        else:
            closed_frames = 0
            if drowsy:
                print("AWAKE 😃")
                arduino.write(b'AWAKE\n')
                drowsy = False

        # Display info
        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        text = "DROWSY" if drowsy else "AWAKE"
        color = (0,0,255) if drowsy else (0,255,0)
        cv2.putText(frame, text, (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    cv2.imshow("Drowsiness Detection", frame)
    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
