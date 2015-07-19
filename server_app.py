#this file contains the server application code.

from messages import *
from socket import *
from threading import *
from time import *
import pickle
import socketserver
import inspect


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

        self.groups = []

        self.announce_thread = Thread(target=self.announce_exec)
        self.announce_thread.daemon = True
        self.announce_thread.start()

        global global_server
        global_server = self

        self.server = ThreadedTCPServer((gethostname(), CONNECTION_PORT), TCPRequestHandler)
        self.server.serve_forever()

    def shutdown(self):
        self.should_shutdown = True

    # thread to send out an announcement that this server exists every second
    def announce_exec(self):
        announcer = socket(AF_INET, SOCK_DGRAM)
        announcer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        announcer.connect(("255.255.255.255", ANNOUNCE_PORT))

        address = gethostbyname(gethostname())

        announcement = AnnouncementData(address, "name")

        while not self.should_shutdown:
            announcer.send(pickle.dumps(announcement))
            sleep(1)

    # this function should be in it's own thread and handles incoming network data
    # not using a socket server here because
    def process_new_request(self, handler):

        try:
            data = pickle.load(handler.rfile)
            # first data should be login data
            # FIXME: Borg: validate login data here, skipping for now
            inspect.isclass(data)

        # except:
        finally:
            pass

        while not self.should_shutdown:
            data = pickle.load(handler.rfile)
            # process each packet here


def server_main():
    server = ServerApp()  # init waits forever as it starts the TCP server
    # server.wait_for_shutdown()

if __name__ == "__main__":
    server_main()