# import socket programming library
import hashlib
import os
import socket
import time
# import thread module
from _thread import *
from multiprocessing.connection import wait
from threading import Event, Thread

port = 12236
BUFFER_SIZE = 1024 # send 1024 bytes each time step


# thread function
def clientOperation(event,socket,id,numClientes):
    md5 = hashlib.md5()
    event.clear() # Set event state to 'False'
    event.wait()
    file = open("Cliente"+str(id)+"-Prueba"+str(numClientes), "wb")

    while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if '<SEP>'.encode() in bytes_read:
                received_hash = bytes_read.decode().split('<SEP>')[1]
                print("Received hash", received_hash) 
                
                break
            if not bytes_read:
                
                break
            # write to the file the bytes we just received
            md5.update(bytes_read)
            file.write(bytes_read)
    file.close()
    print("[CLIENT {0}]:Received file's calculated hash: {1}".format(id,md5.hexdigest()))
    socket.send(b'ok')
    print("Sent confirmation")
    #s.close()
 


def serverOperation(connection, event, filename):
    file = open(filename, "rb")
    md5 = hashlib.md5()
    event.wait()
    
    #c.send(calculated_hash.encode())
    while True:
        # read the bytes from the file
        bytes_read = file.read(BUFFER_SIZE)
        if not bytes_read:
            print("Done Sending")
            break
        # we use sendall to assure transimission in 
        # busy networks
        md5.update(bytes_read)
        connection.send(bytes_read) 
    calculated_hash = md5.hexdigest()
    print("File's hash", calculated_hash)
    connection.send('<SEP>'.encode())
    connection.send(calculated_hash.encode())
print('confirmed')

def MainServerThread(event,numArchivo,numClientes):
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
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.bind((host, port))
    print("Servidor corriendo en puerto: ", port)
 
    # put the socket into listening mode
    socketClient.listen(5)
    print("Socket escuchando")
 
    clientesConectados = 0
    while True:
        if clientesConectados < numClientes:
            # establish connection with client
            connection, addr = socketClient.accept()    
            # Start a new thread and return its identifier
            serverHandler = Thread(target=serverOperation, args=(connection, event, filename))
            serverHandler.start()
            clientesConectados += 1
            #print(clientesConectados, " Clientes conectados")
        else:
            print(clientesConectados, " Clientes conectados")
            event.set()
            break
    time.sleep(10)
    socketClient.close()




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
    numArchivo = int(input("Que archivo desea usar:\n 1. 150 MB \n 2. 250 MB\n"))
    server = Thread(target=MainServerThread, args=(cv,numArchivo,numClientes))
    server.start()
    client = Thread(target=MainClientThread, args=(cv,numClientes))
    client.start()

    