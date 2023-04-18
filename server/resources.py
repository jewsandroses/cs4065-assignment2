import json

# table that holds address:username pairs
user_addr_table = {}

# class that handles most logic for server
class Message_Board():
    boards = []
    user_table = {} # username: send_data_user()
    def __init__(self,id,name):
        self.name = name
        self.id = id
        self.users = []
        self._messages = []
        if self in Message_Board.boards:
            raise ValueError("Board already exists in board list")
        Message_Board.boards.append(self)
    def __eq__(self,other):
        return isinstance(other,Message_Board) and (self.id == other.id or self.name == other.name)
    @property
    def list(self):
        return [self.id,self.name]
    def __repr__(self):
        return str(self.list)
    # adds a user to this board
    def add_connection(self,username):
        if username in self.users:
            raise ValueError("User already connected to board")
        else:
            self.users.append(username)
            self.update_users()
    # removes a user from this board
    def disconnect(self,username):
        if username in self.users:
            self.users.remove(username)
            Message_Board.user_table[username]()
            self.update_users()
        else:
            raise ValueError("Specified user not connected to board")
    # adds a message to this board
    def add_message(self,message,user):
        if message not in self._messages:
            self._messages[1] = self._messages [0]
            self._messages[0] = message
            Message_Board.user_table[user]({"MessageType":"Message","Success":True})
            self.update_users()
    # updates all users connected to this board when necessary
    def update_users(self):
        um = {"MessageType":"Update",
                "Messages": self.messages,
                "ConnectedUsers": self.users,
                "MessageBoard": self.id}
        for user in self.users:
            Message_Board.user_table[user](um)
    # checks if a specific user is connected to any board in cls.boards
    @classmethod
    def user_connected(cls,user):
        for board in cls.boards:
            if user in board.users:
                return True
        return False
    # adds a username:user_function pair to the cls.user_table 
    @classmethod
    def add_user_table(cls,user,function):
        cls.user_table.update({user:function})
    # remove a username:user_function pair from the cls.user_table if that user is not connected to any board
    @classmethod
    def remove_user_table(cls,user):
        if cls.user_connected(user):
            return    
        del cls.user_table[user]
    # returns the get groups message response
    @classmethod
    def get_groups_message(cls):
        return {"MessageType":"Groups",
                "Groups":[board.list for board in cls.boards]}
    # acts as a table that is accessible via the class, allows the boards to be accessed via id or name
    @classmethod
    @property
    def boards_dict(cls):
        b = {board.id:board for board in cls.boards}
        b.update({board.name:board for board in cls.boards})
        return b

# initializes all 6 normal message boards
Message_Board.boards = [
    Message_Board(0,"public"),
    Message_Board(1,"Private Room 1"),
    Message_Board(2,"Private Room 2"),
    Message_Board(3,"Private Room 3"),
    Message_Board(4,"VIP Room"),
    Message_Board(5,"VIP Room 2")]

# adds a user to a board and to the Message_Board user function table
def add_user_connection(user,userfunc,board):
    b = Message_Board.boards_dict[board]
    Message_Board.add_user_table(user,userfunc)
    b.add_connection(user)
    userfunc({"MessageType":"Connection",
              "Success":True,
              "MessageBoard":b.list})

# removes a user from a board and from the Message_Board user function table provided they are no longer in any boards
def end_user_connection(user,userfunc,board):
    b = Message_Board.boards_dict[board]
    b.disconnect()
    Message_Board.remove_user_table(user)
    userfunc({"MessageType":"Disconnect",
              "Success":True,
              "MessageBoard":board})

# removes a user from all boards and from the Message_Board user function table
def end_user_connection_all(user,userfunc):
    for board in Message_Board.boards:
        if user in board.users:
            board.disconnect(user)
    Message_Board.remove_user_table(user)
    userfunc({"MessageType":"Disconnect",
              "Success":True,
              "MessageBoard":None})

# handles logic for determining if a user can send a message in a specific board
def handle_user_message(username,userfunc,board,content):
    b = Message_Board.boards_dict[board]
    if username not in b.users:
        return userfunc({"MessageType":"Message","Success":False})
    b.add_message(content,username)

# handles logic for determining what response the server should have for a given client message
def handle_client_tcp_message(data,userfunc):
    {   "Connection":   lambda x: add_user_connection(x["Username"],userfunc,x["MessageBoard"]),
        "Message":      lambda x: handle_user_message(x["Username"],userfunc,x["MessageBoard"],x["Content"]),
        "Disconnect":   lambda x: end_user_connection(x["Username"],userfunc,x["MessageBoard"]) if x["MessageBoard"] else end_user_connection_all(x["Username"],userfunc),
        "Groups":       lambda x: userfunc(Message_Board.get_groups_message())
    }[data["MessageType"]](data)