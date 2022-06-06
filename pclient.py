# By Matthew Hakin
# 28 July 2019
# For networking class

import socket
import FormatMsg
from datetime import datetime
import time
from bitstring import BitArray, BitStream
import sys

# File to transfer
sFile = sys.argv[1]

# Set the window size. This can be adjusted
windowsize  = 10

# fileDict holds the whole file
fileDict = {}

# window holds the segments that are waiting 
# for acks
window = {}

# Timers for each segment in the window
timer1 = {}

# Set the IP Address for the server
UDP_IP_ADDRESS = sys.argv[2]

# Set the port number
UDP_PORT_NO = int(sys.argv[3])
   
server_address = (UDP_IP_ADDRESS, UDP_PORT_NO)

# blank data segment
data = bytes(0)

# Set up the socket
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initally load window with messages
def Load_Win(clientSock):
    while 1:
        if len(window) < windowsize and len(fileDict) > 0:
            for x in fileDict:
                window[x] = fileDict[x]
                clientSock.sendto(window[x],server_address)
                timer1[x] = time.time()
                if len(window) >= windowsize:
                    break
        else:
            break
    for n in window:
        if n in fileDict:
            fileDict.pop(n)    


# Check to see if the window is full. if not, fill it
# Resends packets whos timers have expired.
def checkWin(clientSock):
    #print("checkWin")
    if len(window) > 0:
        for x in window:
            if time.time() - timer1[x] > 3:
                print(str(x) + " Has timer va " + str(time.time() - timer1[x]))
                clientSock.sendto(window[x],server_address)

# This function loads the file into a dictionary 
def Load_File(filename):
    chunk = sys.argv[1].encode('utf-8')
    crc = FormatMsg.get_crc(chunk)
    print(chunk)
    msg = FormatMsg.tcpHead(0,1001, 2, 0,crc, chunk,  0, 0, 0, 0, 0, 1, 1, 5)
    data = FormatMsg.bitstring_to_bytes(msg.bin)
    fileDict[2] = data
    seq = 3
    f = open(filename, 'rb')
    while 1:
        chunk = f.read(512)
        seq += len(chunk)
        if len(chunk) < 512:
            #def tcpHead(source, dest, seq, ack, check, data, urgent, options, URG, ACK, RST, SYN, FIN, window):
            crc = FormatMsg.get_crc(chunk)
            msg = FormatMsg.tcpHead(0,1001, seq, 0,crc, chunk,  0, 0, 0, 0, 0, 1, 1, 5)
            data = FormatMsg.bitstring_to_bytes(msg.bin)
            fileDict[seq] = data
        else:
            #def tcpHead(source, dest, seq, ack, check, data, urgent, options, URG, ACK, RST, SYN, FIN, window):
            crc = FormatMsg.get_crc(chunk)
            msg = FormatMsg.tcpHead(0,1001, seq, 0,crc, chunk,  0, 0, 0, 0, 0, 1, 0, 5)
            data = FormatMsg.bitstring_to_bytes(msg.bin)
            fileDict[seq] = data
        if len(chunk) < 512:
            return True


# Main send loop of the program
def send_loop(clientSock):    
    clientSock.settimeout(5)
    Load_Win(clientSock)
    while 1:
        try:
            data, addr = clientSock.recvfrom(600)
            checkWin(clientSock)
            if data:
                tempdata = BitArray(data)
                seq = FormatMsg.getAckNumber(tempdata)
                # check if nack if nack resent window[seq]
                if seq in window:
                    window.pop(seq)
                    print("The Window still has " + str(len(window)))
                    timer1.pop(seq)
                    return
        except socket.timeout as e:
            break





































#def tcpHead(source, dest, seq, ack, check, data, urgent, options, URG, ACK, RST, SYN, FIN, window):
def main():
    data = bytes(0)

    msg = FormatMsg.tcpHead(5000, 5000, 1, 0,0,data,0,0,0,0,0,1,0,5)
    data2 = FormatMsg.bitstring_to_bytes(msg.bin)
    clientSock.sendto(data2, (UDP_IP_ADDRESS, UDP_PORT_NO))
    time.sleep(1)
    clientSock.settimeout(10)
    while 1:
        try:
            data, addr = clientSock.recvfrom(600)
            ackmsg = BitArray(data)

            flags = FormatMsg.getFlags(ackmsg)

            print(FormatMsg.isACKset(flags))
            print(FormatMsg.isSYNset(flags))
            print("Sequence num: "+ str(FormatMsg.getAckNumber(ackmsg)))
            print(addr[0])
            time.sleep(1)
            
            newOutMssg = FormatMsg.tcpHead(5000,5000, 2, int(FormatMsg.getSequence(ackmsg)) + 1, 0,bytes(0), 0,0,0,1,0,0,0,1)
            newOutMssgData = FormatMsg.bitstring_to_bytes(newOutMssg.bin)
            clientSock.sendto(newOutMssgData,addr)

            break
        except socket.timeout as e:
            print(e)
            break
    

def sendData():
    msgRepos = {}

    f = open("1.jpg", 'rb')
    id = 3
    while 1:
        chunk = f.read(512)
        id = id + len(chunk) 

        msgRepos[id] = chunk

        if len(chunk) < 512:
            break

    #for n in msgRepos:
        #print(msgRepos[n])


    

    f.close()

    


main()
sendData()


ct = 1

clientSock.settimeout(5)
Load_File(sFile)
count = len(fileDict)

send_loop(clientSock)
while len(window) > 0:
    ct += 1
    checkWin(clientSock)
    print("main loop " + str(ct))
    send_loop(clientSock)

print(count)