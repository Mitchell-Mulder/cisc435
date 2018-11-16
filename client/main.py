import socket

HOST = 'localhost'
PORT = 50007

def createSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def main():
    print("Enter list to list avaliable cache")
    s = createSocket()
    while True:
        command = input(">")
        if command == "exit":
            s.close()
            break
        else:
            s.sendall(command.encode())

        response = s.recv(1024)
        if not response: break
        print(response.decode())


if __name__ == "__main__":
    main()
