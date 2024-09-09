import socket
import threading
import msvcrt
import requests
import os

users = {}
aliases = {}
user_last_pos = {}
server_running = True
chat_history = []

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

        user_socket.send(f"\nWELCOME TO CHATBOX {alias}\nNote:To enter Emoji press '*'\n".encode('utf-8'))
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
    # Add the message to the chat history
    chat_history.append(message)
    
    print_message_to_console(message)

    # Send the chat history to all users except the sender
    to_remove = []
    for user in list(users.keys()):
        if user != user_socket:
            try:
                user.send("\n".join(chat_history).encode('utf-8'))
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
    # Clear the console (Unix/Linux-based systems)
    os.system('clear')

    # Print the chat history in the console
    print("\n".join(chat_history))
    print(f"{message}\n\n")

def server_send_messages():
    global server_running
    typed_message = []  # Track the message being typed

    while server_running:
        try:
            # Clear the console and print chat history
            print_message_to_console(''.join(typed_message))  # Display the current input message

            while True:
                if msvcrt.kbhit():
                    char = msvcrt.getch()

                    try:
                        decoded_char = char.decode('utf-8')

                        if decoded_char == '\r':  # Enter key pressed
                            message = ''.join(typed_message).strip()
                            if message:
                                if message.startswith("remove "):
                                    kickout_user(message[len("remove "):])
                                elif message == "clear chat":
                                    chat_history.clear()
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
                                    return
                                elif message == "list user":
                                    if users:
                                        print("Connected users:")
                                        for user_socket, address in users.items():
                                            user_name = aliases.get(user_socket, "Unknown")
                                            print(f"{user_name} : {address}")
                                    else:
                                        print("No users are currently connected.")
                                else:
                                    broadcast(f"'{server_name}' : {message}")

                            typed_message.clear()
                            break

                        elif decoded_char == '\x08':  # Backspace key pressed
                            if typed_message:
                                typed_message.pop()
                                print(f"\rEnter : {''.join(typed_message)}", end='', flush=True)

                        elif decoded_char == '*':  # Emoji input
                            emoji_input = input(":)")
                            typed_message.append(emoji_input)
                            print(f"\rConfirm : {''.join(typed_message)}", end='', flush=True)

                        else:
                            typed_message.append(decoded_char)
                            print(f"\rEnter : {''.join(typed_message)}", end='', flush=True)

                    except UnicodeDecodeError:
                        pass

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

# Initialize chat history as a list
chat_history.clear()

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
