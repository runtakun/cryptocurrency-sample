from distutils.version import StrictVersion
import json

PROTOCOL_NAME = 'simple_bitcoin_protocol'
MY_VERSION = '0.1.0'

MSG_ADD = 0
MSG_REMOVE = 1
MSG_CORE_LIST = 2
MSG_REQUEST_CORE_LIST = 3
MSG_PING = 4
MSG_ADD_ADD_EDGE = 5
MSG_REMOVE_EDGE = 6

ERR_PROTOCOL_UNMATCH = 0
ERR_VERSION_UNMATCH = 1
OK_WITH_PAYLOAD = 2
OK_WITHOUT_PAYLOAD = 3


class MessageManager:
    def __init__(self):
        print('Initializing MessageManager...')

        self.protocol = 'protocol'
        self.version = 'version'
        self.msg_type = 'msg_type'
        self.payload = 'payload'
        self.my_port = 'my_port'

    def build(self, msg_type, my_port=50082, payload=None):
        message = {
            self.protocol: PROTOCOL_NAME,
            self.version: MY_VERSION,
            self.msg_type: msg_type,
            self.my_port: my_port,
        }

        if payload is not None:
            message[self.payload] = payload

        return json.dumps(message)

    def parse(self, msg):
        content = json.loads(msg)
        msg_ver = StrictVersion(content[self.version])

        cmd = msg[self.msg_type]
        payload = msg[self.payload]

        if msg[self.protocol] != PROTOCOL_NAME:
            return 'error', ERR_PROTOCOL_UNMATCH, None, None
        elif msg_ver > StrictVersion(MY_VERSION):
            return 'error', ERR_VERSION_UNMATCH, None, None
        elif cmd == MSG_CORE_LIST:
            return 'ok', OK_WITH_PAYLOAD, cmd, payload
        else:
            return 'ok', OK_WITHOUT_PAYLOAD, cmd, None
