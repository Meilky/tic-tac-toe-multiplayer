import socket
from utils import parseCmd
import time
import random
import threading

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

class Client:
    input: tuple[str, str] | None
    def __init__(self, socket: socket.socket, bufSize: int):
        socket.setblocking(False)

        self.socket = socket
        self.bufSize = bufSize
        self.state = "connected"
        self.input = None

    def update(self):
        try:
            data = self.socket.recv(self.bufSize)

            if not data:
                self.close()
                return

            try:
                self.input = parseCmd(data.decode("ascii"))

                if not self.input:
                    return

                if self.input[0] == "EX":
                    self.close()
                    return
            except: 
                return
        except socket.error as e:
            if not e.errno == socket.EWOULDBLOCK:
                self.close()

    def send(self, cmd, arg):
        self.socket.send((cmd+":"+ arg).encode("ascii"))

    def getInput(self) -> tuple[str,str] | None:
        return self.input

    def close(self):
        self.state = "disconnected";
        self.socket.close()
        self.input = None

class Player:
    def __init__(self, client: Client):
        self.client = client
        self.state = "init"
        self.name = ""
        self.nbWin = 0
        self.nbLost = 0

    def update(self):
        self.client.update()

        if self.client.state == "disconnected":
            self.handleExit()
            return

        cin = self.client.getInput()

        if not cin:
            return

        (cmd, arg) = cin

        match self.state:
            case "init":
                self.handleInit(cmd, arg)
            case "lobby":
                self.handleLoby(cmd, arg)

    def handleInit(self, cmd, arg):
        if cmd == "PL":
            self.name = arg
            self.state = "lobby"

    def handleLoby(self, cmd, arg):
        if cmd == "EN":
            self.state = "waiting"

    def handleExit(self):
        self.state = "quit"

    def send(self, cmd, arg):
        self.client.send(cmd, arg)

    def getInput(self):
        return self.client.getInput()

class Game:
    def __init__(self, player1: Player, player2: Player):
        self.state = "init"
        self.player1 = player1
        self.player2 = player2
        self.turn = 0
        self.turnChanged = False
        self.board = ["","","","","","","","",""]

        self.update()

    def update(self):
        match self.state:
            case "init":
                self.handleInit()
            case "play":
                self.handlePlay()

    def handleInit(self):
        self.state = "play"
        self.player1.send("AK", self.player2.name)
        self.player2.send("AK", self.player1.name)

        self.player1.state = "play"
        self.player2.state = "play"

        self.turnChanged = True
        if random.random() >= 0.5:
            self.turn = 1 
        else:
            self.turn = 2 

    def handlePlay(self):
        if self.player1.state == "quit":
            self.handlePlayerWin(self.player2)
            self.state = "done"
            return

        if self.player2.state == "quit":
            self.handlePlayerWin(self.player1)
            self.state = "done"
            return

        if self.turnChanged:
            self.turnChanged = False

            if self.turn == 1:
                self.player1.send("TU", self.player1.name + "," + ",".join(self.board))
                self.player2.send("TU", self.player1.name + "," + ",".join(self.board))
            else:
                self.player1.send("TU", self.player2.name + "," + ",".join(self.board))
                self.player2.send("TU", self.player2.name + "," + ",".join(self.board))

        self.handlePlayerInput(self.player1, self.turn == 1)
        self.handlePlayerInput(self.player2, self.turn == 2)

        self.checkEnd()

    def checkEnd(self):
        if self.checkWin(self.player1.name):
            self.handlePlayerWin(self.player1)
            self.handlePlayerLost(self.player2)
            self.state = "done"
        elif self.checkWin(self.player2.name):
            self.handlePlayerWin(self.player2)
            self.handlePlayerLost(self.player1)
            self.state = "done"
        elif self.checkTie():
            self.handlePlayerTie(self.player1)
            self.handlePlayerTie(self.player2)
            self.state = "done"

    def checkWin(self, name):
        for i in range(0, 7, 3):
            if(self.board[i] == name and self.board[i+1] == name and self.board[i+2] == name):
                return True
        for i in range(0, 3):
            if(self.board[i] == name and self.board[i+3] == name and self.board[i+6] == name):
                return True
        if(self.board[0] == name and self.board[4] == name and self.board[8] == name):
            return True
        if(self.board[2] == name and self.board[4] == name and self.board[6] == name):
            return True
        return False
    
    def checkTie(self):
        for x in self.board:
            if(x == ""):
                return False
        return True


    def handlePlayerInput(self, player: Player, isTurn: bool):
        pin = player.getInput()

        if not pin:
            return
        
        (cmd, arg) = pin

        if isTurn and cmd == "MV":
            self.handlePlayerMove(player, arg)

    def handlePlayerMove(self, player: Player, move):
        if not move.isdigit():
            self.handlePlayerMoveError(player)
            return

        idx = int(move)

        if idx < 0 or idx > 8:
            self.handlePlayerMoveError(player)
            return
        
        if not self.board[idx] == "":
            self.handlePlayerMoveError(player)
            return

        self.board[idx] = player.name
        self.turnChanged = True

        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1

    def handlePlayerMoveError(self, player: Player):
        player.send("ER", "Can't move to this place")

    def handlePlayerWin(self, player: Player):
        player.nbWin += 1;
        player.state = "lobby"
        player.send("GE", "win")

    def handlePlayerTie(self, player: Player):
        player.state = "lobby"
        player.send("GE", "tie")

    def handlePlayerLost(self, player: Player):
        player.nbLost += 1;
        player.state = "lobby"
        player.send("GE", "lost")


class Engine:
    def __init__(self):
        self.players = []
        self.games = []
        self.startTime = time.time()

    def addPlayer(self, player: Player):
        self.players.append(player)

    def start(self):
        while True:
            self.tick()

    def tick(self):
        deadPlayer = []

        nextPlayer = None
        for player in self.players:
            player.update()

            if player.state == "waiting":
                if nextPlayer:
                    self.games.append(Game(nextPlayer, player))
                    nextPlayer = None
                else:
                    nextPlayer = player


            if player.state == "quit":
                deadPlayer.append(player)
        
        for player in deadPlayer:
            self.players.remove(player)

        deadGame = []

        for game in self.games:
            game.update()

            if game.state == "done":
                deadGame.append(game)
        
        for game in deadGame:
            self.games.remove(game)

        if time.time() - self.startTime >= 5:
            self.printScoreBoard()
            self.startTime = time.time()

        for player in self.players:
            player.client.input = None

    def printScoreBoard(self):
        print("----------")
        print("Score board:")
        print("----------")

        for player in self.players:
            if player.state == "init":
                continue

            print("Name:",player.name,"Win:",player.nbWin,"Lost:",player.nbLost)


def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(5)

    print(f"Server listening on {HOST}:{PORT}")
    
    engine = Engine()

    serverThread = threading.Thread(target=engine.start)
    serverThread.start()

    try:
        while True:
            clientSocket, address = serverSocket.accept()

            engine.addPlayer(Player(Client(clientSocket, BUFFER_SIZE)))
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()
