import socket
import json
from threading import Thread
from resources import *
import functools

connections = {}
user_table = {}


def wait_for_connection(s):
    while True:
        conn, addr = s.accept()

        print(addr)

        def connfunc(data, addr):
            connections[addr].send(bytes(json.dumps(data) + '\n', 'UTF-8'))

        connections.update({addr: conn})

        return_func = functools.partial(connfunc, addr=addr)

        try:
            conn_th = Thread(target=handle_connection,
                             name=f"{addr[0]}:{addr[1]}", daemon=True,
                             args=(conn, addr, return_func))
            conn_th.start()
        except BaseException as e:
            print(f"Encountered {type(e)}: {e}")


def handle_connection(conn, addr, func):
    while True:
        try:
            raw_bytes = conn.recv(1024).decode("utf-8")
            print(raw_bytes)
            data = json.loads(raw_bytes)
            user_table.update({addr: data["Username"]})
        except BaseException as e:
            print(f"Encountered {type(e)}: {e}")
            data = None
        if not data:
            data = {"MessageType": "Disconnect",
                    "Username": user_table[addr], "MessageBoard": None}
            handle_client_tcp_message(data, func)
            break

        handle_client_tcp_message(data, func)


port = int(input("Port?\n"))
while (port < 1023 or port > 65536):
    port = int(input("Port? (1024-65536)\n"))

connections = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", port))
print(f"Listening on port {port}...")
s.listen()
wait_for_connection(s)
