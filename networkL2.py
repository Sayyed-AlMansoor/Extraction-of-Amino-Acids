import socket
import time
# Port Number
PORT_NUMBER = 3600  #Sayyed and Abhishek
#Host IP Address
HOST_IP = "127.0.0.1"
print("Server Started!!!!")
#Creating socket descriptor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind((HOST_IP, PORT_NUMBER)) # Binding host ip address and port number
    serverSocket.listen() # Listening to the queue which has connection requests from various clients
    clientDescriptor, clientAddress = serverSocket.accept() # Accepting the client request based on FIFO method
    print(f"listening at {PORT_NUMBER} port")
    with clientDescriptor:
        clientDescriptor.settimeout(15) # Setting timeout to 15 seconds
    print(f"CLient Address {clientAddress} has been connected")
    ipDeet = f"IP and PORT_NUMBER: {clientAddress}"
    clientDescriptor.sendall(ipDeet.encode())
    while True:
        inputDataFromClient = clientDescriptor.recv(1024) #Receiving input data from client
        if not str(inputDataFromClient.decode()):
            continue
        decodedInputData = str(inputDataFromClient.decode()) #Decoding input data received from client
        print(f"Command received from client is {decodedInputData}")
# If the input command is TIME, then returing the current time
        if "TIME" in decodedInputData:
            serverResponse = str(time.ctime())
# If the input command is EXIT, then closing the client connection
        elif "EXIT" in decodedInputData:
            serverResponse = "Server is closing all open sockets (including wekcome sockets)"
            clientDescriptor.sendall(serverResponse.encode())
            break
#For invalid input command
        else:
            serverResponse = "Invalid command"
        clientDescriptor.sendall(serverResponse.encode())
    clientDescriptor.close()
print("Server has been shutdown")