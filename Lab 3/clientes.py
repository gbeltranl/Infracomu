# import socket programming library
import hashlib
import os
import socket
import time
# import thread module
from _thread import *
from multiprocessing.connection import wait
from threading import Event, Thread

port = 12346
BUFFER_SIZE = 1024 # send 1024 bytes each time step



# thread function
def clientOperation(event,socket,id,numClientes):
    md5 = hashlib.md5()
    
    file = open("ArchivosRecibidos/Cliente"+str(id)+"-Prueba"+str(numClientes), "wb")

    while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if '<SEP>'.encode() in bytes_read:
                received_hash = bytes_read.decode().split('<SEP>')[1]
                print("Received hash", received_hash) 
                
                break
            if not bytes_read:
                continue
            # write to the file the bytes we just received
            md5.update(bytes_read)
            file.write(bytes_read)
    file.close()
    print("[CLIENT {0}]:Received file's calculated hash: {1}".format(id,md5.hexdigest()))
    #s.close()

def MainClientThread(cv, numClientes):
    # local host IP '127.0.0.1'
    host = 'localhost'
 
    # Define the port on which you want to connect
    for x in range(1,numClientes +1):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 
        # connect to server on local computer
        s.connect((host,port))
        cliente = Thread(name=x , target= clientOperation, args=(cv,s,x,numClientes))
        cliente.start()
        #cliente.join()
    #s.close()
if __name__ == '__main__':
    cv = Event()
    numClientes = int(input("Ingrese el numero de clientes: (max 25)\n"))
    client = Thread(target=MainClientThread, args=(cv,numClientes))
    client.start()
