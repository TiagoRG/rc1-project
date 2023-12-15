import os
import sys
import re
import socket
import threading
import struct
import signal
import datetime
import readline


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
    print("{}----------------------------------------{}".format(Color.GRAY, Color.ENDC))
    while True:
        try:
            message = input()
            if re.match(r'^[!/][eq]$', message):
                print('Done!')
                sock.close()
                os.kill(os.getpid(), signal.SIGTERM)
            print("\033[A                                                           \033[A")
            if message == '':
                print("\033[A                                                           \033[A")
                print("{}----------------------------------------".format(Color.GRAY, Color.ENDC))
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
            print("\033[A                                                           \033[A")
            print("\033[A                                                           \033[A")
            print("\033[A                                                           \033[A")
            print("{}[{}]{} {}{}:{} {}\n".format(Color.GRAY, datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), Color.ENDC,
                                                 Color.OKBLUE, pktdata[0].decode(), Color.ENDC, pktdata[1].decode()))
            print("{}----------------------------------------{}".format(Color.GRAY, Color.ENDC))
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

    ip_addr = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    tcp_port = int(sys.argv[2]) if len(sys.argv) > 2 else 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip_addr, tcp_port))
    except socket.error:
        print('{}Cannot connect to server.{}'.format(Color.FAIL, Color.ENDC))
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit(0)

    username = input('{}Enter your username:{} '.format(Color.GRAY, Color.ENDC)).encode()
    headerformat = '!L'

    # Send list of connected clients
    sock.send(struct.pack('!L{}s'.format(len(username)), len(username), username))

    request = sock.recv(struct.calcsize(headerformat))
    list_size = struct.unpack(headerformat, request)[0]
    list_of_clients = sock.recv(list_size).decode()

    print('{}Connected Clients: {}'.format(Color.OKGREEN, list_of_clients))
    print('Logged in as {}.'.format(username.decode()))
    print('Press Ctrl+C to exit...{}\n\n'.format(Color.ENDC))

    threading.Thread(target=message_send_handler).start()
    threading.Thread(target=message_receive_handler).start()


if __name__ == '__main__':
    main()
