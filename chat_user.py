import socket
import threading
from time import sleep

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
            else:
                break
        except socket.error as e:
            print(f"Socket error while receiving message: {e}")
            break
        except Exception as e:
            print(f"Unexpected error in receive_messages: {e}")
            break

def send_messages(client_socket):
    while True:
        try:
            message = input()
            if message.lower() == "exit chat":
                client_socket.send(message.encode('utf-8'))
                sleep(5)  # Wait for the server to process exit message
                client_socket.close()
                break
            client_socket.send(message.encode('utf-8'))
        except socket.error as e:
            print(f"Socket error while sending message: {e}")
            break
        except Exception as e:
            print(f"Unexpected error in send_messages: {e}")
            break

def getMainKey(key, offset=3):
    try:
        main_key = "".join(chr(ord(char) - offset) for char in key.split("#") if char)
        return main_key
    except Exception as e:
        print(f"Error decoding key: {e}")
        return ""

try:
    key = input("ENTER KEY : ")
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client.connect((getMainKey(key), 5555))
    
    recv_thread = threading.Thread(target=receive_messages, args=(client,))
    recv_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()
except socket.error as e:
    print(f"Socket error while connecting to server: {e}")
except Exception as e:
    print(f"Unexpected error in client setup: {e}")
