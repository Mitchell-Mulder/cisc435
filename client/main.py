import socket
import os
import struct


HOST = 'localhost'
PORT = 50007
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

def createSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def main():
    os.makedirs(CACHE, exist_ok=True)
    print("Enter list to list avaliable cache")
    s = createSocket()
    while True:
        command = input(">")
        if command == "exit":
            s.close()
            break
        elif command == "list" or command == "usage":
            s.sendall(command.encode())
            response = recvResponse(s)
            if not response: break
            print(response.decode())
        else:
            s.sendall(command.encode())
            response = recvResponse(s)
            if not response: break
            
            if response.decode() == "sending image":
                data = recvResponse(s)
                cacheFile = open("{0}/{1}".format(CACHE, command), "wb+")
                if not data: 
                    cacheFile.close()
                    break
                cacheFile.write(data)
                cacheFile.close()
                print("Image has been downlaod to cache folder")
            else:
                print(response.decode())


def recvResponse(conn):
    # Read response length
    rawLength = recvAll(conn, 4)

    # Check if connection was closed
    if not rawLength:
        return None

    msgLength = struct.unpack('>I', rawLength)[0]

    # Read the message data
    return recvAll(conn, msgLength)


def recvAll(conn, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


if __name__ == "__main__":
    main()
