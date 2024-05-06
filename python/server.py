import socket
import uuid

from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

class Client:
    def __init__(self, socket: socket.socket, bufSize: int):
        socket.setblocking(False)
        self.state = "connected"
        self.socket = socket
        self.bufSize = bufSize

        self.inputs = []
        self.outputs = []

    def update(self):
        try:
            data = self.socket.recv(self.bufSize)

            if not data:
                self.close()
                return

            try:
                (cmd, arg) = parseCmd(data.decode("ascii"))

                if cmd == "EX":
                    self.close()
                    return;

                self.inputs.append((cmd, arg))
            except: 
                return
        except socket.error as e:
            if not e.errno == socket.EWOULDBLOCK:
                self.close()
                return

        for (cmd, arg) in self.outputs:
            self.socket.send((cmd + ":" + arg).encode("ascii"))

        self.outputs.clear()

    def close(self):
        self.state = "disconnected";
        self.socket.close()
        self.outputs.clear()
        self.inputs.clear()


class Player:
    def __init__(self, client: Client):
        self.client = client
        self.state = "init"
        self.name = ""
        self.win = 0
        self.lost = 0

        self.inputs = []
        self.outputs = []

    def update(self):
        self.client.update()

        if self.client.state == "disconnected":
            self.quit();
            return

    def quit(self):
        self.state = "quit"
        self.inputs.clear()
        self.outputs.clear()


    def send(self, msg: str):
        if self.state == 0:
            return

        self.socket.send(msg.encode("ascii"))

class Game:
    def __init__(self):
        self.state = "init"

class Engine:
    clients: dict[int, Client]
    players: dict[int, Player]
    games: dict[int, Game]

    def __init__(self):
        self.clients = {}
        self.clientNextId = 0

        self.players = {}
        self.playerNextId = 0

        self.games = {}
        self.gameNextId = 0

    def addClient(self, client: Client):
        self.clients[self.clientNextId] = client
        self.clientNextId += 1

    def tick(self):
        for id, client in self.clients.items():
            print(id)


def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    serverSocket.bind((HOST, PORT))
    
    serverSocket.listen(5)

    print(f"Server listening on {HOST}:{PORT}")
    
    try:
        while True:
            clientSocket, address = serverSocket.accept()

            players.append(Player(clientSocket))
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()
