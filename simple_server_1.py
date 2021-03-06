import signal
from time import sleep

from core.server_core import ServerCore

my_p2p_server = None


def signal_handler(signal, frame):
    shutdown_server()


def shutdown_server():
    global my_p2p_server
    my_p2p_server.shutdown()


def main():
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    global my_p2p_server
    my_p2p_server = ServerCore(50082)
    my_p2p_server.start()


if __name__ == '__main__':
    main()
