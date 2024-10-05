"""
Websocket utils
"""

import asyncio
import datetime
import threading
import websockets


def send_current_time():
    data = {
        "label": "Current time",
        "value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return data


class SocketServer:
    """
    Manage a server socket
    """
    def __init__(self, host="localhost", port=None, data_func=send_current_time):
        self.host = host
        self.port = port
        self.shutdown_event = asyncio.Event()  # Event to signal shutdown
        self.server = None  # Store the server object
        self.server_thread = None  # Store the thread running the server
        self.loop = None  # Store the asyncio loop used by the server
        self.data_func = data_func


    @staticmethod
    async def send(ws: websockets.WebSocketServerProtocol) -> None:
        try:
            while True:

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await ws.send(f"Current server time: {current_time}")
                print(f"Sent time: {current_time}")
                await asyncio.sleep(1)  # Wait for 1 second between sends
                
        except websockets.ConnectionClosed as e:
            print(f"Client disconnected. Server close code: {e.rcvd.code}, reason: {e.rcvd.reason}")
        finally:
            print("Closing server-side WebSocket.")

    async def _start(self) -> None:
        # Get the current event loop for this thread (background thread)
        self.loop = asyncio.get_running_loop()

        # Start the WebSocket server
        self.server = await websockets.serve(self.send, self.host, self.port)
        print(f"WebSocket server started on ws://{self.host}:{self.port}")

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

    def _run(self):
        # Start the server in the current asyncio event loop
        asyncio.run(self._start())

    def is_running(self):
        return self.server_thread is not None and self.server is not None and self.loop is not None

    def start(self):
        if self.is_running():
            return
        # Create a new thread to run the WebSocket server
        self.server_thread = threading.Thread(target=self._run, daemon=True)
        self.server_thread.start()

    def stop(self):
        # Schedule the shutdown process in the event loop running in the background thread
        if self.loop and self.server_thread:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
            self.server_thread.join()  # Wait for the background thread to finish
            print("Server shutdown complete.")
            self.server_thread = None
            self.server = None
            self.loop = None