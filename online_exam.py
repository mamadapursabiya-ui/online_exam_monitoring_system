import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import sounddevice as sd
import numpy as np
import time
from ultralytics import YOLO

# === Configuration ===
MARKS_CORRECT = 2
MARKS_WRONG = -2
CHEAT_PENALTY = 0.25
TOTAL_QUESTIONS = 10
ELIGIBILITY_THRESHOLD = 10.0

# === Global State ===
score = 0.0
current_index = 0
cheating_start_times = {"face": None, "sound": None, "focus": None, "phone": None}
cheating_flags = {"face": False, "sound": False, "focus": False, "phone": False}
cheat_log = []
face_missing = False
sound_detected = False
focus_lost = False
user_answers = []

# === Load YOLOv8 model for phone detection ===
model = YOLO("yolov8n.pt")  # Small and fast model

# === Create GUI ===
root = tk.Tk()
root.title("Online Exam System")
root.geometry("1020x620")
root.configure(bg="#f0f0f0")

selected_option = tk.StringVar()
selected_index = [None]

questions = [
    {"question": "1. Capital of India?", "options": ["A. Mumbai", "B. Delhi", "C. Chennai", "D. Kolkata"], "answer": "B"},
    {"question": "2. Red planet?", "options": ["A. Earth", "B. Mars", "C. Venus", "D. Jupiter"], "answer": "B"},
    {"question": "3. Python is a?", "options": ["A. Snake", "B. Language", "C. Game", "D. Animal"], "answer": "B"},
    {"question": "4. Largest ocean?", "options": ["A. Indian", "B. Arctic", "C. Pacific", "D. Atlantic"], "answer": "C"},
    {"question": "5. Who discovered gravity?", "options": ["A. Newton", "B. Einstein", "C. Galileo", "D. Tesla"], "answer": "A"},
    {"question": "6. 1 byte = ?", "options": ["A. 4 bits", "B. 16 bits", "C. 8 bits", "D. 32 bits"], "answer": "C"},
    {"question": "7. Sun is a?", "options": ["A. Star", "B. Planet", "C. Galaxy", "D. Moon"], "answer": "A"},
    {"question": "8. Java is used for?", "options": ["A. Baking", "B. Coding", "C. Farming", "D. Sleeping"], "answer": "B"},
    {"question": "9. Fastest land animal?", "options": ["A. Lion", "B. Tiger", "C. Cheetah", "D. Horse"], "answer": "C"},
    {"question": "10. Formula of water?", "options": ["A. CO2", "B. O2", "C. H2O", "D. HCl"], "answer": "C"},
]

# === Layout ===
left = tk.Frame(root, bg="white", width=510, height=600)
left.pack(side="left", fill="both")
right = tk.Frame(root, bg="#f9f9f9", width=510, height=600)
right.pack(side="right", fill="both", expand=True)

cam_label = tk.Label(left, bg="white")
cam_label.pack(pady=10)

rules = tk.Label(left, text=(
    "\ud83d\udcdc Exam Rules:\n"
    "\u25aa Keep your face visible in camera\n"
    "\u25aa No mobile phone visible\n"
    "\u25aa No background sound or switching tabs\n"
    "\u25aa Correct: +2 | Wrong: -2 | Cheat: -0.25"
), justify="left", font=("Arial", 11), bg="white", fg="#333", anchor="w")
rules.pack(padx=10, pady=10, anchor="w")

cheat_label = tk.Label(left, text="", font=("Arial", 10, "bold"), fg="red", bg="white")
cheat_label.pack()

question_label = tk.Label(right, text="", font=("Arial", 16), wraplength=480, bg="#f9f9f9")
question_label.pack(pady=20)

option_buttons = []
def on_option_click(idx):
    if selected_index[0] == idx:
        option_buttons[idx].deselect()
        selected_index[0] = None
        selected_option.set("")
    else:
        for i, btn in enumerate(option_buttons):
            if i == idx:
                btn.select()
                selected_index[0] = idx
                selected_option.set(btn.cget("text")[0])
            else:
                btn.deselect()

for i in range(4):
    btn = tk.Checkbutton(
        right,
        text="",
        font=("Arial", 12),
        variable=tk.IntVar(),
        anchor="w",
        width=30,
        bg="#f9f9f9",
        relief="flat",
        indicatoron=True,
        command=lambda idx=i: on_option_click(idx)
    )
    btn.pack(anchor="w", padx=30, pady=2)
    option_buttons.append(btn)

next_btn = tk.Button(right, text="Next", font=("Arial", 12), bg="#007acc", fg="white", command=lambda: next_question())
next_btn.pack(pady=20)

result_label = tk.Label(right, text="", font=("Arial", 14), bg="#f9f9f9", fg="green")
result_label.pack()

def show_question():
    q = questions[current_index]
    selected_option.set("")
    selected_index[0] = None
    question_label.config(text=q["question"])
    for i, opt in enumerate(q["options"]):
        option_buttons[i].config(text=opt)
        option_buttons[i].deselect()

def next_question():
    global current_index, score
    user_answers.append(selected_option.get() or "None")
    if selected_option.get():
        correct = questions[current_index]["answer"]
        score += MARKS_CORRECT if selected_option.get() == correct else MARKS_WRONG
    current_index += 1
    if current_index < TOTAL_QUESTIONS:
        show_question()
    else:
        finish_exam()

def finish_exam():
    for btn in option_buttons:
        btn.pack_forget()
    next_btn.pack_forget()
    question_label.pack_forget()

    result = f"\u2705 Final Score: {score:.2f} / {TOTAL_QUESTIONS * MARKS_CORRECT}\n"
    result += "\u2705 Eligible\n" if score >= ELIGIBILITY_THRESHOLD else "\u274c Not eligible\n"
    result += "\n\ud83d\udcc4 Answers:\n"
    for i, ans in enumerate(user_answers):
        result += f"Q{i+1}: {ans} (Correct: {questions[i]['answer']})\n"
    if cheat_log:
        result += "\n\ud83d\udcc9 Cheating Detected:\n" + "\n".join([f"- {item}" for item in cheat_log])
    else:
        result += "\n\u2705 No cheating detected."
    result_label.config(text=result)

def apply_penalty(reason):
    global score
    score -= CHEAT_PENALTY
    msg = f"⚠️ Cheating: {reason} (-0.25)"
    if reason not in cheat_log:
        cheat_log.append(reason)
    cheat_label.config(text=msg)
    print(msg)
    root.after(3000, lambda: cheat_label.config(text=""))

def detect_cheating():
    now = time.time()
    for reason, active in zip(cheating_flags.keys(), [face_missing, sound_detected, focus_lost, phone_detected]):
        if active:
            if cheating_start_times[reason] is None:
                cheating_start_times[reason] = now
            elif now - cheating_start_times[reason] > 3 and not cheating_flags[reason]:
                apply_penalty(reason)
                cheating_flags[reason] = True
        else:
            cheating_start_times[reason] = None
            cheating_flags[reason] = False

# === Face & Phone Detection via Camera ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
phone_detected = False

def camera_loop():
    global face_missing, phone_detected
    cap = cv2.VideoCapture(0)
    def update_frame():
        nonlocal cap
        ret, frame = cap.read()
        if not ret:
            cam_label.after(100, update_frame)
            return

        # Face Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        face_missing = len(faces) == 0

        # Phone Detection (YOLO)
        results = model.predict(frame, imgsz=320, conf=0.5, verbose=False)
        labels = results[0].boxes.cls.cpu().numpy() if results[0].boxes is not None else []
        names = results[0].names
        detected_objects = [names[int(i)] for i in labels]
        phone_detected = "cell phone" in detected_objects

        detect_cheating()

        frame = cv2.resize(frame, (460, 360))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(img))
        cam_label.imgtk = imgtk
        cam_label.configure(image=imgtk)
        cam_label.after(100, update_frame)
    update_frame()

# === Mic Detection ===
def mic_loop():
    global sound_detected
    while True:
        audio = sd.rec(int(0.5 * 44100), samplerate=44100, channels=1)
        sd.wait()
        sound_detected = np.linalg.norm(audio) > 0.2
        detect_cheating()
        time.sleep(1)

# === Window Focus Detection ===
def on_focus_out(e): global focus_lost; focus_lost = True
def on_focus_in(e): global focus_lost; focus_lost = False
root.bind("<FocusOut>", on_focus_out)
root.bind("<FocusIn>", on_focus_in)

# === Start Everything ===
threading.Thread(target=camera_loop, daemon=True).start()
threading.Thread(target=mic_loop, daemon=True).start()
show_question()
root.mainloop()
