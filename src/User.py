import time
import json
import asyncio
import base64
import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from kademlia.network import Server
from Receiver import Receiver


class User:
    def __init__(self, private_key, ip, kademlia_port, receiver_port, bootstrap_nodes=[], persistence_file="data.json"):
        """User class constructor"""
        # Event loop for io operations
        self.loop = asyncio.get_event_loop()

        self.private_key = private_key
        self.ip = ip
        self.receiver_port = receiver_port
        self.server = Server()
        self.receiver = Receiver(self)
        self.subscriptions = []
        self.subscribers = []
        self.last_post_id = -1
        self.posts = {}
        self.persistence_file = persistence_file

        self.load_local_info()

        self.loop.run_until_complete(self.server.listen(kademlia_port))
        self.loop.run_until_complete(self.server.bootstrap([(self.ip, kademlia_port)]))
        for node in bootstrap_nodes:
            print("Bootstraping with: " + str(node))
            self.loop.run_until_complete(self.server.bootstrap([(node[0], node[1])]))

        # Extract the public key from the private key
        self.public_key = self.serialize_key(self.private_key.public_key())
        
        # Update state using the data on the DHT
        dht_info = self.loop.run_until_complete(
            self.server.get(self.public_key))
        if dht_info != None:
            dht_info = json.loads(dht_info)
            self.subscribers = dht_info["subscribers"]

        self.loop.run_until_complete(self.update_timeline())
        self.loop.run_until_complete(self.sync_subs())
        self.loop.run_until_complete(self.update_info())

        self.receiver.daemon = True
        self.receiver.start()
    
    async def update_subscribers(self):
        """Updates subscribers using dht data"""
        dht_info = await self.server.get(self.public_key)
        if dht_info != None:
            dht_info = json.loads(dht_info)
            self.subscribers = dht_info["subscribers"]
            return self.subscribers
        return []
    
    async def update_info(self):
        """Updates both local and dht data with the current state"""
        self.update_local_info()
        await self.update_dht()

    def update_local_info(self):
        """Updates local data with the current state"""
        with open(self.persistence_file, 'w') as json_file:
            info = {
            "subscribers": self.subscribers,
            "subscriptions": self.subscriptions,
            "posts": json.dumps(self.posts),
            "last_post_id": self.last_post_id,
        }
            json_file.write(json.dumps(info))

    def load_local_info(self):
        """Fetches local data and updates current state"""
        if not os.path.exists(self.persistence_file):
            return

        with open(self.persistence_file) as json_file:
            try:
                info = json.load(json_file)
                self.subscribers = info["subscribers"]
                self.subscriptions = info["subscriptions"]
                loaded_posts = json.loads(info["posts"])
                for key in loaded_posts:
                    loaded_posts[key] = {int(k): v if k.isnumeric() else k for k, v in loaded_posts[key].items()}
                self.posts = loaded_posts
                self.last_post_id = info["last_post_id"]
            except Exception as e:
                print("Local Persistence Exception " + str(e))

    async def update_dht(self):
        """Updates dht data with current state"""
        await self.server.set(self.public_key, json.dumps(self.get_dht_info()))

    def get_dht_info(self):
        """Fetches dht data and updates current state"""
        return {
            "ip": self.ip,
            "port": self.receiver_port,
            "subscriptions": self.subscriptions,
            "subscribers": self.subscribers,
            "last_post_id": self.last_post_id,
        }

    def get_posts(self):
        """Returns a list with the user's posts sorted by the timestamp"""
        res_posts = []
        for author in self.posts.keys():
            for id in self.posts[author].keys():
                full_post = self.posts[author][id]
                full_post["author"] = author
                full_post["id"] = id
                res_posts.append(full_post)
        res_posts.sort(key=lambda post: post["timestamp"], reverse=True)
        return res_posts

    def serialize_key(self, public_key):
        """Serializes public key"""
        return public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    
    def deserialize_key(self, public_key):
        """Deserializes public key"""
        try:
            return serialization.load_pem_public_key(public_key.encode('utf-8'))
        except Exception as e:
            print("Deserialize Exception " + str(e))

    async def create_post(self, text):
        """Creates a new post with the given text, signed with the user's private key"""
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
        await self.update_info()
        await self.sync_subs()

        return post

    def sign(self, text):
        """Signs the given text with the user's private key"""
        # Sign the text using the user's private key
        signature = self.private_key.sign(text.encode('utf-8'))
        return signature

    def verify_signature(self, public_key, signature, content):
        """Verifies the signature of a given content"""
        public_key = self.deserialize_key(public_key)
        return public_key.verify(signature, content)

    def verify_post_signature(self, author_key, post):
        """Verifies the signature of the given post using the author's public key"""

        # Verify the signature using the author's public key
        message = f"{post['text']}:{post['timestamp']}"
        author_key = self.deserialize_key(author_key)
        try:
            result = author_key.verify(base64.b64decode(post["signature"].encode('utf-8')), message.encode('utf-8'))
            return result == None
        except Exception as e:
            print("Verification Exception " + str(e))

    async def write_message(self, ip, port, message):
        """Writes message and waits for an answer"""
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            message = json.dumps(message)
            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()
            line = await reader.read(-1)
            
            if line:
                line = line.strip()
                line = line.decode()
                message = json.loads(line)
                return (True, message)
            
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print("Write Exception " + str(e) + " in message " + str(message))
            return (False, e)

    async def send_to_peer(self, public_key, message):
        """Sends a message to peer and processes answer"""
        print("Getting: " + public_key)
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        ans = await self.write_message(peer_info["ip"], peer_info["port"], message)
        if ans != None and ans[0]:
            return (0, "Message sent", ans[1])
        else:
            return (-1, "Message not sent", peer_info)

    async def add_subscriber(self, public_key):
        """Adds subscriber to state"""
        await self.update_subscribers()
        if public_key not in self.subscribers:
            self.subscribers.append(public_key)
            await self.update_info()

    async def remove_subscriber(self, public_key):
        """Removes subscriber from state"""
        await self.update_subscribers()
        if public_key in self.subscribers:
            self.subscribers.remove(public_key)
            await self.update_info()

    async def add_subscription(self, public_key):
        """Adds subscription from state"""
        if public_key not in self.subscriptions:
            self.subscriptions.append(public_key)
            await self.update_info()

    async def remove_subscription(self, public_key):
        """Removes subscription from state"""
        if public_key in self.subscriptions:
            self.subscriptions.remove(public_key)
            await self.update_info()

    async def add_subscription_to_foreign_dht(self, public_key):
        """Adds subscription to other user's entry in the dht"""
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        if self.public_key not in peer_info["subscribers"]:
            peer_info["subscribers"].append(self.public_key)
            await self.server.set(public_key, json.dumps(peer_info))
        return (0, "Added subscription to DHT with success")

    async def remove_subscription_from_foreign_dht(self, public_key):
        """Removes subscription to other user's entry in the dht"""
        peer_info = await self.server.get(public_key)
        if peer_info is None:
            return (-2, "Unknown Public Key")
        peer_info = json.loads(peer_info)
        if self.public_key in peer_info["subscribers"]:
            peer_info["subscribers"].remove(self.public_key)
            await self.server.set(public_key, json.dumps(peer_info))
        return (0, "Removed subscription from DHT with success")

    async def subscribe(self, public_key):
        """Attempts to send subscription message to other user and interpret answer"""
        if public_key in self.subscriptions:
            return (-3, "Already subscribed")
        message = {
            "op": "subscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            # "signature": None,
        }
        # message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        direct_ans = await self.send_to_peer(public_key, message)
        # Target doesn't exist
        if direct_ans[0] == -2:
            return (-2, "Didn't subscribe. Public Key unknown")
        # Target exists
        else:
            await self.add_subscription(public_key)

            # Target is offline
            if direct_ans[0] == -1:
                await self.add_subscription_to_foreign_dht(public_key)
                peer_subscribers = direct_ans[2]["subscribers"]
                for sub in peer_subscribers:
                    if sub != self.public_key:
                        sub_ans = await self.request_posts(sub, public_key, 0)
                        if sub_ans[0]:
                            return (1, "Subscribed and got posts from other subscribers")
                return (-1, "Subscribed but didn't get posts from other subscribers")

            # Target is online
            if direct_ans[2]["posts"] != {}:
                await self.receive_posts(direct_ans[2]["author"], json.loads(direct_ans[2]["posts"]))
            return (0, "Successfully subscribed and got posts directly from target")

    async def unsubscribe(self, public_key):
        """Attempts to send an unsubscribe message to other user and interpret answer"""
        message = {
            "op": "unsubscribe",
            "sender": self.public_key,
            "timestamp": time.time(),
            # "signature": None,
        }
        # message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't unsubscribe. Public Key unknown")
        else:
            await self.remove_subscription(public_key)
            self.posts.pop(public_key, None)
            await self.update_info()
            if ans[0] == 0:
                return (0, "Unsubscribed and warned target")
            await self.remove_subscription_from_foreign_dht(public_key)
            return (-1, "Unsubscribed but didn't warn target")

    async def find_posts(self, target_public_key, first_post=0):
        """Attempts to get posts from an user asking him directly or its subscribers"""
        direct_ans = await self.request_posts(target_public_key, target_public_key, first_post)
        if direct_ans[0] == -1:
            target_info = await self.server.get(target_public_key)
            if target_info == None:
                return (-2, "Didn't request posts. Target Public Key unknown")
            target_info = json.loads(target_info)
            for sub in target_info["subscribers"]:
                if sub != self.public_key:
                    sub_ans = await self.request_posts(sub, target_public_key, first_post)
                    if sub_ans[0] == 0:
                        return (1, "Requested posts to other subscribers")
            return (-1, "Didn't request posts. Neither target nor subscribers were available")
        else:
            return direct_ans

    async def request_posts(self, public_key, target_public_key, first_post=0):
        """Attempts to request posts from a target user to a given user (the author or other)"""
        message = {
            "op": "request posts",
            "sender": self.public_key,
            "target": target_public_key,
            "first_post": first_post,
            "timestamp": time.time(),
            # "signature": None,
        }
        # message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['target']}:{message['first_post']}:{message['timestamp']}")
        if await self.server.get(target_public_key) == None:
            return (-3, "Didn't request posts. Target Public Key unknown")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't request posts. Interlocutor Public Key unknown")
        elif ans[0] == 0:
            if ans[2]["posts"] != {}:
                await self.receive_posts(ans[2]["author"], json.loads(ans[2]["posts"]))
            return (0, "Got posts")
        else:
            return (-1, "Didn't request posts. User offline")

    async def receive_posts(self, author_key, posts):
        """Validates received posts (using the signature) and chooses which ones to keep"""
        for item in posts.items():
            if self.verify_post_signature(author_key, item[1]):
                if author_key in self.posts.keys():
                    if item[0] not in self.posts[author_key].keys():
                        self.posts[author_key].update({int(item[0]): item[1]})
                else:
                    self.posts[author_key]= {int(item[0]): item[1]}
        await self.update_info()
                
    async def send_sync(self, public_key):
        """Attempts to send sync message to a given user"""
        message = {
            "op": "sync",
            "sender": self.public_key,
            "last_post_id": self.last_post_id,
            "timestamp": time.time(),
            # "signature": None,
        }
        # message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['timestamp']}")
        ans = await self.send_to_peer(public_key, message)
        if ans[0] == -2:
            return (-2, "Didn't send sync. Public Key unknown")
        elif ans[0] == 0:
            return (0, "Sent sync")
        else:
            return (-1, "Didn't send sync. User offline")
    
    async def sync_subs(self):
        """Attempts to send sync messages to all its subscribers"""
        await self.update_subscribers()
        for sub in self.subscribers:
            await self.send_sync(sub)
        
    async def update_timeline(self):
        """Updates timeline by requesting posts to all its subscriptions"""
        for public_key in self.subscriptions:
            if public_key in self.posts and len(self.posts[public_key]) > 0:
                post_latest_id = int(max(self.posts[public_key].keys()))
                await self.find_posts(public_key, post_latest_id + 1)
            else:
                await self.find_posts(public_key, 0)
        return self.posts
