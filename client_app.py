#!/usr/bin/python3
from messages import *
from socket import *
from threading import Thread
from queue import Queue
import traceback
import pickle

# base class to control client communication with the server. It provides a callback
# function for posting when new messages come in from the server
# callback function prototype is:
# message_callback(group, message)
# group is the group where the message came from, and message is the message text.
#
# currently all functions return a two tuple. the first is the int return code (0
# is success) and the second is return code text.
class ClientApp:
    def __init__(self):
        self.connection = None
        self.input_q = Queue()
        self.msg_listeners = list()

    def register_message_listener(self, listener):
        """Register object to listen for events. Object must implement a method called handle_<MessageName> for each
        message type that it wants to handle."""
        self.msg_listeners.append(listener)

    def handle_input(self):
        """Loop for handling input from a socket and outputting to a queue. Run inside a thread."""
        f = self.connection.makefile("rb")
        try:
            while True:
                self.input_q.put(pickle.load(f))
        except (EOFError, ConnectionError, OSError) as e:
            self.close_connection()
            self.input_q.put(ServerErrorMsg("Connection closed by server"))

    def connect_server(self, server_addr):
        if self.connection:
            return

        try:
            self.connection = socket(AF_INET, SOCK_STREAM)
            self.connection.connect((server_addr, CONNECTION_PORT))

            self.input_thread = Thread(target=self.handle_input)
            self.input_thread.daemon = True
            self.input_thread.start()

        except (ConnectionError, OSError) as e:
            traceback.print_exc()
            self.close_connection()
            self.input_q.put(ServerErrorMsg(str(e)))

    def close_connection(self):
        try:
            self.connection.close()
        except (OSError, AttributeError):
            pass

        self.connection = None

    def send_message(self, msg):
        if self.connection:
            self.connection.send(pickle.dumps(msg))

    def check_messages(self):
        """
        should be called periodically by the GUI client.
        :return: None if no message, or message_data if data received
        """
        while not self.input_q.empty():
            msg = self.input_q.get()
            print("Got", type(msg), ":", str(msg))
            for listener in self.msg_listeners:
                # Call appropriate handler function in listener if it exists
                fn = getattr(listener, "handle_" + type(msg).__name__, None)
                if fn:
                    fn(msg)
