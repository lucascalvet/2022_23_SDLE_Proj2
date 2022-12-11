import json
import sys
import asyncio
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server
from User import User

if __name__ == "__main__":
    '''
    import logging
    log = logging.getLogger('kademlia')
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    '''

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

    alice = User(Ed25519PrivateKey.generate(), "127.0.0.1", 1233, 5007, persistence_file="alice_vieira.json")

    bob = User(Ed25519PrivateKey.generate(), "127.0.0.2", 1234, 5002, [("127.0.0.1", 1233)], persistence_file="bob_vance.json")

    print("ALICE KEY:" + str(alice.public_key))
    print("BOB KEY:" + str(bob.public_key))

    print("ALICE POSTS:" + str(alice.posts))

    alice.loop.run_until_complete(alice.create_post("Hola soy Aliceee"))
    
    alice.loop.run_until_complete(alice.create_post("Ou em tuga: Olá sou a Aliceee"))
        
    print("ALICE POSTS2:" + str(alice.posts))

    print("BOB POSTS:" + str(bob.posts))
    
    print("ALICE SUBSCRIB:" + str(alice.subscribers))

    print("BOB SUBSCRIP:" + str(bob.subscriptions))

    bob.loop.run_until_complete(bob.subscribe(alice.public_key))
            
    print("ALICE SUBSCRIB2:" + str(alice.subscribers))
    
    print("BOB SUBSCRIP2:" + str(bob.subscriptions))
    
    print("BOB POSTS2:" + str(bob.posts))
    
    alice.loop.run_until_complete(alice.create_post("No teu país das maravilhas"))
        
    print("ALICE POSTS3:" + str(alice.posts))

    #bob.loop.run_until_complete(bob.update_timeline())
    
    #bob.loop.run_until_complete(bob.update_timeline())
    
    print("BOB POSTS3:" + str(bob.posts))
    
    #bob.loop.run_until_complete(bob.unsubscribe(alice.public_key))
        
    print("ALICE SUBSCRIB3:" + str(alice.subscribers))
    
    print("BOB SUBSCRIP3:" + str(bob.subscriptions))
    
    alice.loop.run_until_complete(alice.create_post("Beijo na bunda"))
    
    print("ALICE POSTS4:" + str(alice.posts))
    
    print("BOB POSTS4:" + str(bob.posts))
        
    #bob.loop.run_until_complete(bob.update_timeline())
    
    #print("BOB POSTS5:" + str(bob.posts))
