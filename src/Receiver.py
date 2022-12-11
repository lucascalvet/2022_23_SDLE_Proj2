from threading import Thread    
import asyncio
import json

class Receiver(Thread):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def run(self):
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.serve())

    async def serve(self):
        server = await asyncio.start_server(self.request_handler, self.user.ip, self.user.receiver_port)
        server.serve_forever()
    
    async def request_handler(self, reader, writer):
        line = await reader.read(-1)

        if line:
            line = line.strip()
            line = line.decode()
            message = json.loads(line)

            operation = message["op"]
            if operation == "subscribe":
                self.subscribe_handler(message)
            elif operation == "unsubscribe":
                self.unsubscribe_handler(message)
            elif operation == "request posts":
                self.request_posts_handler(message)
            elif operation == "request posts":
                self.send_posts_handler(message)
            else:
                print("Invalid operation")

        writer.close()

    def subscribe_handler(self, message):
        asyncio.run_coroutine_threadsafe(self.user.add_subscriber(message["user"]), loop=self.user.loop)
        asyncio.run_coroutine_threadsafe(self.user.send_posts(message["user"], self.user.public_key), loop=self.user.loop)
    
    def unsubscribe_handler(self, message):
        asyncio.run_coroutine_threadsafe(self.user.remove_subscriber(message["user"]), loop=self.user.loop)
        
    def request_posts_handler(self, message):
        asyncio.run_coroutine_threadsafe(self.user.send_posts(message["user"], message["target"], message["first_post"]), loop=self.user.loop)
    
    def send_posts_handler(self, message):
        asyncio.run_coroutine_threadsafe(self.user.receive_posts(message["posts"]), loop=self.user.loop)
    