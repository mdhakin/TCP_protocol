import threading
import time
from bitstring import BitArray, BitStream
import os
import sys
import FormatMsg
import socket
import tcpMain
import state

def main():
    listen()
    return


def listen():
    # Set server port and ipaddress values
    UDP_IP_ADDRESS = sys.argv[1]
    UDP_PORT_NO = int(sys.argv[2])

    # Init the server socket
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((UDP_IP_ADDRESS,UDP_PORT_NO))

    # Instance of the main program
    conn = tcpMain.Tcp_Main(UDP_PORT_NO,UDP_IP_ADDRESS,"conn", serverSock)
    conn.start()
    conn.join()
    
    # close the connection
    serverSock.close()
    return


# Main entry point for the server
main()