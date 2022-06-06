import threading
import time
from bitstring import BitArray, BitStream
import os
import sys
import FormatMsg
import socket
import state

class Tcp_Main(threading.Thread):
    def __init__(self, port, ip, name, serverSock):
        threading.Thread.__init__(self)
        self.port = port
        self.ip = ip
        self.name = name
        self.State = state.tcpState()
        self.State.to_listen()
        self.serverSock = serverSock
        self.lastSeqNum = 1
        self.lastAckNum = 0
        self.clientip = ""
        self.clientPort = 0
    def run(self):
        print("Listening on "+ self.name)
        self.listen()
        return
    

    # main listen loop. Take in data and pass it on
    def listen(self):
        
        while 1:
            try:
                data, addr = self.serverSock.recvfrom(600)
                #self.serverSock.sendto(data, addr)
                msg = BitArray(data)
                flags = FormatMsg.getFlags(msg)
                print("ID = " + self.name)
                print("Port Num = " + str(self.port))
                print("IP Address = " + self.ip)
                print("From: " + addr[0])
                print(self.State)
                print("Source port: " + str(FormatMsg.getSource(msg)))
                print(FormatMsg.isSYNset(flags))
                q = open("stat.ini", 'r')
                bQuit = q.readline()
                q.close()
                if bQuit == 'y':
                    break
                # if the current state in estab then listen for data
                if (self.State.current_state == state.tcpState.estab and self.clientip == addr[0]):
                    if self.establishedListen():
                        break

                if (FormatMsg.isSYNset(flags) and self.State.current_state == state.tcpState.listen):
                    print("sending Ack syn")
                    self.State.to_syn_rcvd()
                    self.serverSock.settimeout(5)
                    self.send_syn_ack(data, addr)
                if (FormatMsg.isACKset(flags) and self.State.current_state == state.tcpState.syn_rcvd):
                    if (int(FormatMsg.getAckNumber(msg)) == 2):
                        self.State.to_estab()
                        self.clientip = addr[0]
                        self.clientPort = addr[1]
                        self.serverSock.settimeout(5)
                        print("Established")
                        if self.establishedListen():
                            break
                  
            except socket.timeout as e:
                    print(e)
                    f = open("stat.ini", 'r')
                    bQuit = f.readline()
                    f.close()
                    if bQuit == 'y':
                        break
                    if (self.State.current_state == state.tcpState.syn_rcvd):
                        print("sending Again")
                        self.send_syn_ack(data, addr)
                    if (self.State.current_state == state.tcpState.estab):
                        print("Client ip = " + self.clientip)
                        print("client Port = " + str(self.clientPort))
                        
                        #print("Still Established.. Listening")
                        continue
    # if the connection is established. Wait for data
    def establishedListen(self):
        self.serverSock.settimeout(60)
        bFinSet = False
        fname = ""
        recDict = {}
        print("listeneing...")

        while True:
            f = open("stat.ini", 'r')
            bQuit = f.read()
            f.close()
            bCrC = False
            if bQuit == 'y':
                break
            try:
                data,addr = self.serverSock.recvfrom(600)

                if data:
                    self.serverSock.settimeout(6)
                    #print(data)
                    msg = BitArray(data)
                    seq = FormatMsg.getSequence(msg)

                    #Compare Checksum Values
                    binData = msg.bin[192:]
                    cdata = FormatMsg.bitstring_to_bytes(binData)
                    newCRC = FormatMsg.get_crc(cdata)
                    binCRC = BitArray('0b' + msg.bin[128:144])
                    if newCRC == binCRC.uint:
                        bCrC = True
                    if seq == 2:
                        bin_fname = msg.bin[192:]
                        fname = FormatMsg.bitstring_to_bytes(bin_fname).decode()
                    elif seq in recDict:
                        returnMsg = FormatMsg.tcpHead(0,1001, 1, seq,0, bytes(0),  0, 0, 0, 1, 0, 1, 0, 5)
                        newData = FormatMsg.bitstring_to_bytes(returnMsg.bin)
                        self.serverSock.sendto(newData, addr)
                        continue
                    else:
                        if bCrC:
                            recDict[seq] = data
                        else:
                            print("Bad Checksum")
                    print("Received seq num: " + str(seq))
                    returnMsg = FormatMsg.tcpHead(0,1001, 1, seq,0, bytes(0),  0, 0, 0, 1, 0, 1, 0, 5)
                    newData = FormatMsg.bitstring_to_bytes(returnMsg.bin)
                    fin = FormatMsg.isFINset(FormatMsg.getFlags(msg))
                    if fin:
                        bFinSet = True
                    self.serverSock.sendto(newData, addr)
                    
            except  socket.timeout as e:
                if bFinSet:
                            print("Writing Copy of " + fname)
                            w = open("Copy of " + fname, 'wb')
                            for x in sorted(recDict.keys()):
                                msg = BitArray(recDict[x])
                                binData = msg.bin[192:]
                                data = FormatMsg.bitstring_to_bytes(binData)
                                w.write(data)
                                #print(len(recDict))
                            w.close()
                            return True
     

































    def send_syn_ack(self, data, addr):
        print("Sending first ack")
        #def tcpHead(source, dest, seq, ack, check, data, urgent, options, URG, ACK, RST, SYN, FIN, window):
        bitMsg = BitArray(data)
        self.lastSeqNum = 1
        self.lastAckNum = int(FormatMsg.getSequence(bitMsg)) + 1
        newMsg = FormatMsg.tcpHead(self.port, addr[1], self.lastSeqNum , self.lastAckNum ,0 ,bytes(0) ,0, 0, 0, 1, 0, 1, 0, 1)
        #print(newMsg.bin)
        newData = FormatMsg.bitstring_to_bytes(newMsg.bin)
        self.serverSock.sendto(newData, addr)
        #print(self.State)
            

    def testmsg(self, data):
        msg = FormatMsg.tcpHead("123", self.port, 10, 11, 12, data, 0,0,0,0,0,1,0,5)
        print(FormatMsg.getSource(msg))


        return

