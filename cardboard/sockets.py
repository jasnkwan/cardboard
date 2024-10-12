"""
Websocket utils
"""

import asyncio
import datetime
import json
import threading
from urllib.parse import urlparse
import websockets
import time


def parse_websocket_url(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Validate if the scheme is websocket (ws or wss)
    if parsed_url.scheme not in ['ws', 'wss']:
        raise ValueError("Invalid WebSocket URL scheme. Must be 'ws' or 'wss'.")
    
    # Extract hostname and port
    hostname = parsed_url.hostname
    port = parsed_url.port
    
    if not hostname or not port:
        raise ValueError("WebSocket URL must contain both hostname and port.")
    
    return hostname, port


class SocketDataProvider:
    def __init__(self, listener=None):
        self.listeners = []
        self.data_thread = None
        self.running = False

        if listener is not None:
            self.add_listener(listener)

    def add_listener(self, l):
        if not l in self.listeners:
            self.listeners.append(l)
    
    def remove_listener(self, l):
        self.listeners.remove(l)

    def start(self):
        self.running = True
        self.data_thread = threading.Thread(target=self._update_data, daemon=True)
        self.data_thread.start()
        print(f"Started data provider thread")

    def stop(self):
        self.running = False
        self.data_thread.join()
        self.thread = None

    def is_running(self):
        return self.running
    

class TimeProvider(SocketDataProvider):
    def __init__(self, listener=None):
        super().__init__(listener)

    def _update_data(self):
        
        while self.running:
            data = {
                "label": "Current time",
                "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            for listener in self.listeners:
                listener.on_socket_data(json.dumps(data))

            time.sleep(1)
        print(f"Current time provider: done.")


class SocketDataListener:    
    def on_socket_data(data):
        pass


class WebsocketServer(SocketDataListener):
    def __init__(self, url=None, sleep=.2, debug=False):
        super().__init__()

        self.url = url
        self.sleep = sleep
        self.debug = debug
        
        self.server = None
        self.loop = None
        self.running = False
        self.server_thread = None
        self.shutdown_event = asyncio.Event()

        self.data = None
        self.last_data = None


    def on_socket_data(self, data):
        # print(f"on_socket_data: {self.data}")
        self.data = data
        

    async def consumer(self, msg):
        print(f"Received message: {msg}")


    async def consumer_handler(self, ws):
        async for message in ws:
            await self.consumer(message)


    async def producer_handler(self, ws):
        try:
            while True:
                if self.data != self.last_data:                                        
                    await ws.send(self.data)
                    self.last_data = self.data
                
                # Small sleep to avoid busy-waiting
                await asyncio.sleep(.1)
                
        except websockets.ConnectionClosed as e:
            print(f"Client disconnected. Server close code: {e.rcvd.code}, reason: {e.rcvd.reason}")
        except Exception as e:
            print(f"Unknown exception: {e}")
        finally:
            print("Closing server WebSocket.")


    async def handle(self, websocket):
        consumer_task = asyncio.create_task(self.consumer_handler(websocket))
        producer_task = asyncio.create_task(self.producer_handler(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()        


    async def _start(self):
        # Get the current event loop for this thread (background thread)
        self.loop = asyncio.get_running_loop()

        # Start the WebSocket server
        host, port = parse_websocket_url(self.url)
        self.server = await websockets.serve(self.handle, host, port)
        print(f"WebSocket server started on {self.url}")

        # Wait until the shutdown event is triggered
        await self.shutdown_event.wait()

        # Cleanly close the server
        await self.server.wait_closed()


    async def _shutdown(self):
        # Set the shutdown event to stop the server
        print("Shutting down WebSocket server...")
        self.shutdown_event.set()  # Trigger the shutdown event
        if self.server is not None:
            self.server.close()  # Close the WebSocket server
            await self.server.wait_closed()  # Wait for the server to close


    def _launch(self):
        # Start the server in the current asyncio event loop
        asyncio.run(self._start())


    def start(self):
        # Create a new thread to run the WebSocket server
        self.server_thread = threading.Thread(target=self._launch, daemon=True)
        self.server_thread.start()


    def stop(self):
        # Schedule the shutdown process in the event loop running in the background thread
        if self.loop and self.server_thread:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
            self.server_thread.join()  # Wait for the background thread to finish
            print("Server shutdown complete.")


    def is_running(self):
        running = self.server is not None and self.running
        print(f"  return value:   {running}")
        return running


if __name__ == "__main__":
    provider = TimeProvider()
    provider.start()
    time.sleep(5)
    provider.stop()
    print(f"Good bye.")