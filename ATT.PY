import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from flask import Flask, render_template, Response, jsonify


# from PIL import ImageGrab

path = 'Images'
images = []
classNames = []

# Check if Images directory exists
if not os.path.exists(path):
    print(f"Warning: '{path}' directory not found. Please create it and add face images.")
    os.makedirs(path, exist_ok=True)
    print(f"Created '{path}' directory. Please add face images (jpg, png) to it.")
else:
    myList = os.listdir(path)
    print(f"Found {len(myList)} files in {path}: {myList}")
    for cl in myList:
        if cl.lower().endswith(('.jpg', '.jpeg', '.png')):
            curImg = cv2.imread(f'{path}/{cl}')
            if curImg is not None:
                images.append(curImg)
                classNames.append(os.path.splitext(cl)[0])
    print(f"Loaded {len(classNames)} images: {classNames}")


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    # Create attendance.csv if it doesn't exist
    if not os.path.exists('attendance.csv'):
        with open('attendance.csv', 'w') as f:
            f.write('Name,Time\n')
    
    with open('attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            if line.strip():  # Skip empty lines
                entry = line.split(',')
                nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')


if len(images) == 0:
    print("Error: No images found to encode. Please add face images to the 'Images' directory.")
    encodeListKnown = []
else:
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

# Flask app setup
app = Flask(__name__)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Global variable to track last attendance
last_attendance = {}

def generate_frames():
    while True:
        success, img = cap.read()
        if not success:
            break
        
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        
        # Only process if we have known encodings
        if len(encodeListKnown) > 0:
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    # Mark attendance only once per session (avoid duplicates)
                    now = datetime.now()
                    current_time = now.strftime('%H:%M:%S')
                    if name not in last_attendance or last_attendance[name] != current_time:
                        markAttendance(name)
                        last_attendance[name] = current_time
                        print(f"Attendance marked for {name} at {current_time}")
        else:
            # Display message if no encodings are available
            cv2.putText(img, "No face images loaded", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def attendance():
    attendance_data = []
    if os.path.exists('attendance.csv'):
        with open('attendance.csv', 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        attendance_data.append({'name': parts[0], 'time': parts[1]})
    return jsonify(attendance_data)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)