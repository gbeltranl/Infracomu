# import socket programming library
from multiprocessing.connection import wait
import socket
 
# import thread module
from _thread import *
from threading import Thread, Event
import time
import os
import hashlib

port = 12237
BUFFER_SIZE = 1024 # send 1024 bytes each time step


# thread function
def clientThread(cv,s,x,numClientes):
    md5 = hashlib.md5()
    cv.clear() # Set event state to 'False'
    cv.wait()
    f = open("Cliente"+str(x)+"-Prueba"+str(numClientes), "wb")

    while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = s.recv(BUFFER_SIZE)
            if not bytes_read:
                
                break
            # write to the file the bytes we just received
            md5.update(bytes_read)
            f.write(bytes_read)
    f.close()
    print("[CLIENT {0}]:Received file's calculated hash: {1}".format(x,md5.hexdigest()))
    s.send(b'ok')
    print("Sent confirmation")
    #s.close()
 


def handleClient(c, cv, filename):
    f = open(filename, "rb")
    md5 = hashlib.md5()
    cv.wait()
    
    #c.send(calculated_hash.encode())
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            print("Done Sending")
            break
        # we use sendall to assure transimission in 
        # busy networks
        md5.update(bytes_read)
        c.send(bytes_read) 
    calculated_hash = md5.hexdigest()
    print("File's hash", calculated_hash)
    #c.recv(1024)
print('confirmed')

def MainServerThread(cv,numArchivo,numClientes):
    # the name of file we want to send, make sure it exists
    # get the file size
    if numArchivo == 1:
        filename = "150"
    else:
        filename = "250"
    #filesize = os.path.getsize(filename)    
    
    host = ""

 
    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Servidor corriendo en puerto: ", port)
 
    # put the socket into listening mode
    s.listen(5)
    print("Socket escuchando")
 
    clientesConectados = 0
    while True:
        if clientesConectados < numClientes:
            # establish connection with client
            c, addr = s.accept()    
            # Start a new thread and return its identifier
            serverHandler = Thread(target=handleClient, args=(c,cv, filename))
            serverHandler.start()
            clientesConectados += 1
            #print(clientesConectados, " Clientes conectados")
        else:
            print(clientesConectados, " Clientes conectados")
            cv.set()
            break
    time.sleep(10)
    s.close()




def MainClientThread(cv, numClientes):
    # local host IP '127.0.0.1'
    host = 'localhost'
 
    # Define the port on which you want to connect
    for x in range(1,numClientes +1):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 
        # connect to server on local computer
        s.connect((host,port))
        cliente = Thread(name=x , target= clientThread, args=(cv,s,x,numClientes))
        cliente.start()
        #cliente.join()
    #s.close()

if __name__ == '__main__':
    cv = Event()
    numClientes = int(input("Ingrese el numero de clientes: (max 25)\n"))
    numArchivo = int(input("Que archivo desea usar:\n 1. 150 MB \n 2. 250 MB\n"))
    server = Thread(target=MainServerThread, args=(cv,numArchivo,numClientes))
    server.start()
    client = Thread(target=MainClientThread, args=(cv,numClientes))
    client.start()

    