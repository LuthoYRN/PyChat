from socket import *  # Import necessary socket modules
from threading import *  # Import threading module for concurrent execution
from encryption import *  # Import encryption module for secure communication

# Initialize server host and ports
serverHost = gethostbyname(gethostname()) 
serverPort = 17280
udp_port = 55555
CLIENT_LIMIT = 10

conClients = []  # List to store connected clients
client_statuses = []  # List to store status of each client

# Function to list all connected clients
def list_clients(client_socket):
    active_clients_info = "$L$"
    for x in conClients:
        if (x[0]!=client_socket):
            active_clients_info += f"{x[1][0]}_{x[1][1]}:"
    client_socket.send(active_clients_info.encode())

# Function to list available clients for connection
def list_available_clients(client_socket):
    active_clients_info = "$C$"
    i=0
    for x in conClients:
        if (x[0]!=client_socket) and (client_statuses[i]=="ON"):
            active_clients_info += f"{x[1][0]}_{x[1][1]}:"
        i+=1
    client_socket.send(active_clients_info.encode())

# Function to handle various client requests
def handle_client_request(client_socket, request_message):
    if request_message.startswith("$L$"):
        list_clients(client_socket)
    elif request_message.startswith("$Stts$"):
        changeStatus(client_socket)
    elif request_message.startswith("$C$"):
        list_available_clients(client_socket)
    elif request_message.startswith("$CON$"):
        forward_chat_request(client_socket,request_message)
    elif request_message.startswith("$Y$"):
        inform_client("$Y$",request_message)
        connect_clients()  
    elif request_message.startswith("$N$"):
        inform_client("$N$",request_message)
    elif request_message.startswith("$E$"):
        print("Client disconnected:", client_socket.getpeername())
        conClients.remove((client_socket, client_socket.getpeername()))
        ip,port = client_socket.getpeername()
        i=0
        for x in conClients:
            if (x[1][0]==ip) and (x[1][1]==port):
                break
            i+=1
        client_statuses.pop(i)
    
    else:
        print(f"Unknown request from client: {request_message}")

# Function to listen to client messages
def listen_to_client(client_socket):
    while True:
        try:
            request_message = client_socket.recv(2048).decode()
            if request_message:
                handle_client_request(client_socket, request_message)
        except ConnectionResetError:
            pass
        except Exception as e:
            print(f"Error occurred while handling client request: {e}")
            break

# Function to change client status
def changeStatus(client_socket):
    ip,port = client_socket.getpeername()
    i=0
    for x in conClients:
        if (x[1][0]==ip) and (x[1][1]==port):
            if client_statuses[i]=="ON":
                client_statuses[i]="OF"
            else:
                client_statuses[i]="ON"
        i+=1

# Function to inform clients about chat request response
def inform_client(command,request_message):
    request_message=request_message[3:] #$con$ip_port
    client = request_message.split("_")
    client_ip = client[0]
    client_port = int(client[1])
    for x in conClients:
            if (x[1][0]==client_ip) and (x[1][1]==client_port):
                x[0].send(command.encode())
                break

# Function to forward chat request to a client
def forward_chat_request(client_socket,request_message):
    ip,port = client_socket.getpeername()
    message = "$RCON${}_{}".format(ip,port)
    request_message=request_message[5:] #$con$ip_port
    client_B = request_message.split("_")
    clientB_ip = client_B[0]
    clientB_port = int(client_B[1])
    for x in conClients:
            if (x[1][0]==clientB_ip) and (x[1][1]==clientB_port):
                x[0].send(message.encode())
                break

# Function to establish UDP connection between two clients
def connect_clients():
    done=False
    key=generate_key()
    print("Setting up UDP connection for 2 clients")
    known_port = 50002 #used for messaging
    udp_socket = socket(AF_INET, SOCK_DGRAM) 
    udp_socket.bind(("0.0.0.0", 55555))
    while not done:
        clients = []
        while True:
            data, address = udp_socket.recvfrom(128)
            print('connection from: {}'.format(address))
            clients.append((data,address))
            udp_socket.sendto(b'ready', address)
            udp_socket.sendto(key, address)
            if len(clients) == 2:
                print('got 2 clients, sending details to each')
                break
        c1 = clients.pop()
        c1_name = c1[0].decode("utf-8")
        c1_addr, c1_port = c1[1]
        c2 = clients.pop()
        c2_name = c2[0].decode("utf-8")
        c2_addr, c2_port = c2[1]
        udp_socket.sendto('{} {} {} {}'.format(c1_name,c1_addr, c1_port, known_port).encode(), c2[1])
        udp_socket.sendto('{} {} {} {}'.format(c2_name,c2_addr, c2_port, known_port).encode(), c1[1])
        udp_socket.close()
        done=True
        break

# Function to handle incoming client connections
def client_handler(client_socket, client_address):
    conClients.append((client_socket, client_address)) #tuple
    client_statuses.append("ON")
    Thread(target=listen_to_client, args=(client_socket,)).start()

# Main function to run the server
def main():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    try:
        serverSocket.bind((serverHost, serverPort))
        print(f"Running server on IP {serverHost}, port: {serverPort}")
    except:
        print(f"Unable to bind to host {serverHost} and port {serverPort}")
    serverSocket.listen(CLIENT_LIMIT)
    while True:
        connectionSocket, addr = serverSocket.accept()
        print(f"Successfully connected to client (host: {addr[0]}, port: {addr[1]})")
        Thread(target=client_handler, args=(connectionSocket, addr)).start()

# Entry point of the program
if __name__ == '__main__':
    main()