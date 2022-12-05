import time
import json
import sys
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server


class User:
    def __init__(self, private_key, server, subscriptions = []):
        self.private_key = private_key
        self.server = server
        self.subscriptions = subscriptions
        self.posts = []

        # Extract the public key from the private key
        self.public_key = self.private_key.public_key()

    async def create_post(self, text):
        """Creates a new post with the given text, signed with the user's private key."""
        # Create the post with a timestamp and an empty signature
        post = {
            "text": text,
            "timestamp": time.time(),
            "author": self.public_key,
            "signature": None,
        }

        # Sign the message with the post's timestamp
        message = f"{post['text']}:{post['timestamp']}"
        post["signature"] = self.sign_post(message)

        self.posts.append(post)

        # Store the post on the network
        """TODO: post is a dict and the set function is expecting a bool, int, float, str etc... -> Maybe serialize"""
        await self.server.set(self.public_key, post)

        return post

    def sign_post(self, text):
        """Signs the given text with the user's private key."""
        # Sign the text using the user's private key
        signature = self.private_key.sign(text)
        return signature

    def verify_signature(self, post):
        """Verifies the signature of the given post using the author's public key."""
        # Get the author's public key from the post
        author_public_key = post["author"]

        # Verify the signature using the author's public key
        message = f"{post['text']}:{post['timestamp']}"
        return author_public_key.verify(post["signature"], message)

    async def generate_timeline(self):
        """Returns a list of posts from the user's subscriptions, ordered by timestamp."""
        # Query the network for posts from each of the user's subscriptions
        timeline = []

        # TODO: get the public key for each subscription
        for subscription in self.subscriptions:
            posts = await self.server.get(subscription)

            # Filter out any posts with invalid signatures
            verified_posts = [
                post for post in posts if self.verify_signature(post)
            ]

            # Add the verified posts to the timeline
            timeline.extend(verified_posts)

        # Sort the timeline by the timestamp of each post
        timeline.sort(key=lambda post: post["timestamp"])

        return timeline

    async def print_timeline(self):
        """Prints the posts in the user's timeline"""
        timeline = await self.generate_timeline()
        for post in timeline:
            print(f"- {post['text']}")


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
    server = Server(port)

    # Create Loop to execute tasks
    loop = asyncio.get_event_loop()

    # Set the node's ID and address
    loop.create_task(server.bootstrap([("127.0.0.1", 5678)]))
    #server.bootstrap([("127.0.0.1", 5678)])

    # Start the node
    loop.create_task(server.listen(5678))
    #server.listen(5678)

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
    loop.create_task(alice.print_timeline())
    loop.create_task(bob.print_timeline())
    """
    print("Alice's timeline:")
    for post in user.generate_timeline():
        print(f"- {post['text']}")
    print()

    print("Bob's timeline:")
    for post in user.generate_timeline():
        print(f"- {post['text']}")
    """
