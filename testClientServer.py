import unittest
import threading
import time
import os
import sys
import json
from server import server
from client import client


class TestClientServer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        f = open(os.devnull, 'w')
        sys.stdout = f


    def testClientServer(self):
        expected = ['["dog.png", "cat.jpg", "bear.jpg"]', '']
        threads = []
        response = []
        response2 = []
        response3 = []

        thread = threading.Thread(target=server.main)
        thread2 = threading.Thread(target=client.main, args=(True, ['list', 'exit'], response))
        thread3 = threading.Thread(target=client.main, args=(True, ['list', 'exit'], response2))
        thread4 = threading.Thread(target=client.main, args=(True, ['list', 'exit'], response3))

        threads.extend([thread2, thread3, thread4])

        thread.start()
        for t in threads:
            time.sleep(0.5)
            t.start()

        for t in threads:
            t.join()

        server.alive = False
        thread.join()
        server.alive = True

        self.assertListEqual(expected, response)
        self.assertListEqual(expected, response2)
        self.assertListEqual(expected, response3)


    def testMaxClient(self):
        threads = []
        response = []


        thread = threading.Thread(target=server.main)
        thread2 = threading.Thread(target=client.main, args=(True, ['list', 'list', 'list', 'exit'], []))
        thread3 = threading.Thread(target=client.main, args=(True, ['list', 'list', 'list', 'exit'], []))
        thread4 = threading.Thread(target=client.main, args=(True, ['list', 'list', 'list', 'exit'], []))
        thread5 = threading.Thread(target=client.main, args=(True, ['list', 'list', 'list', 'exit'], response))

        threads.extend([thread2, thread3, thread4, thread5])

        thread.start()
        for t in threads:
            time.sleep(0.5)
            t.start()

        for t in threads:
            t.join()
        server.alive = False
        thread.join()
        server.alive = True

        flag = False
        for res in response:
            if res == 'Socket Closed':
                flag = True
        self.assertTrue(flag)


    def testImageCache(self):
        cacheDir = os.path.join(os.path.dirname(__file__), 'client/cache')
        for f in os.listdir(cacheDir):
            os.remove(os.path.join(cacheDir, f))
        expected = ['dog.png', 'cat.jpg']
        thread = threading.Thread(target=server.main)
        thread2 = threading.Thread(target=client.main, args=(True, ['list', 'dog.png', 'cat.jpg', 'exit'], []))


        thread.start()
        time.sleep(1)
        thread2.start()

        thread2.join()
        server.alive = False
        thread.join()
        server.alive = True
        files = []
        for f in os.listdir(cacheDir):
            files.append(f)
        self.assertListEqual(files, expected)


    def testQuota(self):
        response = []
        thread = threading.Thread(target=server.main)
        thread2 = threading.Thread(target=client.main, args=(True, ['info', 'dog.png', 'cat.jpg', 'bear.jpg', 'dog.png', 'cat.jpg', 'bear.jpg', 'exit'], response))

        thread.start()
        time.sleep(1)
        thread2.start()

        thread2.join()
        server.alive = False
        thread.join()
        server.alive = True
        clientInfo = json.loads(response[0])
        MAX_REQUESTS = clientInfo["MAX_REQUESTS"]
        if MAX_REQUESTS == 3:
            self.assertGreaterEqual(len(response), 4)
            for res in response[1:4]:
                self.assertEqual(res, 'sending image')
        elif MAX_REQUESTS == 5:
            self.assertGreaterEqual(len(response), 6)
            for res in response[1:6]:
                self.assertEqual(res, 'sending image')
        elif MAX_REQUESTS == 0:
            self.assertGreaterEqual(len(response), 7)
            for res in response[1:7]:
                self.assertEqual(res, 'sending image')
        else:
            self.fail('Max requests can\'t be ${0}'.format(MAX_REQUESTS))


    def testPlatinumUser(self):
        response = []
        thread = threading.Thread(target=server.main)
        thread2 = threading.Thread(target=client.main, args=(True, ['info', 'cat.jpg', 'usage', 'exit'], response))

        thread.start()
        time.sleep(1)
        thread2.start()

        thread2.join()
        server.alive = False
        thread.join()
        server.alive = True
        clientInfo = json.loads(response[0])
        MAX_REQUESTS = clientInfo["MAX_REQUESTS"]
        if MAX_REQUESTS == 0:
            usage = json.loads(response[2])
            self.assertTrue(usage.get(clientInfo['name']))
            self.assertEqual(len(usage[clientInfo['name']]), 1)
            self.assertEqual(usage[clientInfo['name']][0]['request'], 'cat.jpg')
        else:
            error = response[2]
            self.assertEqual(error, 'invalid request')


if __name__ == '__main__':
    unittest.main()