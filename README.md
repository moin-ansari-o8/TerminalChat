# TerminalChat
A Command line chat room using Terminal
<br>Author - Moin Ansari

## Overview

TerminalChat enables users to create a chat server using a command-line interface (CLI) and allows clients to join by connecting via a unique chatroom key. The server can handle multiple users, maintain chat history, and broadcast messages. Users can enter regular messages and emojis, and server administrators have control over kicking users, clearing the chat, or shutting down the server.

## Features

- **IPv6-based Chat Room**: Supports global IPv6 addresses for connecting users.
- **Multiple Clients**: Allows multiple users to join the chat using a generated key.
- **Message Broadcasting**: Sends messages from one user to all connected users.
- **Server Control**: The server admin can clear the chat, kick users out,etc.
- **Emoji Support**: Users can add emojis to their messages by pressing `*`.

## How to Run the Program

### Running the Server

1. Clone the repository.
2. Run the server program:
   ```bash
   python chat_server.py
   ```
3. Enter the server name and a valid port number.
4. The program will display a KEY TO CHATROOM (an encoded string).
5. Share this key with users to allow them to join the chatroom.

### Running the Client

1. Clone the repository.
2. Run the client program:
   ```bash
   python chat_user.py
   ```
3. Enter the KEY TO CHATROOM provided by the server.
4. Type messages and communicate with other users.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for new features, feel free to open an issue or submit a pull request.

## Contact

For any questions or feedback, please contact:

- **Email**: moin.edu01@gmail.com