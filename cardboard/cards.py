"""
Cards definition
"""
import json

from cardboard.sockets import SocketServer, CurrentTimeProvider


class Card:
    def __init__(self, title="Card", type="Default", url=None, data_provider=None):
        self.title = title
        self.type = type
        #self.host = host
        #self.port = port
        self.url = url
        self.socket = SocketServer(url=url)

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
            "url": self.url,
        }

class DataCard(Card):
    def __init__(self, title="Data", url=None):
        super().__init__(title=title, type="Data", url=url)
        self.groups = []

    def to_dict(self):
        o = super().to_dict()
        o["groups"] = self.groups
        return o

class PlotCard(Card):
    def __init__(self, title="Plot", url=None):
        super().__init__(title=title, type="Plot", url=url)

