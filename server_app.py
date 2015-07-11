#this file contains the server application code.

from messages import *
from socket import *
from threading import *
from time import *
import pickle


class ServerApp:
    def __init__(self):
        self.should_shutdown = False
        self.listener = socket(AF_INET, SOCK_STREAM)

        self.connection_streams = []

        self.announce_thread = Thread(target=self.announce_exec)
        self.announce_thread.daemon = True
        self.announce_thread.start()
        self.listen_thread = Thread(target=self.listen_exec)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def wait_for_shutdown(self):
        self.listen_thread.join()

    def announce_exec(self):
        announcer = socket(AF_INET, SOCK_DGRAM)
        announcer.connect(("255.255.255.255", ANNOUNCE_PORT))

        address = gethostbyname(gethostname())

        announcement = AnnouncementData(address, "name")

        while not self.should_shutdown:
            announcer.send(pickle.dumps(announcement))
            sleep(1)

    def listen_exec(self):
        self.listener.bind((gethostname(), CONNECTION_PORT))
        self.listener.listen(25)

        while not self.should_shutdown:
            client_socket, address = self.listener.accept()
            connection_thread = Thread(target=self.connection_exec(), args=(client_socket,))
            connection_thread.daemon = True
            connection_thread.start()

    def connection_exec(self, client_socket):
        f = client_socket.makefile('rb', buffer_size)
        data = pickle.load(f)
        #FIXME: check data payload is a LoginData

        f.close()


def server_main():
    server = ServerApp()
    server.wait_for_shutdown()

if __name__ == "__main__":
    server_main()