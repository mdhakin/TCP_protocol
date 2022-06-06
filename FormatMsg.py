# This module handles the formatting of the TCP Header

from bitstring import BitArray, BitStream
import os
import sys
import hashlib

#Function to convert a bitstring to a bytes object
def bitstring_to_bytes(s):
        if s == '':
                return 0
        return int(s, 2).to_bytes(len(s) // 8, byteorder='big')

def getSource(msg):
    msg3 = msg.bin[0:16]
    msg4 = BitArray('0b' + msg3)
    return msg4.int

def getDest(msg):
    msg3 = msg.bin[16:32]
    msg4 = BitArray('0b' + msg3)
    return msg4.int

def getSequence(msg):
    msg3 = msg.bin[32:64]
    msg4 = BitArray('0b' + msg3)
    return msg4.int

def getAckNumber(msg):
    msg3 = msg.bin[64:96]
    msg4 = BitArray('0b' + msg3)
    return msg4.int

def getWindow(msg):
    msg3 = msg.bin[112:128]
    msg4 = BitArray('0b' + msg3)
    return msg4.int

def getFlags(msg):
    msg3 = list(msg.bin[104:110])
    return msg3


# These Functions take a list of 6 ascii chars representing
# A six bit word
# isURGset(['1', '1', '0', '0', '0', '1'])
# msg is a list
def isURGset(msg):
        if msg[0] == '1':
                return True
        else:
                return False

def isACKset(msg):
        if msg[1] == '1':
                return True
        else:
                return False

def isRSTset(msg):
        if msg[3] == '1':
                return True
        else:
                return False

def isSYNset(msg):
        if msg[4] == '1':
                return True
        else:
                return False

def isFINset(msg):
        if msg[5] == '1':
                return True
        else:
                return False

def get_crc(data):
    md5_returned = hashlib.md5(data)
    sixteenbyte = md5_returned.digest()
    g = BitArray(sixteenbyte)
    crc = g.int % 65535
    return crc


def tcpHead(source, dest, seq, ack, check, data, urgent, options, URG, ACK, RST, SYN, FIN, window):
    msg = BitArray()
    msg.append('uint:16=' + str(source))
    msg.append('uint:16=' + str(dest))
    msg.append('uint:32=' + str(seq))
    msg.append('uint:32=' + str(ack))
    msg.append('uint:8=192') # Data Offset
    Flags = list('000000')
    if URG:
            Flags[0] = '1'
    if ACK:
            Flags[1] = '1'
    if RST:
            Flags[3] = '1'
    if SYN:
            Flags[4] = '1'
    if FIN:
            Flags[5] = '1'
    msg.append('0b' + FlagsToStr(Flags))
    msg.append('uint:18=' + str(window)) #Window
    msg.append('uint:16=' + str(check))
    msg.append('uint:16=' + str(urgent))
    msg.append('uint:24=' + str(options))
    msg.append('uint:8=0') #padding
    msg.append(data)
    return msg


















def FlagsToStr(str2):
    str3 = str2[0] + str2[1] + str2[2] + str2[3] + str2[4] + str2[5]
    return str3

# This function is here as a note to myself
def exampleOf_bitstring_to_bytesObject():
    print("")
    print("")
    fg = bytearray()
    print("Appending 127 to the fg bytearray()")
    fg.append(127)
    print(fg)
    print("")
    print("Appending another 127 to the fg bytearray()")
    fg.append(127)
    print(fg)
    print("")
    fg2 = BitArray()
    print("Converting fg to a bitstring")
    fg2.append(fg)
    print("Printing the new bitstring made from fg called fg2")
    print(fg2.bin)
    print("")
    print("Converting the bitstring back into a bytes object")
    print("Then comparing the original bytes object with the bytes object")
    print("Created from converting the bitstring back into bytes")
    fg3 = bitstring_to_bytes(fg2.bin)
    if fg == fg3:
        print("They are equal")
        print(fg)
        print(fg3)
        print("")


def fMain(theFile):
        #theFile = "1.jpg"
        if os.path.exists("Copy of " + theFile):
                os.remove("Copy of " + theFile)
                getFile(theFile)
                return
        else:
                getFile(theFile)


def getFile(filename):
        limit = 4
        datalen = 512
        strDataLen = str(datalen)
        with open(filename, 'rb') as file:
                ct = 0
                while 1:
                        
                        chunk = file.read(datalen)
                        bChunk = BitArray()
                        bChunk.append(chunk)
                        msg = tcpHead(5089,69,12,13,1,chunk, 0, 0, 1, 1, 1, 0, 1, 10)
                        
                        #print(isURGset(getFlags(msg)))
                        send = bitstring_to_bytes(msg.bin)
                        if ct < limit:
                                print("")
                                print("")
                                print("")
                                print(chunk)
                                #print(bChunk)
                                print(bitstring_to_bytes(bChunk.bin))
                        
                        writefile(send, filename, ct, limit)
                        if len(chunk) < datalen:
                                print(getSource(msg))
                                print(getDest(msg))
                                print(getSequence(msg))
                                print(getAckNumber(msg))
                                print(getWindow(msg))
                                testFlags = ['1', '1', '0', '1', '0', '1']
                                print(isURGset(testFlags))
                                print(isACKset(testFlags))
                                print(isRSTset(testFlags))
                                print(isSYNset(testFlags))
                                print(isFINset(testFlags))
                                break
                        ct += 1
                        
        file.close()
        return


def writefile(chunk, filename, ct, limit):
        fg = BitArray()
        fg.append(chunk)
        data = fg.bin[192:]
        byteData = bitstring_to_bytes(data)
        #if ct < limit:
               # continue
                #print(data)
                #print(byteData)
        f = open("Copy of " + filename, 'ab')
        f.write(byteData)
        f.close()
        return

#if len(sys.argv) > 1:
        #fMain(sys.argv[1])




