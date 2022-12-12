from User import User
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import logging
log = logging.getLogger('kademlia')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

with open("keys/bootstrap", "rb") as f:
    user_private_key = load_pem_private_key(f.read(), password=None)

user = User(user_private_key, "127.0.0.1", 6000, 6001)

while True:
    dummy = True
