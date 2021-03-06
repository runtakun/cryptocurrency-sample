import threading


class CoreNodeList:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = set()

    def add(self, peer):
        """
        Core ノードをリストに追加する
        """
        with self.lock:
            print('Adding peer: ', peer)
            self.list.add(peer)
            print('Current Core list: ', self.list)

    def remove(self, peer):
        """
        Core ノードをリストから削除する
        """
        with self.lock:
            print('Removing peer: ', peer)
            self.list.remove(peer)
            print('Current Core list: ', self.list)

    def overwrite(self, new_list):
        """
        複数の peer の接続状況確認を行った後で一括での上書き処理をしたいような場合はこちら
        """
        with self.lock:
            print('core node list will be going to overwrite')
            self.list = new_list
            print('Current Core list: ', self.list)

    def get_list(self):
        """
        現在接続状態にある Peer の一覧を返却する
        """
        return self.list
