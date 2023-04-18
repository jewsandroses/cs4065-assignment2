import socket, json, asyncio
from resources import *

connections = {}
user_table = {}

async def wait_for_connection(s):
    while True:
        conn, addr = s.accept()
        def connfunc(data):
            conn.send(bytes(json.dumps(data), 'UTF-8'))
        connections.update({addr:handle_connection(conn,addr,connfunc)})

async def handle_connection(conn,addr,func):
    while True:
        data = json.loads(conn.recv(1024).decode("utf-8"))
        if not data: data = {"MessageType":"Disconnect","Username":user_table[addr],"MessageBoard":None}
        handle_client_tcp_message(data,func)
        

port = int(input("Port?\n"))
while(port < 1023 or port > 65536):
    port = int(input("Port? (1024-65536)\n"))

connections = {}

s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", port))
print(f"Listening on port {port}...")
s.listen()
asyncio.run(wait_for_connection(s))