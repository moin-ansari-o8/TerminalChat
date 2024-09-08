import socket
import threading
import sys
from time import sleep
import os

def getMainKey(key, offset=3):
    try:
        main_key = "".join(chr(ord(char) - offset) for char in key.split("#") if char)
        return main_key
    except Exception as e:
        print(f"Error decoding key: {e}")
        return ""

def clear_console():
    os.system('clear')

def handle_server_messages(user_socket):
    while True:
        try:
            message = user_socket.recv(1024).decode('utf-8')
            if message:
                if message == "SERVER SHUTDOWN":
                    print("..press enter to terminate program")
                    break
                else:
                    clear_console()
                    print(message+"\n\n")
            else:
                break
        except socket.error as e:
            break

    user_socket.close()

def main():
    key = input("ENTER KEY : ")
    user_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    user_socket.connect((getMainKey(key), 5555))

    threading.Thread(target=handle_server_messages, args=(user_socket,)).start()

    while True:
        try:
            message = input("Enter : ").strip()
            user_socket.send(message.encode('utf-8'))
            if message.lower() == "exit chat":
                break
        except socket.error as e:
            break

    user_socket.close()

if __name__ == "__main__":
    main()
