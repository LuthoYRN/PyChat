# Importing necessary modules
from socket import *
from threading import *
import os
import sys
from chat_aesthetics import *  # Importing custom module for chat aesthetics
from encryption import *  # Importing custom module for encryption
from tqdm import tqdm  # Importing tqdm for progress bar
from time import *  # Importing time module for timing operations

# Initializing server host and port
serverHost = ""  # Placeholder for server host
serverPort = 17280  # Default server port

# Global variables for synchronization and status tracking
accepting_req = False  # Flag to track if chat request is being accepted
ready_to_prompt = -1  # Flag to track readiness for user input
status = "Online"  # Default status for the client

lock = Lock()  # Lock for thread synchronization

# Function to clear terminal screen
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear') 

# Function to handle server responses
def handle_server_response(client_socket, response_message):
    global ready_to_prompt
    lock.acquire()  # Acquiring lock for thread safety
    ready_to_prompt = -1  # Resetting prompt flag
    # Handling different response scenarios
    if response_message.startswith("$L$"):
        # Processing list of connected clients
        if ":" in response_message:
            index = 1
            client_list = response_message[len("$L$"):].split(":")
            print("List of clients connected to server:")
            print("-" * 40)
            for client in client_list:
                if client!="":
                    client_addr = client.split("_")
                    print(f"{index}. IP Address: {client_addr[0]} Port: {client_addr[1]}")
                    index += 1
            ready_to_prompt = 1
        else:
            print("No other client has connected to the server yet...")
            ready_to_prompt = 1
    elif response_message.startswith("$C$"):
        # Processing list of available clients for connection
        if ":" in response_message:
            index = 1
            client_list = response_message[len("$C$"):].split(":")
            print("Clients available for connection:")
            print("-" * 40)
            for client in client_list:
                if client:
                    client_addr = client.split("_")
                    print(f"{index}. IP Address: {client_addr[0]} Port: {client_addr[1]}")
                    index += 1
            # Prompting user for client choice
            end_loop = False
            print()
            while not end_loop:
                client_choice = input("Enter the number of the client to connect to (or Q to cancel): ")
                if client_choice.upper() == 'Q':
                    print("Connection cancelled.")
                    ready_to_prompt = 1
                    end_loop = True
                elif client_choice.isdigit():
                    client_choice = int(client_choice)
                    if 1 <= client_choice <= (len(client_list)-1):
                        client_details = client_list[client_choice - 1].split("_")
                        client_socket.send(f"$CON${client_details[0]}_{client_details[1]}".encode())
                        end_loop = True
                        print("Waiting for requested client to accept/decline request...")
                    else:
                        print("Invalid client number. Please enter a valid number.")
                else:
                    print("Invalid input. Please enter a number or 'Q' to cancel.")
        else:
            print("No client is available to connect yet...")
            ready_to_prompt = 1
    elif response_message.startswith('$Y$'):
        # Handling acceptance of chat request
        print("Chat request accepted!")
        udp(50005)  # Initiating UDP chat
    elif response_message.startswith('$N$'):
        # Handling rejection of chat request
        print("(x) Chat request got rejected (x)")
        ready_to_prompt =  1
    elif response_message.startswith("$RCON$"): 
        # Handling chat request reception
        accept_chat_request(client_socket,response_message)
    else:
        # Handling unknown response
        print(f"Unknown response from server: {response_message}")
    lock.release()  # Releasing lock after processing response

# Function to accept chat request from another client
def accept_chat_request(client_socket,response_message):
    global accepting_req
    global ready_to_prompt
    accepting_req = True
    clear_terminal()  # Clearing terminal screen
    ip,port = response_message[len("$RCON$"):].split("_")
    print(f"Client IP: {ip} , Port: {port} wants to chat")
    print("Do you accept (Y) / decline(N) ?")
    decision=input(">").upper()
    if decision=='Y':
        client_socket.send(f"$Y${ip}_{port}".encode())
        udp(50006)  # Initiating UDP chat
    else:
        client_socket.send(f"$N${ip}_{port}".encode())
        accepting_req = False
        clear_terminal()
        ready_to_prompt=1

# Function to receive file from another client
def receive_file(ip,username):
    # Creating TCP socket for file transfer
    receiver_sock = socket(AF_INET, SOCK_STREAM)
    receiver_sock.bind((ip, 9999))
    receiver_sock.listen(1)
    print(f"Receiving file from {username}...")
    client, addr = receiver_sock.accept()
    # Receiving file name
    file_name = client.recv(1024).decode('utf-8', errors='ignore')
    # Receiving file size
    file_size = int(client.recv(1024).decode('utf-8', errors='ignore'))
    # Receiving file data
    with open(file_name, "wb") as file:
        received_size = 0
        # Displaying progress bar
        progress = tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=file_size, mininterval=0.1,leave=False)
        while received_size < file_size:
            data = client.recv(1024)
            if not data:
                break
            file.write(data)
            received_size += len(data)
            progress.update(len(data))
            sleep(0.01)  # Introducing delay for progress bar
    progress.close()
    client.send(b"complete")  # Sending completion signal
    print("File received successfully ✔")
    receiver_sock.close()
    client.close()

# Function to send file to another client
def send_file(receiver_ip,username):
    # Creating TCP socket for file transfer
    file_sock = socket(AF_INET,SOCK_STREAM)
    file_sock.connect((receiver_ip,9999))
    # Getting file path from user
    file_path = input("Enter filename > ")  
    # Sending file name and size
    file_sock.send(file_path.encode())
    file_size = str(os.path.getsize(file_path))
    file_sock.send(file_size.encode())
    with open(file_path, "rb") as file:
        # Reading and sending file data in chunks
        data = file.read()
        print(f"Sending file to {username}...")
    file_sock.sendall(data)
    # Closing socket
    data = file_sock.recv(1024).decode()
    if data=="complete":
        print("File sent ✔")
        file.close()
        file_sock.close()

# Function to handle UDP communication
def udp(port):
    clear_terminal()
    udp_server = (serverHost, 55555)  
    print('Connecting to UDP server...')
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print("Enter your username:\n")
    my_username = input("> ")
    sock.sendto(my_username.encode(), udp_server)
    while True:
        data = sock.recv(1024).decode()
        if data.strip() == 'ready':
            print('\nChecked in with server, waiting for peer...')
            break
    key = sock.recv(1024)
    data = sock.recv(1024).decode()
    username,ip, sport, dport = data.split(' ')
    sport = int(sport)
    dport = int(dport)
    sock.close()
    clear_terminal()
    centre(f"Connected to {username}!")
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto(encrypt_message('0',key), (ip, dport)) # Punch a hole
    centre('Ready to exchange messages')
    centre(GREY+"       Note: (1) To send a file type sendf (2) To exit chat, type X"+RESET)
    print("_"*terminal_size())  
    print()  
    # Creating sender and listener messaging sockets
    send_sock = socket(AF_INET, SOCK_DGRAM)
    listen_sock = socket(AF_INET, SOCK_DGRAM)
    # Functions used by message threads
    def send_messages(send_sock,key):        
        global ready_to_prompt
        try:
            chatActive = True
            send_sock.bind(("0.0.0.0" , sport+1))
            while chatActive:
                left()
                msg = input('')
                if msg.upper()=="X":  
                    # Check if user wants to exit
                    send_sock.sendto(encrypt_message("Exiting...",key), (ip, dport))  # Send exit signal to the peer
                    print("Exiting UDP chat...")
                    send_sock.sendto(encrypt_message("Exiting myself...",key), (gethostbyname(gethostname()), dport))  # Send exit to itself
                    send_sock.close()
                    clear_terminal()
                    chatActive=False
                    ready_to_prompt=1
                elif msg=="sendf":
                    send_sock.sendto(encrypt_message(f"sendf {ip}",key), (ip, dport))  # Send file request to peer   
                    try: 
                        send_file(ip,username)
                    except:
                        print("Could not send file, try again ❌\n")
                else:
                    msg=encrypt_message(msg,key)
                    send_sock.sendto(msg, (ip, dport))
        except error as e:
            pass
        except OSError as e:
            pass
        except Exception as e:
            print(e)

    def listen(listen_sock,send_sock,username,key):
        global ready_to_prompt
        try:
            chatActive=True
            listen_sock.bind(('0.0.0.0', dport))
            while chatActive:
                data = listen_sock.recv(1024)
                data = decrypt_message(data,key)
                if data!="0":
                    if (data==""):
                        print("\r"+BRIGHT_RED+"\nYou "+GREY+"> ",end="")
                    else:
                        if (data.startswith("sendf") and len(data.split(" "))==2):
                            try:
                                receive_file((data.split(" "))[1],username)
                            except:
                                print("File could not be received ❌")
                                send_sock.sendto(encrypt_message("",key), (gethostbyname(gethostname()), dport))
                        else:
                            if data=="Exiting myself...":
                                listen_sock.close()
                                chatActive = False
                            else:
                                right("{} < {}".format(data,username),"{}".format(data)," < ","{}".format(username))
                                if data=="Exiting...":
                                    send_sock.close()  
                                    listen_sock.close()
                                    clear_terminal()
                                    chatActive = False
                                    ready_to_prompt=1
                else:
                    continue
        except error as e:
            pass
        except OSError as e:
            pass
        except Exception as e:
            print(e)
  
    # Starting sender and listener threads
    listener = Thread(target=listen, args=(listen_sock,send_sock,username,key,),daemon=True).start()
    messenger = Thread(target=send_messages,args=(send_sock,key,),daemon=True).start()

# Function to send request to server
def request_from_server(command, client_socket):
    message = f"${command}$"      
    client_socket.send(message.encode())

# Function to listen to server responses
def listen_to_server(client_socket):
    while True:
        try:
            response_message = client_socket.recv(2048).decode()
            if response_message:
                handle_server_response(client_socket, response_message)
        except ConnectionResetError:
            pass
        except error:
            sys.exit(1)
        except Exception as e:
            print(f"Error occurred while handling server response: {e}") 
            break

# Function to prompt user for actions
def prompt(status):
    global ready_to_prompt
    print(RESET+"\nList of commands")
    print("-"*40)
    if status=="Online":
        print(BRIGHT_GREEN+f"<<{status}>>"+RESET)
    else:
        print(BRIGHT_RED+f"<<{status}>>"+RESET)
    print()
    print("1. List available clients")
    print("2. Connect to a client")
    print("3. Change active status")
    print("4. Exit")      
    ready_to_prompt =-1      

# Main function
def main():
    global ready_to_prompt
    global accepting_req
    global status
    global serverHost
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        print("Configuring server...")
        print("...")
        # Connecting to server
        while True:
            serverHost = input("Enter the server host : > ")
            try:
                serverPort = int(input("Enter the server port : > "))
                try: 
                    clientSocket.connect((serverHost, serverPort))
                    clear_terminal()
                    break
                except Exception:
                    print("Server not found, try again.")
                    print("...")
            except Exception:
                print("Invalid port number input, try again")
                print("...")
        
        print(f"Connected to server (host: {serverHost}, Port: {serverPort})") 
        Thread(target=listen_to_server, args=(clientSocket,)).start()  # Starting listener thread
        ready_to_prompt=1
        while True:
            lock.acquire()
            if (ready_to_prompt>0):
                lock.release()  
                prompt(status)
                action = input("\nEnter the number of the command: ")
                # Processing user commands
                if action == '1':
                    print("Please wait while updating the list of clients...")
                    request_from_server("L", clientSocket)
                elif action == '2':
                    if status!="Offline":
                        request_from_server("C", clientSocket)
                    else:
                        print("You cannot connect to another client while offline")
                        print("...")
                        ready_to_prompt = 1
                elif action =='3':
                    print("Choose active status\n(1) Online\n(2) Offline")
                    print("...")
                    while True:
                        status = input("Enter your choice: ")
                        if status=="1":
                            request_from_server("Stts",clientSocket)
                            status = "Online"
                            break
                        elif status=="2":
                            request_from_server("Stts",clientSocket)
                            status = "Offline"
                            break
                        else:
                            print("Invalid input. Please enter 1 or 2")
                            print("...")
                    ready_to_prompt=1
                elif action == '4':
                    print("Exiting...")
                    if status=="Online":
                        request_from_server("Stts",clientSocket)
                    request_from_server("E", clientSocket)
                    clientSocket.close()
                    break
                else:
                    if accepting_req:
                        print("Confirm response?")
                    else:
                        print("Invalid command. Please enter a valid command.")
                        ready_to_prompt=1
            else:
                lock.release() 
    except ConnectionResetError:
        print("Server offline")
        os.system("taskkill /f /pid %d > nul 2>&1" % os.getpid())
    except Exception as e:
        print(f"Error occurred: {e}")

# Entry point of the program
if __name__ == '__main__': 
    main()