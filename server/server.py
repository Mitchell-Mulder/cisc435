import socket
import json
import os
import threading
import random
import datetime
import struct

MAX_CONNECTIONS = 3
HOST = ''
PORT = 50007
HISTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache/")
connectionsCounter = 0
alive = True


# This function reads the names of all the files in the cache folder and returns a list of file names
def getCache():
    files = []
    directory = os.path.join(os.path.dirname(__file__), 'cache')
    for f in os.listdir(directory):
        files.append(f)
    return files


# Creates client name, code, and based on the code calculated the maximum requests
def createInfo():
    name = "client-{0}".format(random.randint(1,10000))
    code = random.randint(50,300)
    return {"name": name, "code": code, "MAX_REQUESTS": getMaxRequests(code)}


# Calculates the maximum requests based on the code
def getMaxRequests(code):
    if code % 10 == 0:
        return 0
    elif code % 2 == 0:
        return 3
    else:
        return 5


# Appends all responses with a header that specifies the message length.
# This was needed to send the images fragmented into multiple packets
def sendResponse(conn, response):
    response = struct.pack('>I', len(response)) + response
    conn.sendall(response)


# This is the client thread that is spawned when a connection is accepted
def clientThread(conn, addr):
    # Used to ensure maximum connections do not exceed 3
    global connectionsCounter

    # Creates client info
    clientInfo = createInfo()
    MAX_REQUESTS =  clientInfo["MAX_REQUESTS"]

    # Creates a new entry inside the history.json file for the new client
    with open(HISTORY, "r") as hist:
        fileData = json.load(hist)
    fileData[clientInfo["name"]] = []
    with open(HISTORY, "w") as hist:
        json.dump(fileData, hist)

    # Counts the number of requests to ensure quota is not exceeded
    requestCounter = 0

    while True:
        # Listen for incomming requests, if None then connection is closed an break
        data = conn.recv(1024)
        if not data: break
        data = data.decode()

        # If request is list then return the list of file names in the cache folder
        if data == "list":
            response = getCache()
            response = json.dumps(response).encode()
        # If request is info then return the client's info
        elif data == "info":
            response = json.dumps(clientInfo).encode()
        # if the request is usage and the client is a platinum user then return the history.json file
        elif data == "usage" and MAX_REQUESTS == 0:
            with open(HISTORY, "rb") as hist:
                response = hist.read()
        # If the request is a file in the cache folder
        elif data in getCache():
            # if the client exceeded their quota then break and connection will be closed
            if requestCounter >= MAX_REQUESTS and MAX_REQUESTS != 0:
                break

            # Add request to history.json file
            with open(HISTORY, "r") as hist:
                fileData = json.load(hist)

            now = datetime.datetime.now()
            clientData = fileData[clientInfo["name"]]
            clientData.append({"request": data, "datetime": now.strftime("%Y-%m-%dT%H:%M:%S")})

            with open(HISTORY, "w") as hist:
                json.dump(fileData, hist)

            # Send a response back to client to get ready
            sendResponse(conn, "sending image".encode())

            # Read the cached file as bytes and send it to the client
            cacheFile = open("{0}/{1}".format(CACHE, data), "rb")
            cacheBytes = cacheFile.read()
            response = cacheBytes
            cacheFile.close()

            # Increment the requests counter
            requestCounter += 1
        # Invaild request
        else:
            response = "invalid request"
            response = response.encode()
        sendResponse(conn, response)
    # Connection counter decremented and connection is closed
    connectionsCounter -= 1
    print('Connection closed by', addr)
    conn.close()


def main():
    # Used to stop the server 
    global alive

    # Used to ensure maximum connections do not exceed 3
    global connectionsCounter

    # Overwrite or create the history file
    with open(HISTORY, "w") as hist:
        json.dump({}, hist)

    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    s.bind((HOST, PORT))
    s.listen(0)
    threads = []
    while alive:
        try:
            # Accept incomming connections
            conn, addr = s.accept()
            connectionsCounter += 1

            # If quota is exceed close connection
            if connectionsCounter > MAX_CONNECTIONS:
                connectionsCounter -= 1
                conn.close()
                continue
            print('Connected by', addr)

            # Spawn a client thread
            t = threading.Thread(target=clientThread, args=(conn,addr))
            t.start()
            threads.append(t)
        except socket.timeout:
            pass

    # Ensure all threads have exited
    for t in threads:
        t.join()
    # Close connection
    s.close()


if __name__ == "__main__":
    main()
