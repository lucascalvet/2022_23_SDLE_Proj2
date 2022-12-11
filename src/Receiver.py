from threading import Thread    
import asyncio
import json
import time

class Receiver(Thread):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def run(self):
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.serve())

    async def serve(self):
        server = await asyncio.start_server(self.request_handler, self.user.ip, self.user.receiver_port)
        await server.serve_forever()
    
    async def request_handler(self, reader, writer):
        try:
            line = await reader.read(-1)
            
            if line:
                line = line.strip()
                line = line.decode()
                message = json.loads(line)

                operation = message["op"]
                if operation == "subscribe":
                    self.subscribe_handler(writer, message)
                elif operation == "unsubscribe":
                    self.unsubscribe_handler(writer, message)
                elif operation == "request posts":
                    self.request_posts_handler(writer, message)
                elif operation == "sync":
                    self.sync_handler(writer, message)
                else:
                    print("Invalid operation")

            writer.close()
        except Exception as e:
            print("Receiver Exception " + str(e) + " in operation " + str(operation))

    async def write_res(self, writer, message):
        try:
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
    
    async def write_ack(self, writer):
        message = {
            "op": "acknowledge",
            "sender": self.user.public_key,
            "timestamp": time.time(),
            # "signature": None,
        }
        return await self.write_res(writer, message)

    async def send_posts(self, writer, public_key, target_public_key, first_post=0):
        message = {
            "op": "send posts",
            "sender": self.user.public_key,
            "author": target_public_key,
            "first_id": first_post,
            "posts": {},
            "timestamp": time.time(),
            # "signature": None,
        }
        if target_public_key not in self.user.posts.keys():
            await self.write_res(writer, message)
     
        try:
            posts_to_send = {key: self.posts[target_public_key][key] for key in self.posts[target_public_key] if key >= first_post}
            posts_to_send = json.dumps(posts_to_send)
        except Exception as e:
            print("JSON Exception " + str(e))
     
        message["posts"] = posts_to_send
        #message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['author']}:{message['first_id']}:{message['posts']}:{message['timestamp']}")
        print("DEBUG_INSIDE_SEND_DEST:" + str(public_key))
        await self.write_res(writer, message)

    def subscribe_handler(self, writer, message):
        print("DEBUG_SUBHAND_SELF: " + str(self.user.public_key))
        print("DEBUG_SUBHAND_SENDDEST: " + str(message["sender"]))
        self.user.add_subscriber(message["sender"])
        asyncio.run_coroutine_threadsafe(self.send_posts(writer, message["sender"], self.user.public_key), loop=self.user.loop)
    
    def unsubscribe_handler(self, writer, message):
        self.user.remove_subscriber(message["sender"])
        asyncio.run_coroutine_threadsafe(self.write_ack(writer), loop=self.user.loop)
        
    def request_posts_handler(self, writer, message):
        print("DEBUG_REQUESTHAND_SELF: " + str(self.user.public_key))
        print("DEBUG_REQUESTHAND_SENDDEST: " + str(message["sender"]))
        asyncio.run_coroutine_threadsafe(self.send_posts(writer, message["sender"], message["target"], message["first_post"]), loop=self.user.loop)
        
    def sync_handler(self, writer, message):
        asyncio.run_coroutine_threadsafe(self.write_ack(writer), loop=self.user.loop)
        if message["sender"] in self.user.subscription:
            if message["sender"] in self.posts and len(self.posts[message["sender"]]) > 0:
                post_latest_id = int(max(self.posts[message["sender"]].keys()))
                if int(message["last_post_id"]) > post_latest_id:
                    asyncio.run_coroutine_threadsafe(self.user.find_posts(message["sender"], post_latest_id + 1), loop=self.user.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.user.find_posts(message["sender"], 0), loop=self.user.loop)
    
    