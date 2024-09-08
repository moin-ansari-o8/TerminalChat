import socket
import threading
import requests
import os

users = {}
aliases = {}
user_last_pos = {}
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

def handle_user(user_socket, user_address):
    try:
        user_socket.send("Enter your name: ".encode('utf-8'))
        alias = user_socket.recv(1024).decode('utf-8').strip()
        aliases[user_socket] = alias
        user_last_pos[user_socket] = 0

        user_socket.send(f"\nWELCOME TO CHATBOX {alias}".encode('utf-8'))
        broadcast(f"'{alias}' joined the chat.", user_socket)
        
        while True:
            try:
                message = user_socket.recv(1024).decode('utf-8').strip()
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
        print(f"Error handling user {user_address}: {e}")
    finally:
        user_socket.close()
        remove_user(user_socket)

def broadcast(message, user_socket=None):
    print_message_to_console(message)

    with open("convo.txt", "a", encoding="utf-8") as file:
        file.write("\n" + message)

    with open("convo.txt", "r", encoding="utf-8") as file:
        chat_history = file.read().strip()

    to_remove = []
    for user in list(users.keys()):
        if user != user_socket:
            try:
                user.send(chat_history.encode('utf-8'))
            except socket.error as e:
                print(f"Error broadcasting message to {aliases.get(user, 'Unknown')}: {e}")
                to_remove.append(user)

    for user in to_remove:
        remove_user(user)

def remove_user(user_socket):
    if user_socket in users:
        alias = aliases.get(user_socket, "Unknown")
        del users[user_socket]
        del aliases[user_socket]
        del user_last_pos[user_socket]
    else:
        print(f"Error: Tried to remove a user that doesn't exist: {user_socket}")

def kickout_user(alias):
    user_socket = None
    for socket, user_alias in aliases.items():
        if user_alias == alias:
            user_socket = socket
            break

    if user_socket:
        try:
            user_socket.send("You have been kicked out by the server.".encode('utf-8'))
            user_socket.close()
            remove_user(user_socket)
            broadcast(f"{alias} has been kicked out by {server_name}.")
        except socket.error as e:
            print(f"Error kicking out user {alias}: {e}")
    else:
        print(f"Error: No user with name '{alias}' found.")

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
                kickout_user(to_remove)

            elif message == "clear chat":
                with open("convo.txt", "w") as file:
                    file.write("")
                print("Chat cleared.")

            elif message == "end chat":
                broadcast("Chat has been ended.")
                broadcast("SERVER SHUTDOWN")
                import time
                time.sleep(2)
                for user_socket in list(users.keys()):
                    try:
                        user_socket.send("SERVER SHUTDOWN".encode('utf-8'))
                        user_socket.close()
                    except socket.error as e:
                        print(f"Error closing user socket: {e}")
                server_running = False
                server.close()
                break

            elif message == "list user":
                if users:
                    print("Connected users:")
                    for user_socket, address in users.items():
                        user_name = aliases.get(user_socket, "Unknown")
                        print(f"{user_name} : {address}")
                else:
                    print("No users are currently connected.")

            elif message.strip():
                broadcast(f"'{server_name}' : {message}")

        except Exception as e:
            print(f"Error in server message handling: {e}")

def accept_connections():
    global server_running

    while server_running:
        try:
            user_socket, addr = server.accept()
            users[user_socket] = addr
            print(f"Accepted connection from {addr}")
            user_handler = threading.Thread(target=handle_user, args=(user_socket, addr))
            user_handler.start()

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
