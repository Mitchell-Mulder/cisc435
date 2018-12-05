import socket
import os
import struct
import time


HOST = 'localhost'
PORT = 50007
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

# Creates a socket
def createSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


# Parse the user command and return the servers response/print it to stdout
def parseCommand(sock, command):
    response = b''
    # If exit then pass and the main function will break and close socket
    if command == "exit":
        pass
    # If list, usgae, or info then send command and return the servers response/print it to stdout
    elif command in ["list", "usage", "info"]:
        sock.sendall(command.encode())
        response = recvResponse(sock)
        if not response: return ""
        print(response.decode())
    # Else assume it is a request for cached image
    else:
        sock.sendall(command.encode())
        response = recvResponse(sock)
        if not response: return ""

        # If server has image it will respond with sending image
        if response.decode() == "sending image":
            # Read bytes into file
            data = recvResponse(sock)
            cacheFile = open("{0}/{1}".format(CACHE, command), "wb+")
            if not data: 
                cacheFile.close()
                return ""
            cacheFile.write(data)
            cacheFile.close()
            print("Image has been downlaod to cache folder")
        # Server does not have that image
        else:
            print(response.decode())
    return response.decode()


def main(test=False, testCommands=None, response=None):
    # Create a cache directory if one isn't present
    os.makedirs(CACHE, exist_ok=True)
    print(
"""Usage:   list             # List the cached images names to query
         <image-name>     # Downloads the cached image to cache folder
         info             # Sends back client name, code, and number of maximum requests(0 for unlimited)
         usage            # Query client usage if platinum user
         exit             # Closes the socket connection""")
    # Create new socket
    sock = createSocket()
    try:
        while True:
            # If testing append all responses to list to be checked
            if test:
                time.sleep(1)
                # Loop through test commands and save responses
                if testCommands:
                    command = testCommands.pop(0)
                    response.append(parseCommand(sock, command))
                else:
                    break
            else:
                # Ask for command
                command = input(">")
                # If response from server is empty then connection is closed
                response = parseCommand(sock, command)
                if response == "":
                    break
    except (BrokenPipeError, ConnectionResetError):
        print("Socket closed by server")
        if test:
            response.append('Socket Closed')
    finally:
        # Close socket
        sock.close()

# Unpack response to check length, then call recvAll with the correct length
def recvResponse(conn):
    # Read response length
    rawLength = recvAll(conn, 4)

    # Check if connection was closed
    if not rawLength: return None

    msgLength = struct.unpack('>I', rawLength)[0]

    # Read the message data
    return recvAll(conn, msgLength)


# Recv only n bytes of data sent by the server
def recvAll(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet: return None
        data += packet
    return data


if __name__ == "__main__":
    main()
