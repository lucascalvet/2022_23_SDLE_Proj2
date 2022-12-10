import json
import sys
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server
from .User import User

if __name__ == "__main__":
    import logging
    log = logging.getLogger('kademlia')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

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

    # Create Loop to execute tasks
    loop = asyncio.get_event_loop()

    # Set the node's ID and address
    loop.create_task(server.bootstrap([("127.0.0.1", 5678)]))
    #server.bootstrap([("127.0.0.1", 5678)])

    # Start the node
    loop.create_task(server.listen(5678))
    # server.listen(567
    
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
    """
    print("Alice's timeline:")
    for post in user.generate_timeline():
        print(f"- {post['text']}")
    print()

    print("Bob's timeline:")
    for post in user.generate_timeline():
        print(f"- {post['text']}")
    """
