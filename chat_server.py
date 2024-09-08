import socket
import threading
import requests
import os

clients = {}
aliases = {}
client_last_pos = {}
server_running = True

def get_global_ipv6():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        response.raise_for_status()
        ipv6_address = response.json()['ip']
        return ipv6_address
    except requests.RequestException as e:
        print(f"Error fetching global IPv6 address: {e}")
        return None

def encode_ipv6(ipv6_address, offset=3):
    try:
        encoded_ip = "".join(chr(ord(char) + offset) + "#" for char in ipv6_address)
        return encoded_ip
    except Exception as e:
        print(f"Error encoding IPv6 address: {e}")
        return ""

def handle_client(client_socket, client_address):
    try:
        client_socket.send("Enter your name: ".encode('utf-8'))
        alias = client_socket.recv(1024).decode('utf-8').strip()
        aliases[client_socket] = alias
        client_last_pos[client_socket] = 0

        client_socket.send(f"\nWELCOME TO CHATBOX {alias}".encode('utf-8'))
        broadcast(f"'{alias}' joined the chat.", client_socket)
        
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8').strip()
                if not message:
                    break
                if message.lower() == "exit chat":
                    broadcast(f"'{alias}' has left the chat.")
                    break
                broadcast(f"'{alias}' : {message}")
            except socket.error as e:
                print("")
                break
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        remove_client(client_socket)

def broadcast(message, client_socket=None):
    print_message_to_console(message)

    with open("convo.txt", "a", encoding="utf-8") as file:
        file.write("\n" + message)

    with open("convo.txt", "r", encoding="utf-8") as file:
        chat_history = file.read().strip()

    to_remove = []
    for client in list(clients.keys()):
        if client != client_socket:
            try:
                client.send(chat_history.encode('utf-8'))
            except socket.error as e:
                print(f"Error broadcasting message to {aliases.get(client, 'Unknown')}: {e}")
                to_remove.append(client)

    for client in to_remove:
        remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        alias = aliases.get(client_socket, "Unknown")
        del clients[client_socket]
        del aliases[client_socket]
        del client_last_pos[client_socket]
    else:
        print(f"Error: Tried to remove a client that doesn't exist: {client_socket}")

def kickout_client(alias):
    client_socket = None
    for socket, client_alias in aliases.items():
        if client_alias == alias:
            client_socket = socket
            break

    if client_socket:
        try:
            client_socket.send("You have been kicked out by the server.".encode('utf-8'))
            client_socket.close()
            remove_client(client_socket)
            broadcast(f"{alias} has been kicked out by {server_name}.")
        except socket.error as e:
            print(f"Error kicking out client {alias}: {e}")
    else:
        print(f"Error: No client with name '{alias}' found.")

def print_message_to_console(message):
    os.system('clear')
    
    with open("convo.txt", "r", encoding="utf-8") as file:
        chat_history = file.read().strip()

    print(chat_history)
    print(f"{message}\n\n")

def server_send_messages():
    global server_running

    while server_running:
        try:
            message = input("Enter Message: ").strip()

            if message.startswith("remove "):
                to_remove = message[len("remove "):]
                kickout_client(to_remove)

            elif message == "clear chat":
                with open("convo.txt", "w") as file:
                    file.write("")
                print("Chat cleared.")

            elif message == "end chat":
                broadcast("Chat has been ended.")
                broadcast("SERVER SHUTDOWN")
                import time
                time.sleep(2)
                for client_socket in list(clients.keys()):
                    try:
                        client_socket.send("SERVER SHUTDOWN".encode('utf-8'))
                        client_socket.close()
                    except socket.error as e:
                        print(f"Error closing client socket: {e}")
                server_running = False
                server.close()
                break

            elif message == "list client":
                if clients:
                    print("Connected Clients:")
                    for client_socket, address in clients.items():
                        client_name = aliases.get(client_socket, "Unknown")
                        print(f"{client_name} : {address}")
                else:
                    print("No clients are currently connected.")

            elif message.strip():
                broadcast(f"'{server_name}' : {message}")

        except Exception as e:
            print(f"Error in server message handling: {e}")

def accept_connections():
    global server_running

    while server_running:
        try:
            client_socket, addr = server.accept()
            clients[client_socket] = addr
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_handler.start()

        except socket.error as e:
            if server_running:
                print(f"Error accepting connection: {e}")
            else:
                break

with open("convo.txt", "w") as file:
    file.write("")

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
try:
    server.bind(("::", 5555))
    server.listen(5)
except socket.error as e:
    print(f"Error setting up server socket: {e}")
    exit(1)

server_name = input("Enter server name: ")
global_ipv6 = get_global_ipv6()
if global_ipv6:
    encoded_ipv6 = encode_ipv6(global_ipv6)
    print("KEY TO CHATROOM : ", encoded_ipv6)
print("Chat room started...")

server_message_thread = threading.Thread(target=server_send_messages)
server_message_thread.start()

accept_connections()
