
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
    def __init__(self):
        self.should_shutdown = False
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connected = False

        self.server_list = set()
        self.group_list = set()  # FIXME: Borg: currently this is not being populated. Need new message system to get
        #  these to the client

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
            return -1, "ERROR: not connected"
        # package data here
        message_data = MessageData(group, message)
        self.connection.send(pickle.dumps(message_data))
        return 0, ""

    def join_group(self, group):
        if not self.connected:
            return -1, "ERROR: not connected"
        # package data here
        group_data = GroupSubscriptionData(group, True)
        self.connection.send(pickle.dumps(group_data))
        return 0, ""

    def leave_group(self, group):
        if not self.connected:
            return -1, "ERROR: not connected"
        # package data here
        group_data = GroupSubscriptionData(group, False)
        self.connection.send(pickle.dumps(group_data))
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

        self.connection.connect((target.address, CONNECTION_PORT))

        # package data here
        login = LoginData(username, password)

        self.connection.send(pickle.dumps(login))
        data = self.connection.recv(4096)
        if data == '':
            return -1, "ERROR, connection closed"

        self.connection.setblocking(False)
        self.connected = True
        return 0, ""

    def disconnect_server(self):
        self.connection.close()
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connected = False

    def get_server_names(self):
        return self.server_list.copy()

    def get_group_names(self):
        return self.group_list.copy()

    def find_servers(self):
        while not self.should_shutdown:
            chunk = self.announcement.recv(2048)
            if chunk == '':
                raise RuntimeError("socket connection broken")

            announcement_data = pickle.loads(chunk)
            # add server name to list
            self.server_list.add(announcement_data)

    def check_messages(self):
        """
        should be called periodically by the GUI client.
        :return: None if no message, or message_data if data received
        """
        if not self.should_shutdown and self.connected:
            chunk = self.connection.recv(2048)
            if not chunk == '':
                return pickle.loads(chunk)
        return None

