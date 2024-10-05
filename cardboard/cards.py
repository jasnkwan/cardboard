from collections import deque
import json

from cardboard.sockets import SocketServer


def _serialize(obj):
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, set):
        return [_serialize(item) for item in obj]  # Convert set to list
    elif isinstance(obj, deque):
        return [_serialize(item) for item in obj]  # Convert set to list
    elif isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    elif hasattr(obj, "__dict__"):
        # Convert object attributes to a dictionary
        return {key: _serialize(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, SocketServer):
        return {"host": obj.host, "port": obj.port}
    else:
        # For basic types, return the value directly
        return obj
        

class Card:
    def __init__(self, title="Card", type="Default", port=None):
        self.title = title
        self.type = type
        self.port = port
        self.socket = SocketServer(host="localhost", port=port)

    def start(self):
        self.socket.start()

    def stop(self):
        self.socket.stop()

    def is_running(self):
        return self.socket.is_running()

    def to_json(self):
        return json.dumps(_serialize(self))
    
    def to_dict(self):
        return json.loads(self.to_json())

class DataCard(Card):
    def __init__(self, title="Data", port=None):
        super().__init__(title=title, type="Data", port=port)
        self.groups = []

class PlotCard(Card):
    def __init__(self, title="Plot", port=None):
        super().__init__(title=title, type="Plot", port=port)

