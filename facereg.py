import cv2
import pickle

# ---------- LOAD TRAINED MODEL ----------
# LBPH face recognizer (comes with opencv-contrib)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_model.yml")  # trained model file

# Load label map (name <-> id)
with open("labels.pickle", "rb") as f:
    label_map = pickle.load(f)

# Reverse mapping: id -> name
id_to_name = {v: k for k, v in label_map.items()}
print("Loaded labels:", id_to_name)

# Haar cascade for face detection
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# ---------- LIVE RECOGNITION FUNCTION ----------

def live_face_recognition():
    cap = cv2.VideoCapture(0)   # 0 = default camera

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Live face recognition started.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Convert to grayscale (LBPH works with gray images)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            # Crop face
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))

            # Predict id and confidence
            label_id, confidence = recognizer.predict(face_roi)

            # LBPH: lower confidence = better match
            # Tune this threshold as needed (try 70–100 range)
            if confidence < 80:
                name = id_to_name.get(label_id, "Unknown")
                print(f"Recognized: {name} with confidence {confidence:.2f}")
            else:
                name = "Unknown"

            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
            text = f"{name} ({int(confidence)})"
            cv2.putText(
                frame,
                text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # Show the frame
        cv2.imshow("Live Face Recognition - Press 'q' to exit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    live_face_recognition()
