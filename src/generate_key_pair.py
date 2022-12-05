from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import sys

key = Ed25519PrivateKey.generate()

pem_private = key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())

pem_public = key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

with open(sys.argv[1], 'wb') as pem_private_out:
    pem_private_out.write(pem_private)

with open(sys.argv[2], 'wb') as pem_public_out:
    pem_public_out.write(pem_public)