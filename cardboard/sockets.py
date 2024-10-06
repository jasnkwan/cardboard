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
from cardboard.runnable import Runnable



def send_current_time():
    data = {
        "label": "Current time",
        "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return data


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
        if listener is not None:
            self.add_listener(listener)

    def add_listener(self, l):
        if not l in self.listeners:
            self.listeners.append(l)
    
    def remove_listener(self, l):
        self.listeners.remove(l)


class CurrentTimeProvider(Runnable, SocketDataProvider):
    def __init__(self, listener=None):
        super().__init__()
        SocketDataProvider.__init__(self, listener)
        self.data_thread = None
        self.running = False

    async def _on_start(self):
        print(f"Start data provider thread")
        self.data_thread = threading.Thread(target=self._update_data, daemon=True)
        self.data_thread.start()
        self.running = True
        print(f"Started data provider thread")

    async def _on_stop(self):
        self.running = False
        print(f"joining data thread")
        self.data_thread.join()
        print("joined data thread")
        self.thread = None

    def _update_data(self):
        print(f"update data: running={self.running}")
        while self.running:
            data = {
                "label": "Current time",
                "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            for listener in self.listeners:
                listener.on_socket_data(json.dumps(data))

            time.sleep(1)
        print(f"done.")


class SocketDataListener:    
    def on_socket_data(data):
        pass

class SocketServer(SocketDataListener):
    def __init__(self, url=None, sleep=.2, debug=False):
        super().__init__()

        self.url = url
        self.sleep = sleep
        self.debug = debug

        self.data = None
        self.last_data = None

        self.server = None
        self.thread = None
        self.shutdown_event = asyncio.Event()

    async def _start_thread(self):
        print(f"Runnable._start_thread)")
        self.loop = asyncio.get_running_loop()

        # HACK Alert!!!
        # Fix the threading launch and shutdown issues in debug mode.
        try:            
            print(f"SocketServer: Starting socket...")
            host, port = parse_websocket_url(self.url)
            self.server = await websockets.serve(self.send, host, port)
            print(f"WebSocket server started on {self.url}")
        except Exception as e:
            if not self.debug:
                if not str(e).startswith("[Errno 48]"):
                    print(f"{e}")

        # Wait here until shutdown event is triggered
        await self.shutdown_event.wait()


    async def _shutdown_thread(self):
        # Trigger the shutdown event
        self.shutdown_event.set()

        # call the subclass startup func
        if self.server is not None:
            # Close the socket server and wait for it to be closed
            self.server.close()  
            await self.server.wait_closed()


    def _launch_thread(self):
        print(f"SocketServer._launch")

        asyncio.run(self._start_thread())


    def start(self):
        print(f"SocketServer.start: is_running={self.is_running()}")

        if not self.is_running():
            self.thread = threading.Thread(target=self._launch_thread, daemon=True)
            self.thread.start()
    

    def stop(self):
        if self.is_running():
            print(f"SocketServer.stop")
            asyncio.run_coroutine_threadsafe(self._shutdown_thread(), self.loop)
            print(f"SocketServer Ran coroutine")
            self.thread.join()
            print(f"SocketServer thread joined")
            self.thread = None
            self.loop = None
        print(f"SocketServer.stopped") 


    def is_running(self):
        return self.thread is not None and self.loop is not None


    async def send(self, ws: websockets.WebSocketServerProtocol) -> None:
        try:
            while True:
                if self.data != self.last_data:
                    await ws.send(self.data)
                    self.last_data = self.data
                
                # Small sleep to avoid busy-waiting
                await asyncio.sleep(self.sleep)
                
        except websockets.ConnectionClosed as e:
            print(f"Client disconnected. Server close code: {e.rcvd.code}, reason: {e.rcvd.reason}")
        finally:
            print("Closing server-side WebSocket.")


    def on_socket_data(self, data):
        self.data = data
        print(f"on_socket_data: {data}")

'''
class SocketServer(Runnable, SocketDataListener):
    """
    Manage a server socket
    """
    def __init__(self, host="localhost", port=None, sleep=.1):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None  # Store the server object
        
        self.sleep = sleep

        self.data = None
        self.last_data = None

    async def _start_thread(self):
        print(f"SocketServer._start_thread)")
        self.loop = asyncio.get_running_loop()
        print(f"SockerServer._start_thread, call _on_start...")

        # call subclass startup func
        print(f"SocketServer: Starting socket...")
        self.server = await websockets.serve(self.send, self.host, self.port)
        print(f"WebSocket server started on ws://{self.host}:{self.port}")

        print(f"SocketServer._start_thread, called _on_start.")
        # Wait here until shutdown event is triggered
        await self.shutdown_event.wait()


    async def _shutdown_thread(self):
        # Trigger the shutdown event
        self.shutdown_event.set()

        if self.server is not None:
            # Close the socket server and wait for it to be closed
            self.server.close()  
            await self.server.wait_closed()


    def _launch(self):
        print(f"SocketServer._launch")
        asyncio.run(self._start_thread())
        

    async def send(self, ws: websockets.WebSocketServerProtocol) -> None:
        try:
            while True:
                if self.data != self.last_data:
                    await ws.send(self.data)
                    self.last_data = self.data
                
                # Small sleep to avoid busy-waiting
                await asyncio.sleep(self.sleep)
                
        except websockets.ConnectionClosed as e:
            print(f"Client disconnected. Server close code: {e.rcvd.code}, reason: {e.rcvd.reason}")
        finally:
            print("Closing server-side WebSocket.")


    def on_socket_data(self, data):
        self.data = data
        #print(f"on_socket_data: {data}")
'''


if __name__ == "__main__":
    provider = CurrentTimeProvider()
    provider.start()
    time.sleep(5)
    provider.stop()
    print(f"Good bye.")