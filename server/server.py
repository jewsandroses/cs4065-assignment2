import socket, json, asyncio
from resources import *

# table holding address:async_function pairs 
connections = {}

# function listening socket runs
async def wait_for_connection(s):
    # Loop through waiting for TCP connections
    while True:
        # wait for connection and get socket (conn) and address of connection
        conn, addr = s.accept()
        # initializes a function that will be called when sending data to the connected socket
        def connfunc(data):
            conn.send(bytes(json.dumps(data), 'UTF-8'))
        # adds 
        connections.update({addr:handle_connection(conn,addr,connfunc)})

# function each connected socket runs
async def handle_connection(conn,addr,func):
    # Loop through waiting for client messages
    while True:
        # Wait for message from client and convert raw data to python dictionary
        data = json.loads(conn.recv(1024).decode("utf-8"))

        # if no content was sent, dissconnect user and close tcp socket
        if not data:
            data = {"MessageType":"Disconnect","Username":user_addr_table[addr],"MessageBoard":None}
            del user_addr_table[addr]
            del connections[addr]
            break

        # if user is disconnecting from all groups, but not closing the socket 
        if data["MessageType"] == "Disconnect" and not data["MessageBoard"]:
            del user_addr_table[addr]

        # if user is sending a message that contains their username, add it to the user_addr_table for later use
        if data["MessageType"] != "Groups":
            user_addr_table[addr] = data["Username"]

        # send data to resource handler to handle message logic
        handle_client_tcp_message(data,func)
        

port = int(input("Port?\n"))
while(port < 1023 or port > 65536):
    port = int(input("Port? (1024-65536)\n"))


s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", port))
print(f"Listening on port {port}...")
s.listen()
asyncio.run(wait_for_connection(s))