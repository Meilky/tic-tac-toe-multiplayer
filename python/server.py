import os
import socket
import threading
import time

from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

def checkWin(board, player):
    for i in range(0, 7, 3):
        if(board[i] == player and board[i+1] == player and board[i+2] == player):
            return True
    for i in range(0, 3):
        if(board[i] == player and board[i+3] == player and board[i+6] == player):
            return True
    if(board[0] == player and board[4] == player and board[8] == player):
        return True
    if(board[2] == player and board[4] == player and board[6] == player):
        return True

def checkLose(board, player):
    if(player == "X"):
        opponent = "O"
    else:
        opponent = "X"
    if(checkWin(board, opponent)):
        return True
    return False

def checkTie(board):
    for x in board:
        if(x == " "):
            return False
    return True
    

def getAIMove(board, nextMove, aiPlayer):
    if(checkWin(board, aiPlayer)):
        return (-1, 10)
    elif(checkLose(board, aiPlayer)):
        return (-1, -10)
    elif(checkTie(board)):
        return (-1, 0)

    moves = []
    
    for i in range(len(board)):
        if(board[i] == " "):
            board[i] = nextMove
            
            score = getAIMove(board, ("X" if nextMove == "O" else "O"), aiPlayer)[1]
            moves.append((i, score))
            board[i] = " "

    
    if(nextMove == aiPlayer):
        maxScore = moves[0][1]
        bestMove = moves[0]
        for move in moves:
            if(move[1] > maxScore):
                bestMove = move
                maxScore = move[1]
        return bestMove
    else:
        minScore = moves[0][1]
        worstMove = moves[0]
        for move in moves:
            if(move[1] < minScore):
                worstMove = move
                minScore = move[1]
        return worstMove

games = []

class Game:
    def __init__(self,id):
        self.id = id
        self.board = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
        self.turn = "P"
        self.winner = " "

    def play(self, player, move):
        if not(move >= 0 and move <=8):
            raise Exception("Can't do the move")

        if not(self.board[move] == " "):
            raise Exception("Can't do the move")

        self.board[move] = player

        if checkWin(self.board, player):
            return 1
        if checkLose(self.board, player):
            return 2
        if checkTie(self.board):
            return 3

        return 0


    def aiPlay(self, move):
        result = self.play("O", move)

        self.turn = "P"

        if result == 1:
            self.winner = "A"
        elif result == 2:
            self.winner = "P"
        elif result == 3:
            self.winner = "T"

        return result

    def pPlay(self, move):
        result = self.play("X", move)

        self.turn = "A"

        if result == 1:
            self.winner = "P"
        elif result == 2:
            self.winner = "A"
        elif result == 3:
            self.winner = "T"

        return result

class Player:
    def __init__(self, name):
        self.state = 0
        self.name = name
        self.win = 0
        self.lost = 0
        self.rageQuit = 0

class Game:
    def __init__(self, player1, player2):
        self.board = ["","","","","","","","",""]
        self.player1 = player1
        self.player2 = player2
        self.turn = player1

def handleClientConnection(s: socket.socket, players):
    while True:
        try:
            data = s.recv(BUFFER_SIZE)

            if not data:
                break;

            (cmd, arg) = ("", "")

            try:
                (cmd, arg) = parseCmd(data.decode("ascii"))
            except: 
                s.close()
                break;

            if not cmd == "PL":
                s.send("ER:You should send your name first".encode("ascii"))
                s.close()
                break;

            if not len(arg) > 0:
                s.send("ER:You should send your name first".encode("ascii"))
                s.close()
                break;

            nameExist = False

            for player in players:
                if player.name == arg:
                    nameExist = True
                    break

            if nameExist:
                s.send("ER:A user already have your name".encode("ascii"))
                s.close()
                break;

            players.append(Player(arg))
            break;
        except socket.error as e:
            if e.errno == socket.EWOULDBLOCK:
                pass
            else:
                print("Socket error:", e)
                s.close()
                break

def handleServer(games, players):
    while True:
        nextPlayer = None

        for player in players:
            if player.state == 0:
                if not nextPlayer:
                    nextPlayer = player
                else:
                    nextPlayer.state = 1
                    player.state = 1
                    games.append(Game(nextPlayer.name,player.name))
                    nextPlayer = None

        for game in games:



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
            
            clientThread = threading.Thread(target=handleClientConnection, args=(clientSocket, players))
            clientThread.start()
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()
