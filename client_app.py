
from messages import *
from socket import *
from threading import *
import pickle


# base class to control client communication with the server. It provides a callback
# function for posting when new messages come in from the server
# callback function prototype is:
# message_callback(group, message)
# group is the group where the message came from, and message is the message text.
#
# currently all functions return a two tupple. the first is the int return code (0
# is success) and the second is return code text.
# FIXME: Borg: Consider changing to raising an exception.
class ClientApp:
    def __init__(self, message_callback):
        self.should_shutdown = False
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connected = False

        self.server_list = set()
        self.announcement = socket(AF_INET, SOCK_DGRAM)
        self.announcement.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.announcement.bind((gethostname(), ANNOUNCE_PORT))
        self.announce_thread = Thread(target=self.find_servers)
        self.announce_thread.daemon = True
        self.announce_thread.start()

    def shutdown(self):
        self.should_shutdown = True
        self.announcement.close()
        self.announce_thread.join()

    def send_message(self, group, message):
        if not self.connected:
            return -1, "ERROR: already connected"
        # package data here

        #self.connection.send(data)
        return 0, ""

    def join_group(self, group):
        if not self.connected:
            return -1, "ERROR: already connected"
        # package data here

        #self.connection.send(data)
        return 0, ""

    def leave_group(self, group):
        if not self.connected:
            return -1, "ERROR: already connected"
        # package data here

        #self.connection.send(data)
        return 0, ""

    def connect_server(self, server_name, username, password):
        if self.connected:
            return -1, "ERROR: already connected"

        target = ""
        for server in self.server_list:
            if server.name == server_name:
                target = server
                break

        if target == "":
            return -1, "ERROR: invalid server name"

        # package data here
        login = LoginData(username, password)

        self.connection.send(pickle.dumps(login))
        data = self.connection.recv(4096)
        if data == '':
            return -1, "ERROR, connection closed"

        self.connected = True
        return 0, ""

    def get_server_names(self):
        return self.server_list.copy()

    def find_servers(self):
        while not self.should_shutdown:
            chunk = self.announcement.recv(2048)
            if chunk == '':
                raise RuntimeError("socket connection broken")

            announcement_data = pickle.loads(chunk)
            # add server name to list
            self.server_list.add(announcement_data)

    def message_thread(self):
        while not self.should_shutdown and self.connected:
            chunk = self.connection.recv(2048)

