import os
import socket
import threading
import signal
import sys
import struct


SOCKS_LIST = []


def signal_handler(sig, frame):
    print('\nDone!')
    server.close()
    os.kill(os.getpid(), signal.SIGTERM)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

##


def handle_client_connection(client_socket, address):
    global SOCKS_LIST
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    headerformat = '!BLLL'
    try:
        while True:
            request = client_socket.recv(struct.calcsize(headerformat))
            try:
                pktheader = struct.unpack(headerformat, request)
            except struct.error:
                print('Client {} error. Done!'.format(address))
                break
            version, size, order, now = pktheader
            request = client_socket.recv(size)
            pktdata = struct.unpack('{}s'.format(size), request)
            data = f"{address[0]}:{address[1]}: {pktdata[0].decode()}"
            size = len(data)
            print('Received ver: {}, size: {}, order: {}, date: {} -> {}'.format(version,
                  size, order, now, data))
            pkt = struct.pack('!BLLL{}s'.format(
                size), version, size, order, now, data.encode())
            # client_socket.send(pkt)
            for sock in SOCKS_LIST:
                sock.send(pkt)
    except (socket.timeout, socket.error):
        print('Client {} error. Done!'.format(address))
    finally:
        client_socket.close()
        SOCKS_LIST.remove(client_socket)
        print(SOCKS_LIST)
        print('Closed connection from {}:{}'.format(address[0], address[1]))


ip_addr = "0.0.0.0"
tcp_port = 5005


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip_addr, tcp_port))
server.listen(5)  # max backlog of connections

print('Listening on {}:{}'.format(ip_addr, tcp_port))

while True:
    client_sock, address = server.accept()
    SOCKS_LIST.append(client_sock)
    print(SOCKS_LIST)
    client_handler = threading.Thread(
        target=handle_client_connection, args=(client_sock, address), daemon=True)
    client_handler.start()
