from cardboard.cards import Card, DataCard, PlotCard, FormCard
from cardboard.sockets import TimeProvider
import os
import json
import atexit

global board_json
board_json = None

card_dict = {}
data_providers = {}


def cleanup():
    print(f"Cleanup cardboard on exit")
    for card_id in card_dict:
        print(f"{stop_card(card_id)}")

atexit.register(cleanup)


def configure_board(data=None, file=None):
    global board_json
    if data is not None:
        board_json = data
    elif file is not None:
        if os.path.exists(file):
            with open(file, "r") as f:
                board_json = json.load(f)
                print(f"configure: board_json={board_json}")

def start_card(card_id, card_type, card_url):
    print(f"Starting {card_type} card {card_id} on {card_url}")
    global card_dict
    global data_providers

    if card_id in card_dict:
        url = card_dict[card_id].url
        return {"status": "error", "message": f"Card {card_id} already running on {url}"}

    card = None
    if card_type == "Data":
        card = DataCard(title=card_id, url=card_url)        
    elif card_type == "Plot":
        card = PlotCard(title=card_id, url=card_url)
    elif card_type == "Form":
        card = FormCard(title=card_id, url=card_url)
    else:
        card = Card(title=card_id, url=card_url)

    if card is not None:
        card_dict[card_id] = card

    card.start()

    if card_type == "Data" or card_type == "Form":
        print(f"Create default provider for {card.url}")
        data_provider = TimeProvider(listener=card.socket)
        data_provider.start()

        card_id = card.title
        data_providers[card_id] = []
        data_providers[card_id].append(data_provider)

    return {"status": "success", "message": f"Started card {card_id} on {card_url}"}


def stop_card(card_id):
    print(f"Stopping card {card_id}")
    global card_dict
    global data_providers

    if card_id not in card_dict:
        return {"status": "error", "message": f"Card {card_id} not found"}

    card = card_dict[card_id]
    if card is not None:
        if card.is_running():
            card.stop()

    if card_id in data_providers:
        providers = data_providers[card_id]
        if providers is not None:
            for provider in providers:
                if provider.is_running():
                    provider.stop()

    return {"status": "success", "message": f"Stopped card {card_id}"}
