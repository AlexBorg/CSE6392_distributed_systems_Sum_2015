# this file contains all the messages to be sent between the client and the server
# It also contains connection port information and any defines needed by both

import collections

ANNOUNCE_PORT = 2000
CONNECTION_PORT = 2001

MessageData = collections.namedtuple('MessageData', 'group message')

LoginData = collections.namedtuple('LoginData', 'username password')

# join is true for joining, and false for leaving
GroupSubscriptionData = collections.namedtuple('GroupSubscriptionData', 'group join')

AnnouncementData = collections.namedtuple('AnnouncementData', 'address name')
