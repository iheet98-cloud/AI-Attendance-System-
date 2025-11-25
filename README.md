**AI Attendance System**

This project implements an automated attendance system using **face recognition** and a **Flask-based web interface**, designed to replace the traditional manual attendance process still used in many schools. The system identifies students’ faces in real time through a webcam, marks their attendance automatically, and stores records securely in a CSV file.

## **Features**

* **Automated Face Recognition:** Detects and identifies registered faces using `face_recognition` and OpenCV.
* **Real-Time Video Stream:** A live camera feed is displayed through Flask for monitoring.
* **Automatic Attendance Logging:** When a face is recognized, the system records the name and timestamp in `attendance.csv`.
* **Web Interface:** Simple routes to display the main page, video stream, and attendance data.
* **Duplicate Prevention:** Ensures attendance is marked once per session for each student.
* **Easy Setup:** Just place student images in the `Images/` folder and run the script.

## **Project Structure**

```
├── ATT.PY                 # Main application file
├── Images/                # Store face images here (jpg/png)
├── attendance.csv          # Auto-generated attendance log
└── templates/
    └── index.html         # Web interface template
```

## **How It Works**

1. The system loads all images from the `Images/` directory and generates face encodings.
2. A webcam feed is processed frame-by-frame for face detection.
3. If a detected face matches a known encoding, the student’s attendance is marked with the current time.
4. Attendance records are accessible in JSON format through the `/attendance` route.

## **Requirements**

Install the required libraries:

```bash
pip install opencv-python face_recognition flask numpy
```

Ensure `cmake` and `dlib` dependencies are installed if required by your environment.

## **How to Run**

```bash
python ATT.PY
```

Then open:

```
http://127.0.0.1:5000/
```

## **Usage Notes**

* Store clear, front-facing images of each student in the `Images/` folder.
* File names (without extension) become the recognized names.
* The system auto-creates necessary folders and files if missing.

## **Future Enhancements**

* Database integration for long-term attendance management.
* User authentication for administrators.
* Mobile-friendly dashboard.
* Notifications for absent students.

---

If you want, I can also provide a **LICENSE**, **CONTRIBUTING.md**, or improve the README with badges, screenshots, or installation scripts.
