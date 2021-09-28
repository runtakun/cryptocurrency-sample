import os
from concurrent.futures import ThreadPoolExecutor
import socket


def _handle_message(args_tuple):
    conn, addr, data_sum = args_tuple
    while True:
        data = conn.recv(1024)
        data_sum = data_sum + data.decode('utf-8')

        if not data:
            break

        if data_sum != '':
            print(data_sum)


def _get_myip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    executor = ThreadPoolExecutor(max_workers=os.cpu_count())

    my_host = _get_myip()
    print('my ip address is now ...', my_host)
    my_socket.bind((my_host, 50030))
    my_socket.listen(1)

    while True:
        print('Waiting for connection ...')
        conn, addr = my_socket.accept()
        print('Connected by .. ', addr)
        data_sum = ''
        executor.submit(_handle_message, (conn, addr, data_sum))


if __name__ == '__main__':
    main()
