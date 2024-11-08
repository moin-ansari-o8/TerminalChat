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
2. Run the main program to start the server:
   ```bash
   python main.py
   ```
3. Select the server option by entering 1.
4. Enter a unique server name and specify a valid port number.
5. A KEY TO CHATROOM will be generated and displayed. Share this key with clients to allow them to join.

### Running the Client

1. Clone the repository.
2. Run the main program to start the client:
   ```bash
   python main.py
   ```
3. Select the client option by entering 2.
4. Enter the KEY TO CHATROOM provided by the server admin.
5. Type messages and communicate with other users.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for new features, feel free to open an issue or submit a pull request.

## Contact

For any questions or feedback, please contact:

- **Email**: moin.edu01@gmail.com
- **LinkedIn**: [Moin Ansari](https://www.linkedin.com/in/moin-ansari1817/)