import socket
import threading
import re

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

PROT_RE = r"(\w+)\:(.*)"


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
    return False

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

def handle_client(s: socket.socket, gameId):
    game = Game(gameId)
    games.append(game)

    print("Start game:", gameId)
    
    while True:
        if not game.turn == "P":
            continue;

        if not game.winner == " ":
            if game.winner == "T":
                s.send(("GE:T").encode("ascii"))
            elif game.winner == "P":
                s.send(("GE:P").encode("ascii"))
            elif game.winner == "A":
                s.send(("GE:A").encode("ascii"))

            break


        s.send(("BO:" + ",".join(game.board)).encode("ascii"))

        data = s.recv(BUFFER_SIZE)

        if not data:
            break

        payload = data.decode("ascii")

        result = re.search(PROT_RE, payload)

        if not result:
            break

        (cmd, arg) = result.groups()

        match cmd:
            case "BO":
                s.send(("BO:" + ",".join(game.board)).encode("ascii"))
            case "MV":
                try:
                    result = game.pPlay(int(arg))

                    if result == 1:
                        s.send(("GE:P").encode("ascii"))
                    elif result == 2:
                        s.send(("GE:A").encode("ascii"))
                    elif result == 3:
                        s.send(("GE:T").encode("ascii"))
                except:
                    s.send(("ER:Can't do the move").encode("ascii"))
            case _:
                s.send("ER:Unkown command".encode("ascii"))

    
    s.close()

def handle_ai():
    while True:
        for i in range(0, len(games)):
            game = games[i]

            if(game.turn == "A" and game.winner == " "):
                moves = getAIMove(game.board, "O", "O")

                game.aiPlay(moves[0])


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.bind((HOST, PORT))
    
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    
    ai_thread = threading.Thread(target=handle_ai)
    ai_thread.start()

    gameId = 0;
    try:
        while True:
            client_socket, address = server_socket.accept()
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, gameId))
            client_thread.start()

            gameId += 1
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
