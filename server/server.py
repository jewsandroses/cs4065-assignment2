


class Message_Board():
    boards = []
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
    def add_connection(self,username):
        if username in self.users:
            raise ValueError("User already connected to board")
        else:
            self.users.append(username)
            #TODO: Send all connected users update message
    def disconnect(self,username):
        if username in self.users:
            self.users.remove(username)
            #TODO: Send all connected users update message
        else:
            raise ValueError("Specified user not connected to board")
    def add_message(self,message):
        if message not in self._messages:
            self._messages[1] = self._messages [0]
            self._messages[0] = message
    def get_messages(self):
        return self._messages
Message_Board(0,"public")
Message_Board(1,"Private Room 1")
Message_Board(2,"Private Room 2")
Message_Board(3,"Private Room 3")
Message_Board(4,"VIP Room")
Message_Board(5,"VIP Room 2")
