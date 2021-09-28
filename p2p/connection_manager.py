import pickle
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from .message_manager import MessageManager, ERR_PROTOCOL_UNMATCH, ERR_VERSION_UNMATCH, OK_WITH_PAYLOAD, \
    OK_WITHOUT_PAYLOAD, MSG_ADD, MSG_CORE_LIST, MSG_REMOVE, MSG_PING, MSG_REQUEST_CORE_LIST
from .code_node_list import CoreNodeList

PING_INTERVAL = 1800


class ConnectionManager:
    def __init__(self, host, my_port):
        print('Initializing ConnectionManager...')
        self.host = host
        self.port = my_port
        self.core_node_set = CoreNodeList()
        self._add_peer((host, my_port))
        self.mm = MessageManager()
        self.ping_timer = None
        self.my_c_host = None
        self.my_c_port = None

    def start(self):
        t = threading.Thread(target=self._wait_for_access)
        t.start()

        self.ping_timer = threading.Timer(PING_INTERVAL, self._check_peers_connection)
        self.ping_timer.start()

    def join_network(self, host, port):
        self.my_c_host = host
        self.my_c_port = port
        self._connect_to_P2PNW(host, port)

    def _connect_to_P2PNW(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        msg = self.mm.build(MSG_ADD, self.port)
        s.sendall(msg.encode('utf-8'))
        s.close()

    def send_msg(self, peer, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer))
            s.sendall(msg.encode('utf-8'))
            s.close()
        except OSError:
            print('Connection failed for peer: ', peer)
            self._remove_peer(peer)

    def send_msg_to_all_peer(self, msg):
        print('send_msg_to_all_peer was called!')
        current_list = self.core_node_set.get_list()
        for peer in current_list:
            if peer != (self.host, self.port):
                print('message will be sent to ... ', peer)
                self.send_msg(peer, msg)

    def connection_close(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket.close()
        s.close()
        self.ping_timer.cancel()
        msg = self.mm.build(MSG_REMOVE, self.port)
        if self.my_c_host and self.my_c_port:
            self.send_msg((self.my_c_host, self.my_c_port), msg)

    def _wait_for_access(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(0)

        executor = ThreadPoolExecutor(max_workers=10)

        while True:
            print('Waiting for the connection ...')
            soc, addr = self.socket.accept()
            print('Connected by .. ', addr)
            data_sum = ''

            params = (soc, addr, data_sum)
            executor.submit(self._handle_message, params)

    def _handle_message(self, params):
        soc, addr, data_sum = params
        while True:
            data = soc.recv(1024)
            data_sum = data_sum + data.decode('utf-8')

            if not data:
                break

        if not data_sum:
            return

        result, reason, cmd, peer_port, payload = self.mm.parse(data_sum)
        print(result, reason, cmd, peer_port, payload)
        status = (result, reason)

        if status == ('error', ERR_PROTOCOL_UNMATCH):
            print('Error: Protocol name is not matched')
            return
        elif status == ('error', ERR_VERSION_UNMATCH):
            print('Error: Protocol version is not matched')
            return
        elif status == ('ok', OK_WITHOUT_PAYLOAD):
            if cmd == MSG_ADD:
                print('ADD node request was received!!')
                self._add_peer((addr[0], peer_port))
                if (addr[0], peer_port) == (self.host, self.port):
                    return
                else:
                    self._publish_core_list()
            elif cmd == MSG_REMOVE:
                print('REMOVE request was received!! from', addr[0], peer_port)
                self._remove_peer((addr[0], peer_port))
                self._publish_core_list()
            elif cmd == MSG_PING:
                print('PING node request was received!!')
                return
            elif cmd == MSG_REQUEST_CORE_LIST:
                print('List for Core nodes was requested!!')
                msg = self._make_core_list_message()
                self.send_msg((addr[0], peer_port), msg)
            else:
                print('received unknown command', cmd)
                return
        elif status == ('ok', OK_WITH_PAYLOAD):
            if cmd == MSG_CORE_LIST:
                print('Refresh the code node list...')
                new_core_set = pickle.loads(payload.encode('utf8'))
                print('latest code node list: ', new_core_set)
                self.core_node_set = new_core_set
            else:
                print('received unknown command', cmd)
                return
        else:
            print('Unexpected status', status)

    def _make_core_list_message(self):
        cl = pickle.dumps(self.core_node_set, 0).decode()
        return self.mm.build(MSG_CORE_LIST, self.port, cl)

    def _publish_core_list(self):
        msg = self._make_core_list_message()
        self.send_msg_to_all_peer(msg)

    def _add_peer(self, peer):
        """
        Core ノードをリストに追加する
        """
        self.core_node_set.add((peer))

    def _remove_peer(self, peer):
        """
        離脱したと判断される Core ノードをリストから削除する
        """
        self.core_node_set.remove(peer)

    def _check_peers_connection(self):
        """
        接続されている Core ノードすべての接続状況確認を行う。クラスの外からは利用しない想定。
        この接続処理は定期的に実行される
        """
        print('check_peers_connection was called')
        current_core_list = self.core_node_set.get_list()
        changed = False
        dead_c_node_set = list(filter(lambda p: not self._is_alive(p),
                                      current_core_list))

        if dead_c_node_set:
            changed = True
            print('Removing ', dead_c_node_set)
            current_core_list = current_core_list - set(dead_c_node_set)
            self.core_node_set.overwrite(current_core_list)

        current_core_list = self.core_node_set.get_list()
        print('current code node list:', current_core_list)

        if changed:
            self._publish_core_list()

        self.ping_timer = threading.Timer(PING_INTERVAL, self._check_peers_connection)
        self.ping_timer.start()

    def _is_alive(self, target):
        """
        有効ノード確認メッセージの送信

        :param target: 有効ノード確認メッセージの送り先となるノードの接続情報
                    （IPアドレスとポート番号）
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target))
            msg_type = MSG_PING
            msg = self.mm.build(msg_type)
            s.sendall(msg.encode('utf-8'))
            s.close()
            return True
        except OSError:
            return False
