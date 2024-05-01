import socket
from utils import parseCmd

HOST = '127.0.0.1'
PORT = 6666
BUFFER_SIZE = 1024


def main():
    name = input("Wha't your name:")

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 
    s.connect((HOST,PORT))

    s.send(("PL:"+name).encode("ascii"))

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


            print(cmd, arg)
            break
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

