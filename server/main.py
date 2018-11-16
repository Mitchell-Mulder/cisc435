# Echo server program
import socket
import json
import os
import threading
import time
import random

MAX_CONNECTIONS = 3
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
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


def clientThread(conn):
    global connectionsCounter
    clientInfo = createInfo()
    MAX_REQUESTS =  getMaxRequests(clientInfo["code"])
    print("code: {0}, max_requests:{1}".format(clientInfo["code"], MAX_REQUESTS))
    requestCounter = 0
    while True:
        data = conn.recv(1024)
        if not data: break
        data = data.decode()
        if data == "list":
            response = getCache()
        elif data == "info":
            response = clientInfo
        elif data in getCache():
            if requestCounter >= MAX_REQUESTS and MAX_REQUESTS != 0:
                break
            response = data
            requestCounter += 1
        else:
            response = "invalid request"
        conn.sendall(json.dumps(response).encode())
    connectionsCounter -= 1
    conn.close()


def main():
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
