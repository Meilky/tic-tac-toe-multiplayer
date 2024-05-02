import socket
from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024


def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 
    s.connect((HOST,PORT))

    name = input("What's your name:")

    s.send(("PL:"+name).encode("ascii"))

    print("Waiting to be matched")

    board = ["", "", "", "", "", "","", "", ""]
    otherPlayer = ""
    while True:
        try:
            data = s.recv(BUFFER_SIZE)

            if not data:
                break;

            (cmd, arg) = ("", "")

            try:
                (cmd, arg) = parseCmd(data.decode("ascii"))
            except: 
                pass

            if cmd == "AK":
                otherPlayer = arg

            print(cmd, arg)
        except socket.error as e:
            if e.errno == socket.EWOULDBLOCK:
                pass
            else:
                print("Socket error:", e)
                break
        
    s.close()
    print("The connection has been closed")
 
if __name__ == '__main__':
    main()

