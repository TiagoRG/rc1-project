import os
import sys
import re
import socket
import threading
import struct
import signal
import datetime
import readline
import argparse


class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = "\033[93m"
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    GRAY = '\033[90m'


def message_send_handler():
    global sock
    print("{}{}{}".format(Color.GRAY, "-"*os.get_terminal_size().columns, Color.ENDC))
    while True:
        try:
            message = input()
            if re.match(r'^[!/][eq]$', message):
                print('Done!')
                sock.close()
                os.kill(os.getpid(), signal.SIGTERM)
            print('\033[1A' + '\033[K', end='')
            if message == '':
                print('\033[1A' + '\033[K', end='')
                print("{}{}{}".format(Color.GRAY, "-"*os.get_terminal_size().columns, Color.ENDC))
                continue
            message = message.encode()
            msg_size = len(message)
            try:
                now = int(datetime.datetime.now().timestamp())
            except ValueError:
                now = 0
            pkt = struct.pack('!LL{}s'.format(msg_size), msg_size, now, message)
            sock.send(pkt)
        except (socket.timeout, socket.error):
            print('Server error. Done!')
            sock.close()
            os.kill(os.getpid(), signal.SIGTERM)


def message_receive_handler():
    global sock
    headerformat = '!LLL'
    while True:
        try:
            request = sock.recv(struct.calcsize(headerformat))
            try:
                pktheader = struct.unpack(headerformat, request)
            except struct.error:
                print('{}Server error.{}'.format(Color.FAIL, Color.ENDC))
                os.kill(os.getpid(), signal.SIGTERM)
                sys.exit(0)
            usr_size, msg_size, now = pktheader
            request = sock.recv(usr_size + msg_size)
            pktdata = struct.unpack('{}s{}s'.format(usr_size, msg_size), request)
            print()
            print('\033[1A' + '\033[K', end='')
            print('\033[1A' + '\033[K', end='')
            print('\033[1A' + '\033[K', end='')
            print("{}[{}]{} {}{}:{} {}\n".format(Color.GRAY, datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), Color.ENDC,
                                                 Color.OKBLUE, pktdata[0].decode(), Color.ENDC, pktdata[1].decode()))
            print("{}{}{}".format(Color.GRAY, "-"*os.get_terminal_size().columns, Color.ENDC))
            sys.stdout.write(readline.get_line_buffer())
            sys.stdout.flush()
        except (socket.timeout, socket.error):
            print('{}Server error.{}'.format(Color.FAIL, Color.ENDC))
            sock.close()
            os.kill(os.getpid(), signal.SIGTERM)


def signal_handler(sig, frame):
    global sock
    print('\nDisconnected!')
    sock.close()
    os.kill(os.getpid(), signal.SIGTERM)


def main():
    global sock
    global username

    signal.signal(signal.SIGINT, signal_handler)

    ip_addr = "127.0.0.1"
    tcp_port = 5005

    for arg in sys.argv[1:(2 if all(a.isdigit() for a in sys.argv[1:]) else 3)]:
        if arg.isdigit():
            tcp_port = int(arg)
        else:
            ip_addr = arg

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip_addr, tcp_port))
    except socket.error:
        print('{}Cannot connect to server.{}'.format(Color.FAIL, Color.ENDC))
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit(0)

    username = input('Enter your username: ').encode()
    print('\033[1A' + '\033[K', end='')
    headerformat = '!L'

    # Send list of connected clients
    sock.send(struct.pack('!L{}s'.format(len(username)), len(username), username))

    request = sock.recv(struct.calcsize(headerformat))
    list_size = struct.unpack(headerformat, request)[0]
    list_of_clients = sock.recv(list_size).decode()

    print('{}Logged in as {}.'.format(Color.OKGREEN, username.decode()))
    print('Connected Clients: {}'.format(list_of_clients))
    print('Press Ctrl+C to exit...{}\n\n'.format(Color.ENDC))

    threading.Thread(target=message_send_handler).start()
    threading.Thread(target=message_receive_handler).start()


if __name__ == '__main__':
    main()
