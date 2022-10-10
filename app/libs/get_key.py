from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def get_private_key():
    with open('./jwt-key', 'rb') as key_file:
        secret_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend())
    return secret_key


def get_pub_key():
    with open('./jwt-key.pub', 'rb') as key_file:
        pub_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend())
    return pub_key