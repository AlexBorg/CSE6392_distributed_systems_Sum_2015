# this file contains all the messages to be sent between the client and the server
# It also contains connection port information and any defines needed by both

ANNOUNCE_PORT = 2000
CONNECTION_PORT = 2001


class MessageData:
    def __init__(self, group, message):
        self.group = group
        self.message = message


class LoginData:
    def __init__(self, username="", password=""):
        self.username = username
        self.password = password


class GroupSubscriptionData:
    def __init__(self, group="", join=True):
        self.group = group
        self.join = join  # join is true for joining, and fasle for leaving


class AnnouncementData:
    def __init__(self, address="", name=""):
        self.address = address
        self.name = name
