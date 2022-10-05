import hashlib
import socket
from threading import Event, Thread
import datetime
import os

port = 12345
BUFFER_SIZE = 2048  # Send 2048 bytes each time step
# Create the log file name
name_log = str(datetime.datetime.now()).replace(' ', '').replace(':', '-').split('.')[0]
name_log += '-log.txt'
# Create the log file
log_file = open('./Logs/' + name_log, 'w')

# Thread function
def clientOperation(socket, id, numClientes):
    received_hash = ''
    # Instantiate the MD5 algorithm for hashing the files
    md5 = hashlib.md5()
    filename ="Cliente" + str(id) + "-Prueba" + str(numClientes) + ".txt"
    filepath = "./ArchivosRecibidos/Cliente" + str(id) + "-Prueba" + str(numClientes) + '.txt'
    # Create the file that is going to be transferred
    file = open(filepath, "wb")
    # Send confirmation to server that is ready to receive the file
    socket.send(str(socket.getsockname()[1]).encode())
    print('Data transfer initiated for client:', socket.getsockname(),'\n-------------------------------------')
    start_time = datetime.datetime.now().timestamp()
    end_time = datetime.datetime.now().timestamp()
    while True:
        # Read 2048 bytes from the socket (receive)
        bytes_read = socket.recv(BUFFER_SIZE)
        # Asks if the separator is in the bytes read
        if '<SEP>'.encode() in bytes_read:
            # Separates the hashcode from the bytes read
            end_time = datetime.datetime.now().timestamp()
            received_hash = bytes_read.decode().split('<SEP>')[1]
            break
        # Waits for the server to send the bytes
        if not bytes_read:
            continue
        # Update the MD5 with bytes read to complete hash
        md5.update(bytes_read)
        # Write to the file the bytes we just received
        file.write(bytes_read)
    file.close()
    print("[CLIENT {0}]: Received file's calculated hash: {1}".format(socket.getsockname(), md5.hexdigest()))
    print('[CLIENT {0}]: Hash from server: {1}'.format(socket.getsockname(), received_hash))
    print('[CLIENT {0}]: Integrity of data is:'.format(socket.getsockname()), received_hash == md5.hexdigest(),'\n-------------------------------------')
    filesize = os.path.getsize(filepath)
    log_file.write('The file is ({0}) selected for the test and it is: {1}\n'.format(filename, filesize/1000000))
    log_file.write('Connected client: ' + str(socket.getsockname()) + '\n')
    log_file.write('Client ' + str(socket.getsockname()) + ' transmission has successfully ended.' + '\n')
    log_file.write('The file received on Client ' + str(socket.getsockname()) + 'took: ' + str((end_time - start_time)) + ' ms.' + '\n')
    socket.close()


def MainClientThread(numClientes):
    host = 'localhost'
    # Instantiate N Threads for the number of clients selected
    for x in range(1, numClientes + 1):
        # Instantiate a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect socket to the server on localhost
        s.connect((host, port))
        # Create the client
        cliente = Thread(name = x, target = clientOperation, args = (s, x, numClientes))
        # Starts the client process
        cliente.start()


if __name__ == '__main__':
    # Asks for the number of clients required for the transfer
    numClientes = int(input("Ingrese el numero de clientes: (max 25)\n"))
    os.system('clear')
    # Instantiate a Superior Thread
    client = Thread(target=MainClientThread, args = (numClientes,))
    # Starts the thread to MainClientThread function
    client.start()