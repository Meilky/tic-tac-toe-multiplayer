import socket
import threading

from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

# state 0 = disconnected
# state 1 = just connected
# state 2 = waiting
# state 3 = in game
# state 4 = game done
class Player:
    def __init__(self, socket: socket.socket):
        self.socket = socket
        self.isConnected = True
        self.name = ""
        self.win = 0
        self.lost = 0
        self.rageQuit = 0

    def recv(self):
        try:
            data = self.socket.recv(BUFFER_SIZE)

            if not data:
                self.state = 0;
                self.socket.close()
                return None

            try:
                return parseCmd(data.decode("ascii"))
            except: 
                return None
        except socket.error as e:
            if not e.errno == socket.EWOULDBLOCK:
                self.state = 0
                self.socket.close()
                
        return None

    def send(self, msg: str):
        if self.state == 0:
            return

        self.socket.send(msg.encode("ascii"))

# state 0 = just created
# state 1 = player 1 to play
# state 2 = player 2 to play
# state 3 = game done tie
# state 5 = game done player 1 win
# state 6 = game done player 2 win
class Game:
    def __init__(self, player1: Player, player2: Player):
        self.board = ["","","","","","","","",""]
        self.state = 0
        self.player1 = player1
        self.player2 = player2

def handlePlayers(games: list[Game], players: list[Player]):
    disconnected = [];

    nextPlayerWaiting = None
    for player in players:
        if player.state == 0:
            disconnected.append(player)
            continue

        if player.state == 2:
            if not nextPlayerWaiting:
                nextPlayerWaiting = player
                continue

            games.append(Game(nextPlayerWaiting, player))
            nextPlayerWaiting = None
            continue

        result = player.recv()

        if not result:
            continue;

        (cmd, arg) = result

        if player.state == 1:
            if not cmd == "PL":
                player.send("ER:You need to send your name first")
                break

            if not len(arg) > 0:
                player.send("ER:You name need to be more than one character")
                break

            sameName = False
            for player2 in players:
                if player2.state == 1:
                    continue
                if player2.name == arg:
                    sameName = True
                    break

            if sameName:
                player.send("ER:A player already have this name")
                continue

            player.name = arg
            player.state = 2
            continue

        if cmd == "RP":
            player.state = 2

    for player in disconnected:
        players.remove(player)

def handleGames(games: list[Game]):
    for game in games:

        match game.state:
            case 0:
                game.player1.send("AK:" + game.player2.name)
                game.player2.send("AK:" + game.player1.name)

                game.state = 1
            case 1:
                game.player1.recv()
        continue

def handleServer(games: list[Game], players: list[Player]):
    while True:
        handlePlayers(games, players)

        handleGames(games)

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    serverSocket.bind((HOST, PORT))
    
    serverSocket.listen(5)

    print(f"Server listening on {HOST}:{PORT}")
    
    games = []
    players = []

    serverThread = threading.Thread(target=handleServer, args=(games, players))
    serverThread.start()

    try:
        while True:
            clientSocket, address = serverSocket.accept()
            clientSocket.setblocking(False)

            players.append(Player(clientSocket))
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()
