import socket
import threading
import sys
import os

if os.name == "nt":  # For Windows
    import msvcrt

    def getch():
        return msvcrt.getch()

else:  # For Linux/Termux
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


import requests
import base64
import json

# serverside codes
users = {}
aliases = {}
user_last_pos = {}
server_running = True
chat_history = []
MAX_HISTORY_SIZE = 100


def get_global_ipv6():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        response.raise_for_status()
        ipv6_address = response.json()["ip"]
        return ipv6_address
    except requests.RequestException as e:
        print(f"Error fetching global IPv6 address: {e}")
        return None


def get_valid_way():
    while True:
        try:
            valid_way = int(input("Enter Port: "))
            if 0 <= valid_way <= 65535:
                return valid_way
            else:
                print("Port number must be between 0 and 65535.")
        except ValueError:
            print("Invalid input. Please enter a valid integer for the port.")


def handle_user(user_socket, user_address):
    try:
        user_socket.send("Enter your name: ".encode("utf-8"))
        alias = user_socket.recv(1024).decode("utf-8").strip()
        aliases[user_socket] = alias
        user_last_pos[user_socket] = 0
        user_socket.send(
            f"\nWELCOME TO CHATBOX {alias}\nNote: To enter Emoji press '*'\n".encode(
                "utf-8"
            )
        )
        broadcast(f"'{alias}' joined the chat.", user_socket)
        while True:
            try:
                message = user_socket.recv(1024).decode("utf-8").strip()
                if not message:
                    break
                if message.lower() == "exit chat":
                    broadcast(f"'{alias}' has left the chat.")
                    break
                broadcast(f"'{alias}' : {message}")
            except socket.error as e:
                print(f"Error receiving message from {user_address}: {e}")
                break
    except Exception as e:
        print(f"Error handling user {user_address}: {e}")
    finally:
        user_socket.close()
        remove_user(user_socket)


def broadcast(message, user_socket=None):
    if len(chat_history) >= MAX_HISTORY_SIZE:
        chat_history.pop(0)
    chat_history.append(message)
    print_message_to_console(message)
    to_remove = []
    for user in list(users.keys()):
        if user != user_socket:
            try:
                user.send("\n".join(chat_history).encode("utf-8"))
            except socket.error as e:
                print(
                    f"Error broadcasting message to {aliases.get(user, 'Unknown')}: {e}"
                )
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
            user_socket.send("You have been kicked out by the server.".encode("utf-8"))
            user_socket.close()
            remove_user(user_socket)
            broadcast(f"{alias} has been kicked out by {server_name}.")
        except socket.error as e:
            print(f"Error kicking out user {alias}: {e}")
    else:
        print(f"Error: No user with name '{alias}' found.")


def print_message_to_console(message):
    os.system("cls" if os.name == "nt" else "clear")
    print("\n".join(chat_history) + "\n")


def server_send_messages():
    global server_running
    typed_message = []
    while server_running:
        try:
            print_message_to_console("".join(typed_message))
            while True:
                if os.name == "nt" and msvcrt.kbhit():
                    char = getch()
                    try:
                        decoded_char = char.decode("utf-8")
                        if decoded_char == "\r":
                            message = "".join(typed_message).strip()
                            if message:
                                if message.startswith("remove "):
                                    kickout_user(message[len("remove ") :])
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
                                            user_socket.send(
                                                "SERVER SHUTDOWN".encode("utf-8")
                                            )
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
                                            user_name = aliases.get(
                                                user_socket, "Unknown"
                                            )
                                            print(f"{user_name} : {address}")
                                            import time

                                            time.sleep(3)
                                    else:
                                        print("No users are currently connected.")
                                else:
                                    broadcast(f"'{server_name}' : {message}")
                            typed_message.clear()
                            break
                        elif decoded_char == "\x08":
                            if typed_message:
                                typed_message.pop()
                                print(
                                    f"\rEnter : {''.join(typed_message)}",
                                    end="",
                                    flush=True,
                                )
                        elif decoded_char == "*":
                            emoji_input = input(":)")
                            typed_message.append(emoji_input)
                            print(
                                f"\rConfirm : {''.join(typed_message)}",
                                end="",
                                flush=True,
                            )
                        else:
                            typed_message.append(decoded_char)
                            print(
                                f"\rEnter : {''.join(typed_message)}",
                                end="",
                                flush=True,
                            )
                    except UnicodeDecodeError:
                        pass
        except Exception as e:
            print(f"Error in server message handling: {e}")


def accept_connections():
    global server_running
    ct = 1
    while server_running:
        try:
            user_socket, addr = server.accept()
            users[user_socket] = addr
            print(f"Accepted connection from {addr}")
            user_handler = threading.Thread(
                target=handle_user, args=(user_socket, addr)
            )
            user_handler.start()
            if ct == 1:
                server_message_thread = threading.Thread(target=server_send_messages)
                server_message_thread.start()
                ct = 0
        except socket.error as e:
            if server_running:
                print(f"Error accepting connection: {e}")
            else:
                break


def encode(x: str, y: int) -> str:
    data = {"ip": x, "port": y}
    json_str = json.dumps(data)
    encoded_data = base64.b64encode(json_str.encode()).decode()
    return encoded_data


# user side codes
def getMainKey(encoded_data: str) -> (str, int):  # type:ignore
    decoded_json = base64.b64decode(encoded_data).decode()
    data = json.loads(decoded_json)
    return data["ip"], data["port"]


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def handle_server_messages(client_socket, typed_message_ref):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message == "SERVER SHUTDOWN":
                    print("\n\n..press enter to terminate program")
                    break
                else:
                    clear_console()
                    print(message)
                    print(f"\nEnter : {''.join(typed_message_ref)}", end="", flush=True)
            else:
                break
        except socket.error as e:
            break
    client_socket.close()


if __name__ == "__main__":
    print("\nWho are you?")
    print("1.Server")
    print("2.User")
    print("0.Exit")
    n = int(input("\nEnter Index Number: "))
    match n:
        case 1:
            server_name = input("Enter Server Name: ")
            port = get_valid_way()
            server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            try:
                server.bind(("::", port))
                server.listen(5)
            except socket.error as e:
                print(f"Error setting up server socket: {e}")
                exit(1)
            global_ipv6 = get_global_ipv6()
            if global_ipv6:
                encoded_ipv6 = encode(global_ipv6, port)
                print("KEY TO CHATROOM : ", encoded_ipv6)
            print("Chat room started...")
            accept_connections()
        case 2:
            pasw = input("ENTER KEY: ")
            key, way = getMainKey(pasw)
            client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            client_socket.connect((key, way))
            typed_message = []
            threading.Thread(
                target=handle_server_messages, args=(client_socket, typed_message)
            ).start()
            while True:
                try:
                    while True:
                        if os.name == "nt" and msvcrt.kbhit():
                            char = getch()
                            try:
                                decoded_char = char.decode("utf-8")
                                if decoded_char == "\r":
                                    client_socket.send(
                                        "".join(typed_message).encode("utf-8")
                                    )
                                    if "".join(typed_message).lower() == "exit chat":
                                        break
                                    typed_message.clear()
                                    print()
                                elif decoded_char == "\x08":
                                    if typed_message:
                                        typed_message.pop()
                                        print(
                                            f"\rEnter : {''.join(typed_message)} ",
                                            end="",
                                            flush=True,
                                        )
                                elif decoded_char == "*":
                                    emoji_input = input(":)")
                                    typed_message.append(emoji_input)
                                    print(
                                        f"\n\rConfirm : {''.join(typed_message)}",
                                        end="",
                                        flush=True,
                                    )
                                else:
                                    typed_message.append(decoded_char)
                                    print(
                                        f"\rEnter : {''.join(typed_message)}",
                                        end="",
                                        flush=True,
                                    )
                            except UnicodeDecodeError:
                                pass
                except socket.error as e:
                    print(f"Error sending message: {e}")
                    break
            client_socket.close()
        case 0:
            print("Exiting...")
        case _:
            print("no valid input")
