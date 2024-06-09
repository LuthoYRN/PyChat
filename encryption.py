from cryptography.fernet import Fernet  # Import Fernet for encryption

# Function to generate encryption key
def generate_key():
    return Fernet.generate_key()

# Function to encrypt a message
def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(message.encode())
    return cipher_text

# Function to decrypt an encrypted message
def decrypt_message(cipher_text, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text).decode()
    return plain_text