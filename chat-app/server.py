import os
import socket
import threading
import signal
import sys
import struct
import datetime


def handle_client_connection(client_socket, address):
    global CLIENTS
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    headerformat = '!LLL'
    try:
        while True:
            request = client_socket.recv(struct.calcsize(headerformat))
            try:
                pktheader = struct.unpack(headerformat, request)
            except struct.error:
                print('Client {} error. Done!'.format(address))
                break
            username_size, message_size, now = pktheader
            CLIENTS[client_socket]["order"] += 1
            request = client_socket.recv(username_size + message_size)
            pktdata = struct.unpack('{}s{}s'.format(
                username_size, message_size), request)
            username = pktdata[0].decode()
            message = pktdata[1].decode()
            print('Received: username_size: {}, message_size: {}, order: {}, date: {} -> {}: {}'
                  .format(username_size, message_size,
                          CLIENTS[client_socket]["order"],
                          datetime.datetime.fromtimestamp(
                              now).strftime('%Y-%m-%d %H:%M:%S'),
                          username, message))
            try:
                pkt = struct.pack(
                    '!LLL{}s{}s'.format(username_size, message_size),
                    username_size, message_size, now,
                    username.encode(), message.encode())
            except struct.error:
                print('Client {} error. Done!'.format(address))
                break
            for sock in CLIENTS.keys():
                sock.send(pkt)
    except (socket.timeout, socket.error):
        print('Client {} error. Done!'.format(address))
    finally:
        client_socket.close()
        CLIENTS.pop(client_socket)
        print(CLIENTS)
        print('Closed connection from {}:{}'.format(address[0], address[1]))


def handle_connections():
    global server
    global CLIENTS

    while True:
        client_sock, address = server.accept()

        # Get username
        headerformat = '!L'
        request = client_sock.recv(struct.calcsize(headerformat))
        username_size = struct.unpack(headerformat, request)[0]
        username = client_sock.recv(username_size).decode()
        print('Received username: {}'.format(username))
        CLIENTS[client_sock] = {"username": username, "order": 0}

        # Send list of connected clients
        list_of_clients = ', '.join([user["username"]
                                     for user in CLIENTS.values()]).encode()
        client_sock.send(struct.pack('!L{}s'.format(
            len(list_of_clients)), len(list_of_clients), list_of_clients))

        print(CLIENTS)
        client_handler = threading.Thread(
            target=handle_client_connection, args=(client_sock, address),
            daemon=True)
        client_handler.start()


def handle_commands():
    global server
    global CLIENTS
    while True:
        command = input()
        if command == 'exit':
            server.close()
            os.kill(os.getpid(), signal.SIGTERM)
        elif command == 'list':
            print('Connected clients:\n')
            for sock in CLIENTS.keys():
                print('Client username: {}\n    {}\n    {}\n'.format(
                    CLIENTS[sock]["username"],
                    sock.getpeername(),
                    CLIENTS[sock]["order"]))
        else:
            print('Unknown command.')


def signal_handler(sig, frame):
    global server
    print('\nDone!')
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
        print('Invalid port number.')
        sys.exit(0)

    print('Starting server on {}:{}'.format(ip_addr, tcp_port))
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip_addr, tcp_port))
        server.listen(5)  # max backlog of connections
    except socket.error as e:
        print('Error initializing server: {}'.format(e))
        sys.exit(0)

    print('Listening on {}:{}'.format(ip_addr, tcp_port))
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit...')

    threading.Thread(target=handle_connections).start()
    threading.Thread(target=handle_commands).start()


if __name__ == '__main__':
    main()
