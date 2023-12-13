import os
import sys
import socket
import threading
import struct
import signal
import datetime
import readline


def message_send_handler():
    global username
    order = 0
    print("\n----------------------------------------")
    while True:
        try:
            message = input()
            print("\033[A                                                 \033[A")
            if message == '':
                print("\033[A                                                 \033[A")
                print("----------------------------------------")
                continue
            message = f"{username}: {message}".encode()
            version = 1
            order += 1
            size = len(message)
            try:
                now = int(datetime.datetime.now().timestamp())
            except ValueError:
                now = 0
            pkt = struct.pack('!BLLL{}s'.format(
                size), version, size, order, now, message)
            sock.send(pkt)
        except (socket.timeout, socket.error):
            print('Server error. Done!')
            os.kill(os.getpid(), signal.SIGTERM)
            sys.exit(0)


def message_receive_handler():
    headerformat = '!BLLL'
    while True:
        try:
            request = sock.recv(struct.calcsize(headerformat))
            try:
                pktheader = struct.unpack(headerformat, request)
            except struct.error:
                print('Server error. Done!')
                os.kill(os.getpid(), signal.SIGTERM)
                sys.exit(0)
            # version, size, order, now = pktheader
            size, now = pktheader[1], pktheader[3]
            request = sock.recv(size)
            pktdata = struct.unpack('{}s'.format(size), request)
            print()
            print("\033[A                                                 \033[A")
            print("\033[A                                                 \033[A")
            print("\033[A                                                 \033[A")
            print("[{}] {}\n"
                  .format(
                      datetime.datetime.fromtimestamp(
                          now).strftime('%Y-%m-%d %H:%M:%S'),
                      pktdata[0].decode()))
            print("----------------------------------------")
            sys.stdout.write(readline.get_line_buffer())
            sys.stdout.flush()
            # print("\rReceived ver: {}, size: {}, order: {}, date: {} -> {}\n\nMessage > "
            #       .format(version, size, order, now, pktdata[0].decode()), end='')
        except (socket.timeout, socket.error):
            print('Server error. Done!')
            os.kill(os.getpid(), signal.SIGTERM)


send_handler = threading.Thread(target=message_send_handler)
receive_handler = threading.Thread(target=message_receive_handler)


def signal_handler(sig, frame):
    print('\nDone!')
    os.kill(os.getpid(), signal.SIGTERM)


signal.signal(signal.SIGINT, signal_handler)
username = input('Enter your username: ')
print('Logged in as {}.'.format(username))
print('Press Ctrl+C to exit...\n\n')

ip_addr = "127.0.0.1"
tcp_port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((ip_addr, tcp_port))

send_handler.start()
receive_handler.start()
