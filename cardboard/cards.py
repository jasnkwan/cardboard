"""
Cards definition
"""
import json

from cardboard.sockets import WebsocketServer


"""
Base class for cards
"""
class Card:
    def __init__(self, title="Card", type="Default", url=None):
        self.title = title
        self.type = type
        self.url = url
        self.socket = WebsocketServer(url=url)

    def start(self):
        self.socket.start()

    def stop(self):
        self.socket.stop()

    def is_running(self):
        return self.socket.is_running()

    def to_json(self):
        return json.dumps(self.to_dict)
    
    def to_dict(self):
        return {
            "title": self.title,
            "type": self.type,
            "url": self.url,
        }


"""
Simple two column data table presentation card
"""
class DataCard(Card):
    def __init__(self, title="Data", url=None):
        super().__init__(title=title, type="Data", url=url)
        self.groups = []

    def to_dict(self):
        o = super().to_dict()
        o["groups"] = self.groups
        return o


"""
Plot card for displaying a Plotly plot
"""
class PlotCard(Card):
    def __init__(self, title="Plot", url=None):
        super().__init__(title=title, type="Plot", url=url)


"""
Form card for supplying data from client to server
"""
class FormCard(Card):
    def __init__(self, title="Form", url=None):
        super().__init__(title=title, type="Form", url=url)
        self.groups = []

    def to_dict(self):
        o = super().to_dict()
        o["groups"] = self.groups
        return o
