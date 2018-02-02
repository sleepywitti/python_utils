"""
.. module:: SSHCrypto
   :synopsis: helpers for SSH cryptography

.. moduleauthor:: C. Witt <cwitt@posteo.de>

- provided SSH key generation
- providedes simple encryption using part of the private SSH key as key
    uses characters from ssh key to generate salt and initialization vector
    uses AES to encrypt the plain text using key/iv from ssh key
    and returns encrypted byte string to readable string using b64 encoding

.. warning::

    might be a bad way to do it and it can be imprived by using
    encrypted_bytes = Crypto.RSA.importKey(open(key_path).read()).encrypt(plain_string)
"""

import os
import base64
from typing import Tuple

__author__ = "C. Witt"
__copyright__ = "Copyright (C) 2014-2018 C. Witt"


def generate_keys(private_key_path: str, public_key_path: str, comment: str= '', key_size: int=2048) -> None:
    """ creates a new SSH key pair using either Crypto or cryptography

    :param private_key_path: path for private key
    :param public_key_path:  path for public key
    :param comment: path for key size
    :param key_size:
    :raises: ModuleNotFoundError, RuntimeError
    """
    try:
        from cryptography.hazmat.primitives import serialization as crypto_serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend as crypto_default_backend

        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=key_size
        )
        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption())
        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )
    except ModuleNotFoundError:
        import Crypto.PublicKey.RSA  # used for generating ssh key

        key = Crypto.PublicKey.RSA.generate(key_size)
        private_key = key.exportKey('PEM')
        public_key = key.publickey().exportKey('OpenSSH')

    if not private_key or not public_key:
        raise RuntimeError('Keys are empty')

    if len(comment) > 0:
        public_key += b' ' + comment.encode()

    for name, path, key, mod in [('private', private_key_path, private_key, 0o0600),
                                 ('public', public_key_path, public_key), 0o0644]:
        key_dir = os.path.dirname(path)
        if not os.path.isdir(key_dir):
            os.mkdir(key_dir)
        with open(path, 'wb') as file:
            file.write(key)

        os.chmod(path, mod)


def get_key_and_iv(key_path: str, key_length: int=16) -> Tuple[str, str]:
    """ reads key and initialization vector from ssh key

    :param key_path: path to key file
    :param key_length: length of key
    :returns: key and initialization vector
    """
    assert key_length in [16, 24, 32]
    with open(key_path) as ssh_file:
        # skip the first line
        ssh_file.readline()
        # use 24 characters from key and transform them to 16 bytes
        key = base64.b64decode(ssh_file.readline()[:64])[:key_length]
        iv = base64.b64decode(ssh_file.readline()[:24])[:16]
        return key, iv


def encode_with_ssh_key(key_path: str, plain_string: str) -> str:
    """ encrypts a plain string using some data from key file

    :param key_path: path to key file
    :param plain_string: text that has to be encrypted
    :return: encrypted text
    """
    key, iv = get_key_and_iv(key_path)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted_bytes = encryptor.update(plain_string.encode()) + encryptor.finalize()
    except ModuleNotFoundError:
        import Crypto.PublicKey.RSA  # used for generating ssh key
        import Crypto.Cipher.AES

        cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CFB, iv)
        encrypted_bytes = cipher.encrypt(plain_string.encode())

    return base64.b64encode(encrypted_bytes).decode()


def decode_with_ssh_key(key_path: str, encoded_string: str) -> str:
    """ decrypts a plain string using some data from key file

    :param key_path: path to key file
    :param encoded_string: text that has to be decrypted
    :return: decrypted text
    """
    key, iv = get_key_and_iv(key_path)
    encrypted_bytes = base64.b64decode(encoded_string)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()
    except ModuleNotFoundError:
        import Crypto.PublicKey.RSA  # used for generating ssh key
        import Crypto.Cipher.AES

        cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CFB, iv)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)

    return decrypted_bytes.decode()
