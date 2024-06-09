# 🌐 PyChat: Encrypted Peer-to-Peer Chat Application 🌐

Welcome to **PyChat**, a robust and secure peer-to-peer chat application designed for encrypted communication and file sharing. Leveraging TCP and UDP protocols, this application ensures your conversations and file transfers are private and secure, using state-of-the-art encryption techniques.

## 🚀 Features

- **End-to-End Encryption**: All messages and file transfers are encrypted using the `cryptography` library.
- **Peer-to-Peer Communication**: Direct UDP connections for efficient and fast message exchange.
- **File Transfer**: Securely send and receive files between clients.
- **Dynamic Client Management**: List, connect, and manage clients dynamically.
- **User-Friendly Interface**: Enhanced terminal interface with colorful prompts and aligned messages implemented in `chat_aesthetics.py`.

## 📦 Installation

To get started with PyChat, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/LuthoYRN/pychat.git
    cd pychat
    ```
2. Navigate to the project directory:
    ```bash
    cd pychat
    ```
3. **Install Required Packages**:
    Make sure you have Python installed. Then, install the required packages:
    ```bash
    pip install cryptography tqdm
    ```

## 🛠️ Usage

### Running the Server

Start the server to handle multiple client connections:
```bash
python server.py
```

### Running the Client

Once the server is up, start the client on multiple PCs to connect and chat:
```bash
python client.py
```
Connect to the server on port 17280 and use the server's ip address

## Features ✨

- **List Clients**: View all connected clients.
- **Connect to Client**: Initiate a chat session with a specific client.
- **Change Status**: Toggle your availability status.
- **Send Messages**: Chat securely with other clients.
- **File Transfer**: Send and receive files securely.

## 🗝️ Encryption Module

PyChat uses the `encryption.py` module for its encryption needs.

## 📂 Project Structure

```
PyChat/
├── client.py
├── server.py
├── chat_aesthetics.py
├── encryption.py
└── README.md
```
## 🌟 Acknowledgements

- **Cryptography**: For providing robust encryption.
- **TQDM**: For progress bars during file transfers.
