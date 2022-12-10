import time
import json
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server
from .Receiver import Receiver


class User:
    async def __init__(self, private_key, ip, kademlia_port, receiver_port, subscriptions=[], subscribers=[]):
        # Event loop for io operations
        self.loop = asyncio.get_event_loop()

        self.private_key = private_key
        self.ip = ip
        self.receiver_port = receiver_port
        self.server = Server()
        self.receiver = Receiver(self)
        self.subscriptions = subscriptions
        self.subscribers = subscribers
        self.posts = []

        self.loop.run_until_complete(self.server.listen(kademlia_port))

        # Extract the public key from the private key
        self.public_key = self.private_key.public_key()
        await self.server.set(self.public_key, json.dumps(self.info))

    async def update_dht(self):
        await self.server.set(self.public_key, json.dumps(self.get_dht_info()))

    def get_dht_info(self):
        return {
            "ip": self.ip,
            "port": self.receiver_port,
            "subscribers": self.subscribers,
            "last_post_id": self.last_post_id
        }

    async def create_post(self, text):
        """Creates a new post with the given text, signed with the user's private key."""
        self.info["id_last_post"] += 1
        # Create the post with a timestamp and an empty signature
        post = {
            "id": self.info["id_last_post"],
            "text": text,
            "timestamp": time.time(),
            "author": self.public_key,
            "signature": None,
        }

        # Sign the message with the post's timestamp
        message = f"{post['text']}:{post['timestamp']}"
        post["signature"] = self.sign(message)

        self.posts.append(post)
        await self.update_dht()

        return post

    def sign(self, text):
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

    async def write_message(self, ip, port, message):
        try:
            _, writer = await asyncio.open_connection(ip, port)
            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False

    async def send_to_peer(self, public_key, message):
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        if self.write_message(peer_info["ip"], peer_info["port"], message):
            return (0, "Message sent")
        else:
            return (-1, "Message not sent", peer_info)

    def send_message(self, public_key, message):
        return asyncio.run_coroutine_threadsafe(self.send_to_peer(public_key, message), loop=self.loop)

    def add_subscription(self, public_key):
        self.subscriptions.append(public_key)
    
    async def add_subscription_to_dht(self, public_key):
        self.subscriptions.append(public_key)

    async def subscribe(self, public_key):
        message = {
            "op": "subscribe",
            "user": self.public_key,
        }
        message["signature"] = self.sign(f"{message['op']}:{message['user']}")
        direct_ans = self.send_message(public_key, message)
        if direct_ans[0]:
            self.add_subscription(public_key)
            return "Successfully subscribed"
        elif direct_ans[0] == -1:
            peer_subscribers = direct_ans[2]["subscribers"]
            for sub in peer_subscribers:
                sub_ans = await self.request_posts(sub, public_key, 0)
                if sub_ans[0]:
                    return "Got posts from other subscribers"
        return "Didn't subscribe"

    def unsubscribe(self, public_key):
        message = {
            "op": "unsubscribe",
            "user": self.public_key,
        }
        return self.send_message(public_key, message)

    def request_posts(self, public_key, target_public_key, first_post=0):
        message = {
            "op": "request posts",
            "user": self.public_key,
            "target": target_public_key,
            "first_post": first_post,
        }
        return self.send_message(public_key, message)


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
