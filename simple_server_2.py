import signal
import argparse

from core.server_core import ServerCore

my_p2p_server = None


def signal_handler(signal, frame):
    shutdown_server()


def shutdown_server():
    global my_p2p_server
    my_p2p_server.shutdown()


def main():
    parser = argparse.ArgumentParser(description='crypto currency client')
    parser.add_argument('-list', nargs='+', help='server ip address', required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    global my_p2p_server
    my_p2p_server = ServerCore(50090, args.list[0], 50082)
    my_p2p_server.start()
    my_p2p_server.join_network()


if __name__ == '__main__':
    main()
