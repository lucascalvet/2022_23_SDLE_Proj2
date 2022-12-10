from threading import Thread    
import asyncio

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
        # TODO: Handle requests
        return
