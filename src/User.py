import time
import json
import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from kademlia.network import Server
from .Receiver import Receiver


class User:
    def __init__(self, private_key, ip, kademlia_port, receiver_port, subscriptions=[], subscribers=[]):
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
        # TODO: Check DHT 

    async def update_dht(self):
        await self.server.set(self.public_key, json.dumps(self.get_dht_info()))

    def get_dht_info(self):
        return {
            "ip": self.ip,
            "port": self.receiver_port,
            "subscriptions": self.subscriptions,
            "subscribers": self.subscribers,
            "last_post_id": self.last_post_id,
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

    def verify_signature(self, public_key, signature, content):
        return public_key.verify(signature, content)

    def verify_post_signature(self, post):
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
        peer_info = json.loads(peer_info)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        if self.write_message(peer_info["ip"], peer_info["port"], message):
            return (0, "Message sent", peer_info)
        else:
            return (-1, "Message not sent", peer_info)

    def add_subscriber(self, public_key):
        self.subscribers.append(public_key)
        
    def remove_subscriber(self, public_key):
        self.subscribers.append(public_key)

    def add_subscription(self, public_key):
        self.subscriptions.append(public_key)
        
    def remove_subscription(self, public_key):
        self.subscriptions.remove(public_key)
    
    async def add_subscription_to_foreign_dht(self, public_key):
        peer_info = await self.server.get(public_key)
        peer_info = json.loads(peer_info)
        peer_info["subscribers"].append(self.public_key)
        await self.server.set(public_key, json.dumps(peer_info))
        
    async def remove_subscription_from_foreign_dht(self, public_key):
        peer_info = await self.server.get(public_key)
        peer_info = json.loads(peer_info)
        peer_info["subscribers"].remove(self.public_key)
        await self.server.set(public_key, json.dumps(peer_info))

    async def subscribe(self, public_key):
        message = {
            "op": "subscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            "signature": None,
        }
        message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        direct_ans = await self.send_to_peer(public_key, message)
        # Target doesn't exist
        if direct_ans[0] == -2:
            return "Didn't subscribe. Public Key unknown"
        # Target exists
        else:
            self.add_subscription(public_key)
            await self.add_subscription_to_foreign_dht(public_key)
            
            # Target is offline
            if direct_ans[0] == -1:
                peer_subscribers = direct_ans[2]["subscribers"]
                for sub in peer_subscribers:
                    sub_ans = await self.request_posts(sub, public_key, 0)
                    if sub_ans[0]:
                        return "Subscribed and got posts from other subscribers"
                return "Subscribed but didn't get posts from other subscribers"
            
            # Target is online
            return "Successfully subscribed and got posts directly from target"
            
    async def unsubscribe(self, public_key):
        message = {
            "op": "unsubscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            "signature": None,
        }
        message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return "Didn't unsubscribe. Public Key unknown"
        else:
            self.remove_subscription(public_key)
            await self.remove_subscription_from_foreign_dht(public_key)
            if ans[0]:
                return "Unsubscribed and warned target"
            return "Unsubscribed but didn't warn target"

    async def request_posts(self, public_key, target_public_key, first_post=0):
        message = {
            "op": "request posts",
            "sender": self.public_key,
            "target": target_public_key,
            "first_post": first_post,
            "timestamp": time.time(),
            "signature": None,
        }
        message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['target']}:{message['first_post']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return "Didn't request posts. Public Key unknown"
        elif ans[0] == 0:
            return "Requested posts"
        else:
            return "Didn't request posts. User offline"

    async def send_posts(self, public_key, target_public_key, first_post=0):
        message = {
            "op": "send posts",
            "sender": self.public_key,
            "posts": [post for post in self.posts if post["author"] == target_public_key and post["id"] >= first_post],
            "timestamp": time.time(),
            "signature": None,
        }
        message["signature"] = self.sign(f"{message['op']}:{message['user']}:{message['posts']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return "Didn't send posts. Public Key unknown"
        elif ans[0] == 0:
            return "Sent posts"
        else:
            return "Didn't send posts. User offline"

    def receive_posts(self, posts):
        for post in posts:
            if self.verify_signature(post):
                self.posts.append(post)

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
