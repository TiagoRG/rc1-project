import os
import re
import sys
import socket
import threading
import signal
import struct
import datetime


class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = "\033[93m"
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class LogMessage:
    INFO = "[INFO]   "
    ERROR = "[ERROR]  "
    WARNING = "[WARNING]"
    CONNECTION = "[CLIENT] "
    MESSAGE = "[MESSAGE]"


def handle_client_connection(client, address):
    global CLIENTS

    # Get username
    headerformat = '!L'
    request = client.recv(struct.calcsize(headerformat))
    username_size = struct.unpack(headerformat, request)[0]
    username = client.recv(username_size).decode()
    CLIENTS[client] = {"username": username, "order": 0}

    # Send list of connected clients
    list_of_clients = ', '.join([user["username"] for user in CLIENTS.values()]).encode()
    client.send(struct.pack('!L{}s'.format(len(list_of_clients)), len(list_of_clients), list_of_clients))

    print('{}[{}] {}{} Accepted connection from {} ({}:{})'.format(Color.OKGREEN, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                   LogMessage.CONNECTION, Color.ENDC, username, address[0], address[1]))

    message = '{}{}{} has joined the chat.'.format(Color.OKBLUE, username, Color.ENDC)
    pkt = struct.pack('!LLL{}s{}s'.format(len('\033[95mSERVER'.encode()), len(message.encode())),
                      len('\033[95mSERVER'.encode()), len(message.encode()), int(datetime.datetime.now().timestamp()), '\033[95mSERVER'.encode(), message.encode())
    for sock in CLIENTS.keys():
        sock.send(pkt)

    headerformat = '!LL'
    try:
        while True:
            request = client.recv(struct.calcsize(headerformat))
            try:
                pktheader = struct.unpack(headerformat, request)
            except struct.error:
                # print('{}[{}] {}{} Client {} error.'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC, address))
                break
            message_size, now = pktheader
            CLIENTS[client]["order"] += 1
            request = client.recv(message_size)
            pktdata = struct.unpack('{}s'.format(message_size), request)
            message = pktdata[0].decode()
            print('{}[{}] {}{} order: {}, message_size: {}, date: {} -> {}: {}'
                  .format(Color.HEADER, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.MESSAGE, Color.ENDC,
                      CLIENTS[client]["order"], message_size, datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), username, message))
            try:
                pkt = struct.pack('!LLL{}s{}s'.format(username_size, message_size), username_size, message_size, now, username.encode(), message.encode())
            except struct.error:
                # print('{}[{}] {}{} Client {} error.'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC, address))
                break
            for sock in CLIENTS.keys():
                sock.send(pkt)
    except (socket.timeout, socket.error):
        print('{}[{}] {}{} Client {} error.'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC, address))
    finally:
        client.close()
        CLIENTS.pop(client)
        print('{}[{}] {}{} Closed connection from {} ({}:{})'
              .format(Color.WARNING, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.CONNECTION, Color.ENDC, username, address[0], address[1]))

        message = '{}{}{} has left the chat.'.format(Color.OKBLUE, username, Color.ENDC)
        pkt = struct.pack('!LLL{}s{}s'.format(len('\033[95mSERVER'.encode()), len(message.encode())), len('\033[95mSERVER'.encode()), len(message.encode()), int(datetime.datetime.now().timestamp()), '\033[95mSERVER'.encode(), message.encode())
        for sock in CLIENTS.keys():
            sock.send(pkt)


def handle_connections():
    global server
    global CLIENTS

    while True:
        client, address = server.accept()
        client_handler = threading.Thread(target=handle_client_connection, args=(client, address), daemon=True)
        client_handler.start()


def handle_commands():
    global server
    global CLIENTS
    while True:
        command = input()
        print("\033[A                                                 \033[A")
        if re.match(r'^[eq]|exit|quit$', command):
            print('{}[{}] {}{} Shutting down server...'.format(Color.WARNING, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.INFO, Color.ENDC))
            server.close()
            os.kill(os.getpid(), signal.SIGTERM)
        elif re.match(r'^[lc]|list|clients$', command):
            print('Connected clients:\n')
            for sock in CLIENTS.keys():
                print('Username: {}\nAddress: {}:{}\nOrders: {}\n'.format(CLIENTS[sock]["username"], sock.getpeername()[0], sock.getpeername()[1], CLIENTS[sock]["order"]))
        else:
            print('{}[{}] {}{} Unknown command.'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC))


def signal_handler(sig, frame):
    global server
    print('\r{}[{}] {}{} Shutting down server...'.format(Color.WARNING, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.INFO, Color.ENDC))
    server.close()
    os.kill(os.getpid(), signal.SIGTERM)


def main():
    global server
    global CLIENTS
    CLIENTS = {}

    ip_addr = "0.0.0.0"
    try:
        tcp_port = int(sys.argv[1]) if len(sys.argv) > 1 else 5005
    except ValueError:
        print('{}[{}] {}{} Invalid port number.'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC))
        sys.exit(0)

    print('{}[{}] {}{} Starting server on {}:{}'.format(Color.OKBLUE, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.INFO, Color.ENDC, ip_addr, tcp_port))
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip_addr, tcp_port))
        server.listen(5)  # max backlog of connections
    except socket.error as e:
        print('{}[{}] {}{} Error initializing server: {}'.format(Color.FAIL, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.ERROR, Color.ENDC, e))
        sys.exit(0)

    print('{}[{}] {}{} Listening on {}:{}'.format(Color.OKBLUE, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.INFO, Color.ENDC, ip_addr, tcp_port))
    signal.signal(signal.SIGINT, signal_handler)
    print('{}[{}] {}{} Press Ctrl+C to exit...'.format(Color.OKBLUE, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogMessage.INFO, Color.ENDC))

    threading.Thread(target=handle_commands).start()
    threading.Thread(target=handle_connections).start()


if __name__ == '__main__':
    main()
