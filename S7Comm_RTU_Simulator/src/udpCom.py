#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        udpCom.py
#
# Purpose:     This module will provide socket[UDP] client and server communication
#              API for message sending and file transfer.
#
# Author:      Yuancheng Liu
#
# Created:     2019/01/15
# Version:     v_0.2
# Copyright:   Copyright (c) 2019 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Program Design:
    
    We want to create a message communication channel for the data transfer through 
    UDP,  two classes will be provide in this module : 

    - client: send UDP msg/chunk to the destination and get the response (optional). 
    - server: allow the user to pass in their message hanlder in the server, if the handler
            function return value, the value will be send back to the client side.

    If the message/data size is bigger than the MAX/pre-configured UDP socket buffer 
    size, it will be split to several chunks, each chunk will be buffer size - 1 bytes.
    Then the chunk will be send to destination under splitted sequence. The data transfer 
    will follow below steps:
        1. Send b'BM;Send;<messageSize>' to the server side.
        2. Send every thrunk in a loop.
        3. Send b'BM;Sent;Finish' to identify finished and trigger the response.
    The server's reply Big message will follow step 1 & 2.

    Usage: 
    - server: the server side will have a loop to keep fetching data from the buffer,
            so it will good to package it in a threading class running parallel with 
            your main program thread.(As shown in the <udpComTest.py>)
    - client: client = udpClient((<ip address>, <port>))
"""

import time
import socket
from math import ceil

BUFFER_SZ = 4096        # Default socket buffer size. Set to value smaller than MTU will increase small message transfer throughput.
BUFFER_SZ_MAX = 65507   # UDP maximum buffer size.
RESP_TIME = 0.01
BIG_MSG_FLG = 'BM'      # Flag to identify big size message.      
CODE_FMT = 'utf-8'      # default str <-> bytes encode/decode format.

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class udpClient(object):
    """ UDP client module."""
    def __init__(self, ipAddr):
        """ Create an ipv4 (AF_INET) socket object using the udp protocol (SOCK_DGRAM)
            init example: client = udpClient(('127.0.0.1', 502))
            Args:
                ipAddr (tuple(str(), int())): IP address tuple ip + port.
        """
        self.ipAddr = ipAddr
        self.bufferSize = BUFFER_SZ
        self.chunkSize = max(1, self.bufferSize - 8) # make the chunk size 1 byte smaller than the bugger to send big message.
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setTimeOut()

#--udpClient-------------------------------------------------------------------
    def receiveChunk(self, messageSZ):
        """ recieve the chunks based on the data type
            Args:
                messageSZ (int): the whole message size
            Returns:
                bytes: the whole data chunks.
        """
        receiveCount = ceil(messageSZ*1.0/self.chunkSize) # after python3 no need to *1.0
        data = b''
        try:
            for _ in range(receiveCount):
                subData, _ = self.client.recvfrom(self.bufferSize)
                data += subData
        except Exception as err:
            print("udpClient;receiveChunk(): Data transfer error, some data missing.")
            print("Error: %s" %str(err))
        return data

#--udpClient-------------------------------------------------------------------
    def sendMsg(self, msg, resp=False, ipAddr=None):
        """ Convert the msg (smaller than the buffer size) to bytes and send it 
            to UDP server. 
            - resp: server response flag, method will wait server's response and 
                return the bytes format response if it is set to True. 
        """
        if not ipAddr is None: self.ipAddr = ipAddr  # reset ip address if needed.
        if self.client is None: return None # Check whether disconnected.
        if not isinstance(msg, bytes): msg = str(msg).encode(CODE_FMT)
        self.client.sendto(msg, self.ipAddr)
        if resp:
            try:
                data, _ = self.client.recvfrom(self.bufferSize)
                if b'BM;Send' in data:
                    _, _, messageSZ = data.decode(CODE_FMT).split(';') 
                    data = self.receiveChunk(int(messageSZ))
                return data
            except Exception as error:
                print("udpClient;sendMsg(): Can not connect to the server!")
                print(error)
                # self.disconnect() no need to diconnect if we want to do reconnect.
                return None
        return None

#--udpClient-------------------------------------------------------------------
    def sendChunk(self, message, resp=False):
        """ Send the message bigger than the buffer size to the server side.
            Args:
                message (str/bytes): _description_
                resp (bool, optional): _description_. Defaults to False.
            Returns:
                _type_: server's response.
        """
        messageSZ = len(message)
        sendCount = ceil(messageSZ/self.chunkSize)
        # Step 1: tell server side the whole message size: BM;Send;<dataSize>
        msg = ';'.join((BIG_MSG_FLG, 'Send', str(messageSZ))) 
        reply = self.sendMsg(msg, resp=False)
        # ready to receive big size message.
        messageChunks = [ message[i:i+self.chunkSize] for i in range(0, messageSZ, self.chunkSize) ]
        for data in messageChunks:
            self.sendMsg(data, resp=False)
            # finished send all the message.
        msg = ';'.join((BIG_MSG_FLG, 'Sent', 'Finish'))
        reply = self.sendMsg(msg, resp=resp)
        return reply

#--udpClient-------------------------------------------------------------------
    def setBufferSize(self, bufferSize=BUFFER_SZ):
        """ Update the socket buffer size."""
        if isinstance(bufferSize, int) and 1 < bufferSize < BUFFER_SZ_MAX:
            self.bufferSize = bufferSize
            self.chunkSize = max(1, self.bufferSize-8)
            return True
        print("Error: the input buffer size must be a int 0 < x < 65507.")
        return False

#--udpClient-------------------------------------------------------------------
    def setTimeOut(self, timeoutT=20):
        if isinstance(timeoutT, int) and timeoutT > 0:
            self.client.settimeout(timeoutT)
            return True
        print("Error: the timeoutT must be a int x > 0 ")
        return False

#--udpClient-------------------------------------------------------------------
    def disconnect(self):
        """ Send a empty logout message and close the socket."""
        self.sendMsg('', resp=False)
        time.sleep(RESP_TIME) # sleep very short while before close the socket to \
        # make sure the server have enought time to handle the close method, when \
        # server computer is fast, this is not a problem.

        # Call shut down before close: https://docs.python.org/3/library/socket.html#socket.socket.shutdown
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.client = None

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class udpServer(object):
    """ UDP server module."""
    def __init__(self, parent, port):
        """ Create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
            init example: server = udpServer(None, 5005)
        """
        self.bufferSize = BUFFER_SZ
        self.chunkSize = max(1, self.bufferSize-8)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', port))
        self.terminate = False  # Server terminate flag.

#--udpServer-------------------------------------------------------------------
    def receiveChunk(self, messageSZ):
        """ recieve the chunks based on the data type
            Args:
                messageSZ (int): the whole message size
            Returns:
                bytes: the whole data Chunks.
        """
        receiveCount = ceil(messageSZ/self.chunkSize)
        data = b''
        try:
            for _ in range(receiveCount):
                subData, _ = self.server.recvfrom(self.bufferSize)
                data += subData
        except Exception as err:
            print("udpServer;receiveChunk(): Data transfer error, some data missing.")
            print("Error: %s" %str(err))
        return data

#--udpServer-------------------------------------------------------------------
    def serverStart(self, handler=None):
        """ Start the UDP server to handle the incomming message."""
        while not self.terminate:
            data, address = self.server.recvfrom(self.bufferSize)
            # Check whether the message is a big message
            if b'BM;Send' in data:
                bmMsg = data.decode(CODE_FMT)
                _, _, size = bmMsg.split(';')
                data = self.receiveChunk(int(size))
                subData, _ = self.server.recvfrom(self.bufferSize)
            print("Accepted connection from %s" % str(address))
            msg = handler(data) if not handler is None else data
            if not msg is None:  # don't response client if the handler feed back is None
                if not isinstance(msg, bytes): msg = str(msg).encode(CODE_FMT)
                if len(msg) < self.bufferSize:
                    self.server.sendto(msg, address)
                else:
                    self.sendChunk(msg, address)
        # close the server.
        self.server.close()

#--udpClient-------------------------------------------------------------------
    def setBufferSize(self, bufferSize=BUFFER_SZ):
        if isinstance(bufferSize, int) and 1 < bufferSize < BUFFER_SZ_MAX:
            self.bufferSize = bufferSize
            self.chunkSize = max(1, self.bufferSize-8)
            return True
        print("Error: the input buffer size must be a int 1 < x < 65507.")
        return False

#--udpClient-------------------------------------------------------------------
    def sendChunk(self, message, address):
        """ reply the message bigger than the buffer size to the client side.
            Args:
                message (str/bytes): _description_
                resp (bool, optional): _description_. Defaults to False.
            Returns:
                _type_: server's response.
        """
        messageSZ = len(message)
        sendCount = ceil(messageSZ/self.chunkSize) if messageSZ > self.bufferSize else 1
        # Step 1: tell server side the whole message size: BM;Send;<dataSize>
        msg = ';'.join((BIG_MSG_FLG, 'Send', str(messageSZ)))
        self.server.sendto(msg.encode(CODE_FMT), address)
        # ready to receive big size message.
        messageChunks = [ message[i:i+self.chunkSize] for i in range(0, messageSZ, self.chunkSize) ]
        for data in messageChunks:
            self.server.sendto(data, address)

#--udpServer-------------------------------------------------------------------
    def serverStop(self):
        self.terminate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Use case program: udpComTest.py

def msgHandler(msg):
    """ The test handler method passed into the UDP server to handle the 
        incoming messages.
    """
    print("Incomming message: %s" % str(msg))
    return msg

def main():
    """ Main function used for demo the module."""
    print("Run the module as a UDP (1) UDP echo server (2) UDP client: ")
    uInput = str(input())
    if uInput == '1':
        print(" - Please input the UDP port: ")
        udpPort = int(str(input()))
        server = udpServer(None, udpPort)
        print("Start the UDP echo server licening port [%s]" % udpPort)
        server.serverStart(handler=msgHandler)
    elif uInput == '2':
        print(" - Please input the IP address: ")
        ipAddr = str(input())
        print(" - Please input the UDP port: ")
        udpPort = int(str(input()))
        client = udpClient((ipAddr, udpPort))
        while True:
            print(" - Please input the message: ")
            msg = str(input())
            resp = client.sendMsg(msg, resp=True)
            print(" - Server resp: %s" % str(resp))
    else:
        print("Input %s is not valid, program terminate." % str(uInput))

if __name__ == "__main__":
    main()
