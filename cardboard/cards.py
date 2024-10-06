"""
Cards definition
"""
import json

from cardboard.sockets import SocketServer, CurrentTimeProvider


class Card:
    def __init__(self, title="Card", type="Default", host="localhost", port=None, data_provider=None):
        self.title = title
        self.type = type
        self.host = host
        self.port = port
        self.socket = SocketServer(host=host, port=port)

        self.data_provider = data_provider
        if self.data_provider is None:
            print(f"Starting default current time provider...")
            self.data_provider = CurrentTimeProvider(listener=self.socket)
            self.data_provider.start()

    def set_data_provider(self, provider):
        self.data_provider = provider

    def start(self):
        self.socket.start()

    def stop(self):
        self.socket.stop()
        if self.data_provider is not None:
            self.data_provider.stop()
        print(f"cards.stopped")

    def is_running(self):
        return False

    def to_json(self):
        return json.dumps(self.to_dict)
    
    def to_dict(self):
        return {
            "title": self.title,
            "type": self.type,
            "host": self.host,
            "port": self.port,
            "url": f"ws://{self.socket.host}:{self.socket.port}",
        }

class DataCard(Card):
    def __init__(self, title="Data", host=None, port=None):
        super().__init__(title=title, type="Data", host=host, port=port)
        self.groups = []

    def to_dict(self):
        o = super().to_dict()
        o["groups"] = self.groups
        return o

class PlotCard(Card):
    def __init__(self, title="Plot", port=None):
        super().__init__(title=title, type="Plot", port=port)

