import time
import json
import asyncio
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from kademlia.network import Server
from Receiver import Receiver


class User:
    def __init__(self, private_key, ip, kademlia_port, receiver_port, bootstrap_nodes=[], subscriptions=[], subscribers=[]):
        # Event loop for io operations
        self.loop = asyncio.get_event_loop()

        self.private_key = private_key
        self.ip = ip
        self.receiver_port = receiver_port
        self.server = Server()
        self.receiver = Receiver(self)
        self.subscriptions = subscriptions
        self.subscribers = subscribers
        self.last_post_id = -1
        self.posts = {}

        self.loop.run_until_complete(self.server.listen(kademlia_port))
        self.loop.run_until_complete(self.server.bootstrap([(self.ip, kademlia_port)]))
        for node in bootstrap_nodes:
            self.loop.run_until_complete(self.server.bootstrap([(node[0], node[1])]))

        # Extract the public key from the private key
        self.public_key = self.serialize_key(self.private_key.public_key())
        
        # Update state using the data on the DHT
        dht_info = self.loop.run_until_complete(self.server.get(self.public_key))
        if dht_info != None:
            dht_info = json.loads(dht_info)
            self.subscribers = dht_info["subscribers"]
        else:
            self.loop.run_until_complete(self.update_dht())
        
        self.loop.run_until_complete(self.update_timeline())

        self.receiver.daemon = True
        self.receiver.start()

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
    
    def serialize_key(self, public_key):
        return public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    
    def deserialize_key(self, public_key):
        try:
            return serialization.load_pem_public_key(public_key.encode('utf-8'))
        except Exception as e:
            print("Deserialize Exception " + str(e))

    async def create_post(self, text):
        """Creates a new post with the given text, signed with the user's private key."""
        self.last_post_id += 1
        # Create the post with a timestamp and an empty signature
        post = {
                self.last_post_id:
                {
                    "text": text,
                    "timestamp": time.time(),
                    "signature": None,
                }
            }
        
        # Sign the message with the post's timestamp
        message = f"{post[self.last_post_id]['text']}:{post[self.last_post_id]['timestamp']}"
        post[self.last_post_id]["signature"] = base64.b64encode(self.sign(message)).decode('utf-8')

        if self.public_key in self.posts.keys():
            self.posts[self.public_key].update(post)
        else:
            self.posts[self.public_key] = post
        await self.update_dht()

        return post

    def sign(self, text):
        """Signs the given text with the user's private key."""
        # Sign the text using the user's private key
        signature = self.private_key.sign(text.encode('utf-8'))
        return signature

    def verify_signature(self, public_key, signature, content):
        public_key = self.deserialize_key(public_key)
        return public_key.verify(signature, content)

    def verify_post_signature(self, author_key, post):
        """Verifies the signature of the given post using the author's public key."""

        # Verify the signature using the author's public key
        message = f"{post['text']}:{post['timestamp']}"
        author_key = self.deserialize_key(author_key)
        try:
            result = author_key.verify(base64.b64decode(post["signature"].encode('utf-8')), message.encode('utf-8'))
            return result == None
        except Exception as e:
            print("Verification Exception " + str(e))
            return False
        return 

    async def write_message(self, ip, port, message):
        try:
            _, writer = await asyncio.open_connection(ip, port)
            message = json.dumps(message)
            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            print("Write Exception " + str(e) + " in message " + str(message))
            return False

    async def send_to_peer(self, public_key, message):
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        if await self.write_message(peer_info["ip"], peer_info["port"], message):
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
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        peer_info["subscribers"].append(self.public_key)
        await self.server.set(self.public_key, json.dumps(peer_info))
        return (0, "Added subscription to DHT with success")

    async def remove_subscription_from_foreign_dht(self, public_key):
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        peer_info["subscribers"].remove(self.public_key)
        await self.server.set(self.public_key, json.dumps(peer_info))
        return (0, "Removed subscription from DHT with success")

    async def subscribe(self, public_key):
        message = {
            "op": "subscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            #"signature": None,
        }
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        print("DEBUG_INSIDE_SUB_DEST:" + str(public_key))
        direct_ans = await self.send_to_peer(public_key, message)
        # Target doesn't exist
        if direct_ans[0] == -2:
            return (-2, "Didn't subscribe. Public Key unknown")
        # Target exists
        else:
            self.add_subscription(public_key)
            await self.add_subscription_to_foreign_dht(public_key)

            # Target is offline
            if direct_ans[0] == -1:
                peer_subscribers = direct_ans[2]["subscribers"]
                for sub in peer_subscribers:
                    if sub != self.public_key:
                        sub_ans = await self.request_posts(sub, public_key, 0)
                        if sub_ans[0]:
                            return (1, "Subscribed and got posts from other subscribers")
                return (-1, "Subscribed but didn't get posts from other subscribers")

            # Target is online
            return (0, "Successfully subscribed and got posts directly from target")

    async def unsubscribe(self, public_key):
        message = {
            "op": "unsubscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            #"signature": None,
        }
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't unsubscribe. Public Key unknown")
        else:
            self.remove_subscription(public_key)
            await self.remove_subscription_from_foreign_dht(public_key)
            if ans[0]:
                return (0, "Unsubscribed and warned target")
            return (-1, "Unsubscribed but didn't warn target")

    async def find_posts(self, target_public_key, first_post=0):
        direct_ans = await self.request_posts(target_public_key, target_public_key, first_post)
        if direct_ans[0] == -1:
            target_info = await self.server.get(target_public_key)
            if target_info == None:
                return (-2, "Didn't request posts. Target Public Key unknown")
            target_info = json.loads(target_info)
            for sub in target_info["subscribers"]:
                if sub != self.public_key:
                    sub_ans = await self.request_posts(sub, target_public_key, first_post)
                    if sub_ans[0]:
                        return (1, "Requested posts to other subscribers")
            return (-1, "Didn't request posts. Neither target nor subscribers were available")
        else:
            return direct_ans
        
    async def request_posts(self, public_key, target_public_key, first_post=0):
        message = {
            "op": "request posts",
            "sender": self.public_key,
            "target": target_public_key,
            "first_post": first_post,
            "timestamp": time.time(),
            #"signature": None,
        }
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['target']}:{message['first_post']}:{message['timestamp']}")
        if await self.server.get(target_public_key) == None:
            return (-3, "Didn't request posts. Target Public Key unknown")
        print("DEBUG_INSIDE_REQ_DEST:" + str(public_key))
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't request posts. Interlocutor Public Key unknown")
        elif ans[0] == 0:
            return (0, "Requested posts")
        else:
            return (-1, "Didn't request posts. User offline")

    async def send_posts(self, public_key, target_public_key, first_post=0):
        if target_public_key not in self.posts.keys():
            return (-3, "Didn't send posts. Didn't have any ;(")
     
        try:
            posts_to_send = {key: self.posts[target_public_key][key] for key in self.posts[target_public_key] if key >= first_post}
            posts_to_send = json.dumps(posts_to_send)
        except Exception as e:
            print("JSON Exception " + str(e))
     
        message = {
            "op": "send posts",
            "sender": self.public_key,
            "author": target_public_key,
            "first_id": first_post,
            "posts": posts_to_send,
            "timestamp": time.time(),
            #"signature": None,
        }
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['author']}:{message['first_id']}:{message['posts']}:{message['timestamp']}")
        print("DEBUG_INSIDE_SEND_DEST:" + str(public_key))
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't send posts. Public Key unknown")
        elif ans[0] == 0:
            return (0, "Sent posts")
        else:
            return (-1, "Didn't send posts. User offline")

    def receive_posts(self, author_key, posts):
        print("DEBUG_INSIDE_REC_SELF:" + str(self.public_key))
        for item in posts.items():
            if self.verify_post_signature(author_key, item[1]):
                if author_key in self.posts.keys():
                    if item[0] not in self.posts[author_key].keys():
                        self.posts[author_key].update({int(item[0]): item[1]})
                else:
                    self.posts[author_key]= {int(item[0]): item[1]}
                
    async def send_sync(self, public_key):
        message = {
            "op": "sync",
            "last_post_id": self.last_post_id,
            "sender": self.public_key,
            "timestamp": time.time(),
            #"signature": None,
        }
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't unsubscribe. Public Key unknown")
        else:
            self.remove_subscription(public_key)
            await self.remove_subscription_from_foreign_dht(public_key)
            if ans[0]:
                return (0, "Unsubscribed and warned target")
            return (-1, "Unsubscribed but didn't warn target")
        
    async def update_timeline(self):
        for public_key in self.subscriptions:
            if public_key in self.posts and len(self.posts[public_key]) > 0:
                post_latest_id = int(max(self.posts[public_key].keys()))
                print("D1:" + str(public_key) + ":" + str(post_latest_id + 1))
                await self.find_posts(public_key, post_latest_id + 1)
            else:
                print("D2:" + str(public_key))
                await self.find_posts(public_key, 0)
        return self.posts
