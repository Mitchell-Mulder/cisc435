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


def getCache():
    files = []
    directory = os.path.join(os.path.dirname(__file__), 'cache')
    for f in os.listdir(directory):
        files.append(f)
    return files


def createInfo():
    name = "client-{0}".format(random.randint(1,10000))
    code = random.randint(50,300)
    return {"name": name, "code": code}


def getMaxRequests(code):
    if code % 10 == 0:
        return 0
    elif code % 2 == 0:
        return 3
    else:
        return 5


def sendResponse(conn, response):
    # Prefix each message with a header that specifies the length of the message
    response = struct.pack('>I', len(response)) + response
    conn.sendall(response)


def clientThread(conn):
    global connectionsCounter

    clientInfo = createInfo()
    MAX_REQUESTS =  getMaxRequests(clientInfo["code"])
    print("code: {0}, max_requests:{1}".format(clientInfo["code"], MAX_REQUESTS))

    with open(HISTORY, "r") as hist:
        fileData = json.load(hist)

    fileData[clientInfo["name"]] = []

    with open(HISTORY, "w") as hist:
        json.dump(fileData, hist)

    requestCounter = 0
    while True:
        data = conn.recv(1024)
        if not data: break
        data = data.decode()
        if data == "list":
            response = getCache()
            response = json.dumps(response).encode()
        elif data == "info":
            response = json.dumps(clientInfo)
            response = response.encode()
        elif data in getCache():
            if requestCounter >= MAX_REQUESTS and MAX_REQUESTS != 0:
                break

            with open(HISTORY, "r") as hist:
                fileData = json.load(hist)

            now = datetime.datetime.now()
            clientData = fileData[clientInfo["name"]]
            clientData.append({"request": data, "datetime": now.strftime("%Y-%m-%dT%H:%M:%S")})

            with open(HISTORY, "w") as hist:
                json.dump(fileData, hist)
            
            sendResponse(conn, "sending image".encode())

            cacheFile = open("{0}/{1}".format(CACHE, data), "rb")
            cacheBytes = cacheFile.read()
            response = cacheBytes
            cacheBytes.close()

            requestCounter += 1
        else:
            response = "invalid request"
            response = response.encode()
        sendResponse(conn, response)
    connectionsCounter -= 1
    conn.close()


def main():
    # Overwrite or create the history file
    with open(HISTORY, "w") as hist:
        json.dump({}, hist)

    global connectionsCounter
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(0)
    while True:
        conn, addr = s.accept()
        connectionsCounter += 1
        if connectionsCounter > MAX_CONNECTIONS:
            connectionsCounter -= 1
            conn.close()
            continue
        print('Connected by', addr)
        threading.Thread(target=clientThread, args=(conn,)).start()


if __name__ == "__main__":
    main()
