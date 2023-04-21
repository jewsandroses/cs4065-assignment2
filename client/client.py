import socket
import json
from time import sleep
import threading
from pprint import pprint


class Client:

    def __init__(self, user, host, port):
        self.username = user
        self.connection = socket.create_connection((host, port))
        self.group_info = dict()
        self.aval_groups = list()

    def connect(self, message_board=0):
        mess = {
            "MessageType": "Connection",
            "Username": self.username,
            "MessageBoard": message_board
        }
        self.connection.send(bytes(json.dumps(mess), 'utf-8'))

    def message(self, content, message_board=0):
        mess = {
            "MessageType": "Message",
            "Username": self.username,
            "MessageBoard": message_board,
            "Content": content
        }
        self.connection.send(bytes(json.dumps(mess), 'utf-8'))

    def disconnect(self, message_board=0):
        mess = {
            "MessageType": "Disconnect",
            "Username": self.username,
            "MessageBoard": message_board
        }
        self.connection.send(bytes(json.dumps(mess), 'utf-8'))
        self.group_info.pop(message_board)

    def groups(self):
        mess = {
            "MessageType": "Groups",
            "Username": self.username
        }
        self.connection.send(bytes(json.dumps(mess), 'utf-8'))

    def display_users(self, message_board=0):
        print(f"Displaying users from group {message_board}")
        for user in self.group_info[message_board]["Users"]:
            print(user)

    def start_receive_loop(self):

        def loop():
            prev_bytes = bytes()
            while True:
                try:
                    curr_bytes = prev_bytes + self.connection.recv(4096)
                    next_message = curr_bytes.split(sep=b'\n')[0]
                    prev_bytes = curr_bytes.removeprefix(next_message + b'\n')
                    if next_message:
                        print(prev_bytes)
                        print(next_message)
                        rec = json.loads(next_message.decode('utf-8'))
                    else:
                        continue
                except json.JSONDecodeError as e:
                    print(f"Encountered {type(e)}: {e}")
                    print("Connection to server unexpectedly terminated.")
                    rec = None
                    return

                if rec["MessageType"] == "Update":
                    self.group_info[rec["MessageBoard"]] = {
                        "Users": rec["ConnectedUsers"],
                        "Messages": list(set(rec["Messages"] + self.group_info.get(rec["MessageBoard"], {"Messages": list()})["Messages"])),
                    }
                    pprint(self.group_info)

                if rec["MessageType"] == "Groups":
                    self.aval_groups = rec["Groups"]

        loop_th = threading.Thread(target=loop, name="receive_thread")
        loop_th.daemon = True
        loop_th.start()

    def display_messages(self, message_group=0):
        print(f"Messages from group #{message_group}:")
        for message in self.group_info[message_group]["Messages"]:
            print(message)

    def print_status(self):
        print("=== Client Status ===")
        print("Connected Groups:")
        for group in self.group_info:
            print(group)
            print("\tConnected Users:")
            for user in self.group_info[group]["Users"]:
                print("\t\t" + user)
            print("\tMessages:")
            for message in self.group_info[group]["Messages"]:
                print("\t\t" + message)


def main():

    host = input("Host address? Leave blank for default.")
    port = input("Server port?")
    username = input("Username?")

    print("Connecting to server...")
    cli = Client(username, host, port)
    cli.start_receive_loop()

    while True:

        menu = ("Enter one of the following commands:\n"
                "ClientStatus\n"
                "Connect\n"
                "Message\n"
                "DisplayMessages\n"
                "Users\n"
                "Disconnect\n"
                "Groups\n"
                "ConnectGroup\n"
                "DisconnectGroup\n"
                "UsersGroup\n"
                "MessageGroup\n"
                "DisplayMessagesGroup\n"
                "Exit")

        print(menu)

        command = input(">>>")

        command = command.split()

        command_type = command[0]

        if command_type == "Connect":
            cli.connect()
            sleep(1)
            cli.print_status()

        elif command_type == "ClientStatus":
            cli.print_status()

        elif command_type == "Message":
            message = input("Type your message:")
            cli.message(message)
            sleep(1)

        elif command_type == "DisplayMessages":
            cli.display_messages()

        elif command_type == "Groups":
            cli.groups()
            sleep(1)
            print(cli.aval_groups)

        elif command_type == "Users":
            cli.display_users()

        elif command_type == "Disconnect":
            cli.disconnect()

        elif command_type == "ConnectGroup":
            group = int(input("Enter the group ID: "))
            cli.connect(group)
            cli.print_status()

        elif command_type == "DisplayMessagesGroup":
            group = int(input("Enter group ID: "))
            cli.display_messages(group)

        elif command_type == "DisconnectGroup":
            group = int(input("Enter group ID: "))
            cli.disconnect(group)

        elif command_type == "UsersGroup":
            cli.display_users(group)

        elif command_type == "MessageGroup":
            group = int(input("Enter group ID: "))
            message = input("Enter your message: ")
            cli.message(message, group)
            sleep(1)
            cli.print_status()

        elif command_type == "Exit":
            cli.connection.close()
            exit()
        else:
            print("Invalid Command")


if __name__ == "__main__":
    main()
