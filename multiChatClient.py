from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
import signal
import sys
import os


class SocketClient:
    def __init__(self, game_id, user_id):
        self.HOST = "dorm.7ao7ao.com"
        self.PORT = 2333
        self.BUFSIZ = 1000000
        self.ADDR = (self.HOST, self.PORT)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(self.ADDR)
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()
        self.game_id = str(game_id)
        self.user_id = str(user_id)

        self.send(game_id + ':' + user_id)

        self.input_file_content = ""

    def close(self):
        self.sock.close()

    def report_update(self):
        report = "{CHANGEREPORT}"+self.input_file_content
        self.send(report)

    def receive(self):
        """ Handles receiving of messages. """
        while True:
            try:
                msg = self.sock.recv(self.BUFSIZ).decode("utf8")
                print("[Broadcast] "+msg)
                if msg.startswith(self.game_id+':') and msg.find("{CHANGEREPORT}"):
                    with open('output.txt', 'w') as f:
                        start_idx = msg.find(": ")+2+len("{CHANGEREPORT}")
                        f.write(msg[start_idx:])
            except OSError:  # Possibly client has left the chat.
                break

    def send(self, msg, event=None):
        """ Handles sending of messages. """
        self.sock.send(bytes(msg, "utf8"))


if __name__ == '__main__':
    client = SocketClient(input("Game ID: "), input("User ID: "))

    filename = 'output.txt'
    print("Watching {} ...".format(filename))

    def input_changed():
        try:
            with open(filename, 'r') as f:
                new_file = f.read()
                if client.input_file_content == new_file:
                    print("No change detected")
                    return False
                else:
                    client.input_file_content = new_file
                    print("[Log] Change detected")
                    return True
        except Exception as e:
            print("File not found")
            return False

    def handler(s, f):
        client.send("#quit")
        client.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)

    time.sleep(1)
    input_changed()
    client.report_update()
    while True:
        if input_changed():
            client.report_update()
        time.sleep(1)
