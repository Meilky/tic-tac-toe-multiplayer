import socket
import re

PROT_RE = r"(\w+)\:(.*)"

def printBoard(board):
    print("\n")
    for i in range(9):
        if(not board[i] == " "):
            print(board[i], end="   ")
        else:
            print("_", end="   ")
        if(i==2 or i==5):
            print("")
    print("\n")
 
def main():
    host = '127.0.0.1'
    port = 6666
 
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 
    s.connect((host,port))

    while True:
        data = s.recv(1024)

        if not data:
            break

        payload = data.decode("ascii")

        result = re.search(PROT_RE, payload)

        if not result:
            break

        (cmd, arg) = result.groups()

        match cmd:
            case "BO":
                printBoard(arg.split(","))
            case "GE":
                if arg == "P":
                    print("You win")
                elif arg == "T":
                    print("It's a tie")
                elif arg == "A":
                    print("You lost")

                break;
            case "ER":
                print("Error:", arg)

        move = input("What to play:")

        s.send(("MV:" + move).encode("ascii"))
        
    s.close()
 
if __name__ == '__main__':
    main()

