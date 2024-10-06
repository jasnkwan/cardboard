"""
Runnable class
"""

import asyncio
import threading


class Runnable:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.thread = None
        self.loop = None
        self.running = False
        
    async def _start_thread(self):
        self.loop = asyncio.get_running_loop()
        
        await self._on_start()
        # Wait here until shutdown event is triggered
        await self.shutdown_event.wait()


    async def _shutdown_thread(self):
        # Trigger the shutdown event
        self.shutdown_event.set()

        # call the subclass startup func
        await self._on_stop()


    def _launch_thread(self):
        asyncio.run(self._start_thread())


    def start(self):
        if not self.is_running():
            self.thread = threading.Thread(target=self._launch_thread, daemon=True)
            self.thread.start()
    

    def stop(self):
        if self.is_running():
            asyncio.run_coroutine_threadsafe(self._shutdown_thread(), self.loop)
            
            self.thread.join()
            self.thread = None
            self.loop = None


    def is_running(self):
        return self.thread is not None and self.loop is not None

