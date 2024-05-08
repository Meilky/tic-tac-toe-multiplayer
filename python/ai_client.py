import socket
from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

def prettyPrint(board, me, opp):
    out = []

    for i in range(0,9,3):
        for j in range(3):
            case = board[i+j]

            if case == me:
                out.append("X")
            elif case == opp:
                out.append("O")
            else:
                out.append(str(i+j))

    print(" " + out[0] + " | " + out[1] + " | " + out[2])
    print("-----------")
    print(" " + out[3] + " | " + out[4] + " | " + out[5])
    print("-----------")
    print(" " + out[6] + " | " + out[7] + " | " + out[8])

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    s.connect((HOST,PORT))
    s.setblocking(False)

    name = input("What's your name: ")
    oppenent = "";

    s.send(("PL:"+name).encode("ascii"))
    s.send(("EN:").encode("ascii"))
    print("Waiting for another player...")

    while True:
        try:
            data = s.recv(BUFFER_SIZE)

            if not data:
                break;

            cin = parseCmd(data.decode("ascii"))

            if not cin:
                break;

            (cmd, arg) = cin 

            if cmd == "AK":
                oppenent = arg
                print("Playing against", arg)
            elif cmd == "GE":
                print("The game is a", arg)
                if not input("Do you want to play another game (y/n): ") == "y":
                    break;
                s.send(("EN:").encode("ascii"))
                print("Waiting for another player...")
            elif cmd == "TU":
                args = arg.split(",")

                print("Turn to", args[0])
                prettyPrint(args[1:], name, oppenent)

                if args[0] == name:
                    move = input("Move: ")
                    s.send(("MV:" + move).encode("ascii"))
            elif cmd == "ER":
                print(arg)
                move = input("Move: ")
                s.send(("MV:" + move).encode("ascii"))

        except socket.error as e:
            if e.errno == socket.EWOULDBLOCK:
                pass
            else:
                print("Socket error:", e)
                break
        
    s.close()
 
if __name__ == '__main__':
    main()

