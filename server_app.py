# this file contains the server application code.

from messages import *
from socket import *
from threading import *
from time import *
import pickle
import socketserver


global_server = None


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class TCPRequestHandler(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        global global_server
        global_server.process_new_request(self)


class ServerApp:
    def __init__(self):
        self.should_shutdown = False
        self.listener = socket(AF_INET, SOCK_STREAM)

        self.groups = set()

        self.announce_thread = Thread(target=self.announce_exec)
        self.announce_thread.daemon = True
        self.announce_thread.start()

        global global_server
        global_server = self

        self.server = ThreadedTCPServer((gethostname(), CONNECTION_PORT), TCPRequestHandler)
        self.server.serve_forever()

    def shutdown(self):
        self.should_shutdown = True

    def announce_exec(self):
        """
        thread to send out an announcement that this server exists every second
        :return: always None
        """
        announcer = socket(AF_INET, SOCK_DGRAM)
        announcer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        announcer.connect(("255.255.255.255", ANNOUNCE_PORT))

        address = gethostbyname(gethostname())

        announcement = AnnouncementData(address, "name")

        while not self.should_shutdown:
            announcer.send(pickle.dumps(announcement))
            sleep(1)

    def process_new_request(self, handler):
        """
        this function should be in it's own thread and handles incoming network data
        :param handler: StreamRequestHandler that controls the socket
        :return: always None
        """
        #

        try:
            data = pickle.load(handler.rfile)
            # first data should be login data
            # FIXME: Borg: validate login data here, skipping for now
            if data is not LoginData:
                return

        # except:
        finally:
            pass

        handler.wfile(data)  # send data back so client knows connection is accepted

        while not self.should_shutdown:
            data = pickle.load(handler.rfile)
            # may need to lock here

            # process each packet here
            if data is GroupSubscriptionData:
                # FIXME: create group if it doesn't exist
                # Add this socket to the group so future messages can be sent
                print("trying to add group")
            elif data is MessageData:
                for group in self.groups:
                    # FIXME: if group matches data.group, send message to all sockets in the group
                    print("trying send message to group")


def server_main():
    server = ServerApp()  # init waits forever as it starts the TCP server
    # server.wait_for_shutdown()

if __name__ == "__main__":
    server_main()