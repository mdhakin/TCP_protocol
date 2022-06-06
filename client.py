import socket
import sys
import time
import FormatMsg
from bitstring import BitArray, BitStream
import hashlib

#sFile = "C:\\Users\\mooselegion\\OneDrive\\code\\1.jpg"
sFile = sys.argv[1]
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
windowsize  = 10
server_address = ('10.0.1.67', 1001)

fileDict = {}
window = {}
timer1 = {}
addr = server_address


def Load_Win():
    while 1:
        if len(window) < windowsize and len(fileDict) > 0:
            for x in fileDict:
                window[x] = fileDict[x]
                sock.sendto(window[x],server_address)
                timer1[x] = time.time()
                if len(window) >= windowsize:
                    break
        else:
            break
    for n in window:
        if n in fileDict:
            fileDict.pop(n)    

def checkWin():
    #print("checkWin")
    if len(window) > 0:
        for x in window:
            if time.time() - timer1[x] > 3:
                print(str(x) + " Has timer va " + str(time.time() - timer1[x]))
                sock.sendto(window[x],server_address)


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


def send_loop():    
    sock.settimeout(5)
    Load_Win()
    while 1:
        try:
            #print("Start Reading data")
            
            data, addr = sock.recvfrom(600)
            checkWin()
            #print("Finished Reading data")
            if data:
                tempdata = BitArray(data)
                seq = FormatMsg.getAckNumber(tempdata)
                # check if nack if nack resent window[seq]
                print(seq)
                if seq in window:
                    window.pop(seq)
                    print("Popping " + str(seq) + " off the window")
                    print("The Window still has " + str(len(window)))
                    timer1.pop(seq)
                    return
        except socket.timeout as e:
            break



ct = 1

sock.settimeout(5)
Load_File(sFile)
count = len(fileDict)

send_loop()
while len(window) > 0:
    ct += 1
    checkWin()
    print("main loop " + str(ct))
    send_loop()

print(count)

























def main():
    
    id = 0
    f = open("C:\\Users\\mooselegion\\OneDrive\\code\\1.jpg", 'rb')
    
    while 1:
        chunk = f.read(512)
        id = id + len(chunk)

        fileDict[id] = chunk

        if len(chunk) < 512:
            break


    f.close()




def send(msg):
    sock.settimeout(1)
    sock.sendto(msg,server_address)
    try:
        while 1:
            data, addr = sock.recvfrom(512)
            if data == msg:
                return True
            else:
                return False
    except socket.timeout as e:
        print(e)
        return False


def mainLoop():
    timee = 0.0
    for x in fileDict:
        while 1:
            timee = time.time()
            if send(fileDict[x]):
                print("Sent")
                break
            else:
                if (timee - time.time()) > 4:
                    print("failed")
                    return False






