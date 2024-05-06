import socket
from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    s.connect((HOST,PORT))
    s.setblocking(False)

    name = input("What's your name:")

    s.send(("PL:"+name).encode("ascii"))
    s.send(("EN:").encode("ascii"))

    while True:
        try:
            data = s.recv(BUFFER_SIZE)

            if not data:
                break;

            cin = parseCmd(data.decode("ascii"))

            if not cin:
                break;

            (cmd, arg) = cin 

            if cmd == "GE":
                s.send(("EN:").encode("ascii"))

            print(cmd, arg)
        except socket.error as e:
            if e.errno == socket.EWOULDBLOCK:
                pass
            else:
                print("Socket error:", e)
                break
        
    s.close()
 
if __name__ == '__main__':
    main()

