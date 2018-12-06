# CISC 435

## Usage
To run my project please use **Python 3.7.1**. Do not use Python 2.x or the project simply will not work.

1. To create the server to handle incoming requests from clients run this command inside the project folder:

    `python ./server/server.py`

    This will start the server and begin listening for connections. To exit just type control-c.

2. To create clients to submit requests to the server run this command inside the project folder:

    `python ./client/client.py`

    This will create a client and prompt you with the list of available commands to submit to the server. Simply enter the commands and the server’s response will be printed out.

## Automated Tests
* To run automated test run:

    `python -m unittest -v testClientServer.py`

## Report
* The report is located in root of the project folder named: `Mitchell-Mulder-CISC435-Project.pdf`