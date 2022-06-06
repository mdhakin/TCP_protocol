import socket
import sys
import time
import FormatMsg
from bitstring import BitArray, BitStream
import hashlib



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
fname = ""
recDict = {}

serveraddress = "10.0.1.67"
serverport = 1001
sock.bind((serveraddress,serverport))
bFinSet = False

print("listeneing...")

while True:
    f = open("C:\\Users\\mooselegion\\OneDrive\\code\\stat.ini", 'r')
    bQuit = f.read()
    f.close()
    
    if bQuit == 'y':
        break
    try:
        #print("Still listeneing...")
        data,addr = sock.recvfrom(600)

        if data:
            sock.settimeout(6)
            #print(data)
            msg = BitArray(data)
            seq = FormatMsg.getSequence(msg)
            if seq == 2:
                bin_fname = msg.bin[192:]
                fname = FormatMsg.bitstring_to_bytes(bin_fname).decode()
            elif seq in recDict:
                returnMsg = FormatMsg.tcpHead(0,1001, 1, seq,0, bytes(0),  0, 0, 0, 1, 0, 1, 0, 5)
                newData = FormatMsg.bitstring_to_bytes(returnMsg.bin)
                sock.sendto(newData, addr)
                continue
            else:
                recDict[seq] = data
            print(seq)
            returnMsg = FormatMsg.tcpHead(0,1001, 1, seq,0, bytes(0),  0, 0, 0, 1, 0, 1, 0, 5)
            newData = FormatMsg.bitstring_to_bytes(returnMsg.bin)
            fin = FormatMsg.isFINset(FormatMsg.getFlags(msg))
            if fin:
                bFinSet = True
            sock.sendto(newData, addr)
            
    except  socket.timeout as e:
       if bFinSet:
                w = open("Copy of " + fname, 'wb')
                for x in sorted(recDict.keys()):
                    msg = BitArray(recDict[x])
                    binData = msg.bin[192:]
                    data = FormatMsg.bitstring_to_bytes(binData)
                    w.write(data)
                    print(len(recDict))
                w.close()
                break


    

      