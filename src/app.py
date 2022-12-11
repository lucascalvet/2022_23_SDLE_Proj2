import json
import sys
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server
from User import User

if __name__ == "__main__":
    import logging
    log = logging.getLogger('kademlia')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    '''
    # Check that a port was specified
    if len(sys.argv) < 4:
        print("Usage: python3 app.py <port> <private_key_file> <subscription_keys_file>")
        sys.exit(1)

    # Get the port from the command-line arguments and verify that it is numeric
    port = sys.argv[1]
    if not port.isnumeric():
        print("Error: the port number must be an integer")
        sys.exit(1)

    # Convert the port to an integer
    port = int(port)

    # Create a Server instance and listen on the specified port
    server = Server()
    '''

    '''
    # Create Loop to execute tasks
    loop = asyncio.get_event_loop()

    # Set the node's ID and address
    loop.create_task(server.bootstrap([("127.0.0.1", 5678)]))

    # Start the node
    loop.create_task(server.listen(5678))
    
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    # Load the user's private key
    private_key_file = sys.argv[2]
    with open(private_key_file, "rb") as f:
        user_private_key = load_pem_private_key(f.read(), password=None)

    with open(sys.argv[3]) as json_file:
        subscriptions = json.load(json_file)

    # Create the User
    user = User(user_private_key, server, subscriptions)

    # Have Alice create a post and subscribe to Bob
    alice_post = user.create_post("Hello, Bob!")

    # Have Bob create a post and subscribe to Alice
    bob_post = user.create_post("Hi, Alice!")

    # Print Alice's and Bob's timelines to show the posts from their subscriptions"
    loop.create_task(user.print_timeline())
    '''

    loop = asyncio.get_event_loop()

    alice = User(Ed25519PrivateKey.generate(), "127.0.0.1", 1233, 5001)

    bob = User(Ed25519PrivateKey.generate(), "127.0.0.2", 1234, 5002)

    loop.run_until_complete(alice.server.bootstrap([(bob.ip, 1234)]))

    loop.run_until_complete(alice.create_post("Hola soy Aliceee"))

    loop.run_until_complete(bob.subscribe(alice.public_key))

    loop.run_until_complete(bob.update_timeline())

    a = loop.run_until_complete(alice.server.get(alice.public_key))
    print("A")
    print(a)
    b = loop.run_until_complete(bob.server.get(bob.public_key))
    print("B")
    print(b)
    c = loop.run_until_complete(alice.server.get(bob.public_key))
    print("C")
    print(c)
    d = loop.run_until_complete(bob.server.get(alice.public_key))
    print("D")
    print(d)

    print(bob.posts)

