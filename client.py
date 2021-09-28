import socket
import argparse

parser = argparse.ArgumentParser(description='crypto currency client')
parser.add_argument('-ip', help='server ip address', required=True)
args = parser.parse_args()

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((args.ip, 50030))
my_text = "Hello! This is test message from my sample client!"
my_socket.sendall(my_text.encode('utf-8'))
