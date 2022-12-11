from threading import Thread
import asyncio
import json
import time


class Receiver(Thread):
    """Receiver class constructor"""

    def __init__(self, user):
        super().__init__()
        self.user = user

    def run(self):
        """Main class function"""
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.serve())

    async def serve(self):
        """Serve function"""
        server = await asyncio.start_server(self.request_handler, self.user.ip, self.user.receiver_port)
        await server.serve_forever()

    async def request_handler(self, reader, writer):
        """Redirect each type of operation to its specific handler"""
        try:
            line = await reader.read(-1)

            if line:
                line = line.strip()
                line = line.decode()
                message = json.loads(line)

                operation = message["op"]
                if operation == "subscribe":
                    await self.subscribe_handler(writer, message)
                elif operation == "unsubscribe":
                    await self.unsubscribe_handler(writer, message)
                elif operation == "request posts":
                    await self.request_posts_handler(writer, message)
                elif operation == "sync":
                    await self.sync_handler(writer, message)
                else:
                    print("Invalid operation")
                    writer.close()

        except Exception as e:
            print("Receiver Exception " + str(e) +
                  " in operation " + str(operation))

    async def write_res(self, writer, message):
        """Writes the response"""
        try:
            message = json.dumps(message)
            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            writer.close()
            print("Receiver Write Exception " +
                  str(e) + " in response " + str(message))
            return False

    async def write_ack(self, writer):
        """Writes an acknowledgement response"""
        message = {
            "op": "acknowledge",
            "sender": self.user.public_key,
            "timestamp": time.time(),
            # "signature": None,
        }
        return await self.write_res(writer, message)

    async def send_posts(self, writer, target_public_key, first_post=0):
        """Responds with the requested posts"""
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
            return

        try:
            print("HOWDY")
            posts_to_send = {key: self.user.posts[target_public_key][key]
                             for key in self.user.posts[target_public_key] if key >= first_post}
            print("SENDING: " + str(posts_to_send))
            posts_to_send = json.dumps(posts_to_send)
        except Exception as e:
            writer.close()
            print("JSON Exception " + str(e))

        message["posts"] = posts_to_send
        # message["signature"] = self.sign(f"{message['op']}:{message['sender']}:{message['author']}:{message['first_id']}:{message['posts']}:{message['timestamp']}")
        await self.write_res(writer, message)

    async def subscribe_handler(self, writer, message):
        """Handles Subscribe messages"""
        asyncio.run_coroutine_threadsafe(self.user.add_subscriber(
            message["sender"]), loop=self.user.loop)
        await self.send_posts(writer, self.user.public_key)

    async def unsubscribe_handler(self, writer, message):
        """Handles Unsubscribe messages"""
        asyncio.run_coroutine_threadsafe(self.user.remove_subscriber(
            message["sender"]), loop=self.user.loop)
        await self.write_ack(writer)

    async def request_posts_handler(self, writer, message):
        """Handles Request Post messages"""
        await self.send_posts(writer, message["target"], message["first_post"])

    async def sync_handler(self, writer, message):
        """Handles Sync messages"""
        await self.write_ack(writer)
        if message["sender"] in self.user.subscriptions:
            if message["sender"] in self.user.posts and len(self.user.posts[message["sender"]]) > 0:
                post_latest_id = int(
                    max(self.user.posts[message["sender"]].keys()))
                if int(message["last_post_id"]) > post_latest_id:
                    asyncio.run_coroutine_threadsafe(self.user.find_posts(
                        message["sender"], post_latest_id + 1), loop=self.user.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.user.find_posts(
                    message["sender"], 0), loop=self.user.loop)
