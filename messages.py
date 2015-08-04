# this file contains all the messages to be sent between the client and the server
# It also contains connection port information and any defines needed by both

from collections import namedtuple

ANNOUNCE_PORT = 2000
CONNECTION_PORT = 2001

MessageData = namedtuple('MessageData', 'group message')
LoginData = namedtuple('LoginData', 'username password')
RegisterRequest = namedtuple('RegisterRequest', 'username password')
LoginRegisterResponse = namedtuple('LoginRegisterResponse', 'success error')
DisconnectedMsg = namedtuple('DisconnectedMsg', 'reason')
ServerErrorMsg = namedtuple('ServerErrorMsg', 'error')
CreateGroupMsg = namedtuple('CreateGroupMsg', 'name')
ChatErrorMsg = namedtuple('ChatErrorMsg', 'error')

# join is true for joining, and false for leaving
GroupSubscriptionData = namedtuple('GroupSubscriptionData', 'group join')

MsgGroupList = namedtuple('MsgGroupList', 'groups')
