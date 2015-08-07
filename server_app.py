#!/usr/bin/python3
# this file contains the server application code.
from messages import *
import pickle
import socketserver
import traceback
import shelve
from collections import namedtuple, defaultdict
from queue import Queue
from threading import Thread

ConnectionInfo = namedtuple("ConnectionInfo", "user conn out_q")

user_db = shelve.open('users.db', writeback=True)
groups = set()
connections = set()
group_membership = defaultdict(set)
input_q = Queue()

class MsgHandlerThread(Thread):
    daemon = True

    def run(self):
        """Handle messages as they are added to the input message queue by client threads"""

        while True:
            conn, msg = input_q.get()
            print(msg)

            # Look for a handler function for message named handle_<message type> and call it
            handler = getattr(self, "handle_" + type(msg).__name__, None)
            if handler:
                handler(conn, msg)
            else:
                print("No handler for", str(type(msg)))

    def announce_groups(self):
        """Tell every client about the current room list"""
        for conn in connections:
            conn.out_q.put(MsgGroupList(sorted(groups)))

    def handle_MessageData(self, conn, msg):
        """Relay messages to every client -- filtering is done on that end"""
        for client_conn in connections:
            text = "{}: {}\n".format(conn.user, msg.message)
            client_conn.out_q.put(MessageData(msg.group, text))

    def handle_CreateGroupMsg(self, conn, msg):
        """Create a group if it exists otherwise return error"""
        if msg.name in groups:
            conn.out_q.put(ChatErrorMsg("Group '{}' already exists".format(msg.name)))
        else:
            groups.add(msg.name)
            self.announce_groups()

    def handle_GroupSubscriptionData(self, conn, msg):
        """Notify everybody that a user has joined or left a room"""
        if msg.group in groups:
            if msg.join:
                group_membership[conn.user].add(msg.group)
            else:
                group_membership[conn.user].discard(msg.group)

            text = "{} has {}...\n".format(conn.user, "joined" if msg.join else "left")
            for conn in connections:
                conn.out_q.put(MessageData(msg.group, text))

    def handle_UserDisconnectMsg(self, conn, msg):
        """Remove user and generate group leave event for each group they were in"""
        connections.discard(conn)
        if not any(conn.user == c.user for c in connections):
            for group in set(group_membership[conn.user]):
                self.handle_GroupSubscriptionData(conn, GroupSubscriptionData(group, False))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True


class ServerApp(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.
    """
    def handle(self):
        """
        this function should be in it's own thread and handles incoming network data
        :param handler: StreamRequestHandler that controls the socket
        :return: always None
        """
        try:
            # first data should be login data or registration request
            user = self.handle_login()
            if not user:
                return

            # Store connection info for this client
            conn = ConnectionInfo(user, self, Queue())
            connections.add(conn)

            # Start output data thread for this client
            t = Thread(target=self.output_task, args=[conn.out_q])
            t.daemon = True
            t.start()

            # Update client state
            self.send_message(MsgGroupList(sorted(groups)))

            # Use this thread to handle input data from this client
            while True:
                data = pickle.load(self.rfile)
                input_q.put((conn, data))

        except EOFError:
            pass
        except Exception:
            traceback.print_exc()

        input_q.put((conn, UserDisconnectMsg()))

    def send_message(self, msg):
        pickle.dump(msg, self.wfile)

    def handle_login(self):
        while True:
            data = pickle.load(self.rfile)

            if isinstance(data, LoginData):
                # Login -- succeeds if user is already in db and password matches
                if data.username not in user_db or user_db[data.username] != data.password:
                    self.send_message(LoginRegisterResponse(False, "Error: User/Password do not match"))
                else:
                    self.send_message(LoginRegisterResponse(True, ""))
                    return data.username

            elif isinstance(data, RegisterRequest):
                # Registration -- succeeds if user can be added to db
                if data.username in user_db:
                    self.send_message(LoginRegisterResponse(False, "Error: User already exists"))
                else:
                    user_db[data.username] = data.password
                    user_db.sync()
                    self.send_message(LoginRegisterResponse(True, ""))
                    return data.username
            else:
                # Login or register must be first message
                return None

    def output_task(self, q):
        while True:
            m = q.get()
            pickle.dump(m, self.wfile)

if __name__ == "__main__":
    MsgHandlerThread().start()

    server = ThreadedTCPServer(('', CONNECTION_PORT), ServerApp)
    server.serve_forever()
