import socket
import threading
import sys
import os
import msvcrt

def getMainKey(key, offset=3):
    try:
        main_key = "".join(chr(ord(char) - offset) for char in key.split("#") if char)
        return main_key
    except Exception as e:
        print(f"Error decoding key: {e}")
        return ""

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear command for Windows/Linux

def handle_server_messages(client_socket, typed_message_ref):
    while True:
        try:
            # Receive chat history from server
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message == "SERVER SHUTDOWN":
                    print("\n\n..press enter to terminate program")
                    break
                else:
                    # Clear the console and display chat history
                    clear_console()
                    print(message)

                    # Re-display the currently typed message after chat update
                    print(f"Enter : {''.join(typed_message_ref)}", end='', flush=True)
            else:
                break
        except socket.error as e:
            break

    client_socket.close()

def main():
    key = input("ENTER KEY: ")
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.connect((getMainKey(key), 5555))  # Connect to the server

    # Keep track of the currently typed message
    typed_message = []

    # Start a thread to handle incoming messages from the server
    threading.Thread(target=handle_server_messages, args=(client_socket, typed_message)).start()

    # Main loop for typing and sending messages
    while True:
        try:
            while True:
                if msvcrt.kbhit():  # Check if a key has been pressed
                    char = msvcrt.getch()

                    try:
                        # Attempt to decode the character using utf-8
                        decoded_char = char.decode('utf-8')

                        if decoded_char == '\r':  # Enter key pressed
                            # Send the full message and clear the buffer
                            client_socket.send(''.join(typed_message).encode('utf-8'))
                            if ''.join(typed_message).lower() == "exit chat":
                                return
                            typed_message.clear()
                            print()  # Move to the next line after sending

                        elif decoded_char == '\x08':  # Backspace key pressed
                            if typed_message:
                                typed_message.pop()
                                # Clear and reprint the typed message
                                print(f"\rEnter : {''.join(typed_message)} ", end='', flush=True)

                        elif decoded_char == '*':  # '*' key pressed, handle emoji input
                            # Prompt the user to input an emoji or special character
                            emoji_input = input(":)")
                            # Append the emoji to the current typed message
                            typed_message.append(emoji_input)
                            # Reprint the typed message with the emoji included
                            print(f"\rConfirm : {''.join(typed_message)}", end='', flush=True)
                            if decoded_char == '\x08':  # Backspace key pressed
                                if typed_message:
                                    typed_message.pop()
                                    # Clear and reprint the typed message
                                    print(f"\rEnter : {''.join(typed_message)} ", end='', flush=True)


                        else:
                            # Add the typed character and reprint
                            typed_message.append(decoded_char)
                            print(f"\rEnter : {''.join(typed_message)}", end='', flush=True)

                    except UnicodeDecodeError:
                        # Handle special keys that can't be decoded (like arrow keys)
                        pass

        except socket.error as e:
            print(f"Error sending message: {e}")
            break

    client_socket.close()

if __name__ == "__main__":
    main()
