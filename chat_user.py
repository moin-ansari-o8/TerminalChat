import socket
import threading
import sys
import os
import msvcrt
import base64
import json

def getMainKey(encoded_data: str) -> (str, int): #type:ignore
    decoded_json = base64.b64decode(encoded_data).decode()
    data = json.loads(decoded_json)
    return data['ip'], data['port']

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_server_messages(client_socket, typed_message_ref):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message == "SERVER SHUTDOWN":
                    print("\n\n..press enter to terminate program")
                    break
                else:
                    clear_console()
                    print(message)
                    print(f"\nEnter : {''.join(typed_message_ref)}", end='', flush=True)
            else:
                break
        except socket.error as e:
            break
    client_socket.close()

def main():
    pasw = input("ENTER KEY: ")
    key,way=getMainKey(pasw)
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.connect((key,way))
    typed_message = []
    threading.Thread(target=handle_server_messages, args=(client_socket, typed_message)).start()
    while True:
        try:
            while True:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    try:
                        decoded_char = char.decode('utf-8')
                        if decoded_char == '\r':
                            client_socket.send(''.join(typed_message).encode('utf-8'))
                            if ''.join(typed_message).lower() == "exit chat":
                                return
                            typed_message.clear()
                            print()
                        elif decoded_char == '\x08':
                            if typed_message:
                                typed_message.pop()
                                print(f"\rEnter : {''.join(typed_message)} ", end='', flush=True)
                        elif decoded_char == '*':
                            emoji_input = input(":)")
                            typed_message.append(emoji_input)
                            print(f"\n\rConfirm : {''.join(typed_message)}", end='', flush=True)
                        else:
                            typed_message.append(decoded_char)
                            print(f"\rEnter : {''.join(typed_message)}", end='', flush=True)
                    except UnicodeDecodeError:
                        pass
        except socket.error as e:
            print(f"Error sending message: {e}")
            break
    client_socket.close()

if __name__ == "__main__":
    main()
