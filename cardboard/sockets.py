"""
Websocket utils
"""

import asyncio
import datetime
import json
import threading
from urllib.parse import urlparse
import websockets
import socket
import time
import struct
import selectors
import importlib
import pkgutil
import inspect


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

def import_providers(package_name):
    """Find and load all subclasses of Producer and Consumer."""
    discovered_plugins = {}
    # Import the base package
    package = importlib.import_module(package_name)
    # Recursively find all submodules in the package
    for finder, name, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        module = importlib.import_module(name)
        # Check for subclasses of Producer and Consumer
        for attr_name in dir(module):
            try:
                attr = getattr(module, attr_name)    
                if (inspect.isclass(attr) 
                    and issubclass(attr, (SocketDataProvider)) 
                    and attr not in (SocketDataProvider)):
                    class_name = f"{module.__name__}.{attr_name}"
                    discovered_plugins[class_name] = attr
            except Exception as e:
                print(f"{e}")
        

    return discovered_plugins

def instantiate_provider(provider_classpath, package_providers):
    class_name = f"{provider_classpath}" 
    cls = package_providers[class_name]
    if cls is not None:
        try:
            instance = cls()
            #print(f"Instantiated instance of type {instance.type}: {class_name}")
            return instance
        except Exception as e:
            print(f"Failed to instantiate {class_name}: {e}")
    return None
    

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


class UDPSocketProvider(SocketDataProvider):
    def __init__(self, group_addr="232.10.11.12", port=3333, listener=None):
        super().__init__(listener)

        # create a socket and set options
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 6)        
        
        self.group_addr = group_addr
        self.port = int(port)

        # bind udp socket to desired port on all network interfaces
        self.socket.bind(("0.0.0.0", self.port))

        # join the multicast group to receive data from clients
        mreq = struct.pack("4sl", socket.inet_aton(self.group_addr), socket.INADDR_ANY)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        # selector for processing events
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.socket, selectors.EVENT_READ, data=None)
        
        # the socket thread
        self.thread = None
        
        # running flag
        self.running = False    

    def _update_data(self):
        while self.running:
            # read data from udp socket and write to websocket
            try:
                events = self.sel.select(timeout=1)  # Block until at least one event is ready
                for key, mask in events:
                    
                    if mask & selectors.EVENT_READ:
                        
                        # receive data from a client and forward to listeners
                        data, addr = self.socket.recvfrom(4096)
                        print(f"bytes received: {data} from {addr}")
                        for listener in self.listeners:
                            listener.on_socket_data(data)
                            
            except Exception as e:
                print(f"Error in UDP selector receive: {e}")

 
            pass
        print(f"UDP socket provider: done.")


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