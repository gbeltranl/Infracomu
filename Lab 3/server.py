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
clientesConectados = 0

def serverOperation(connection, event, filename):
    file = open(filename, "rb")
    md5 = hashlib.md5()

    # Receive ok from client
    print("suma clientes")
    global clientesConectados
    clientesConectados +=1
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
 
    global clientesConectados
    while True:
        print(clientesConectados)
        if clientesConectados < numClientes:
            # establish connection with client
            connection, addr = socketClient.accept()    
            # Start a new thread and return its identifier
            if connection:
                print("New connection")
                serverHandler = Thread(target=serverOperation, args=(connection, event, filename))
                serverHandler.start()
            #clientesConectados es modificado dentro de cada thread para esperar la confirmacion del cliente
            #clientesConectados += 1
            #print(clientesConectados, " Clientes conectados")
        else:
            print(clientesConectados, " Clientes conectados")
            event.set()
            break
    time.sleep(10)
    socketClient.close()

if __name__ == '__main__':
    cv = Event()
    numClientes = int(input("Ingrese el numero de clientes: (max 25)\n"))
    numArchivo = int(input("Que archivo desea usar:\n 1. 150 MB \n 2. 250 MB\n"))
    server = Thread(target=MainServerThread, args=(cv,numArchivo,numClientes))
    server.start()