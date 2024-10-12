from flask import Blueprint, jsonify, send_from_directory, request
from cardboard.cards import Card, DataCard, PlotCard, FormCard
from cardboard.sockets import TimeProvider
import os
import json
import atexit


card_dict = {}
data_providers = {}


def cleanup():
    print(f"Cleanup cardboard on exit")
    for card_id in card_dict:
        print(f"{stop_card(card_id)}")

atexit.register(cleanup)


cardboard_blueprint = Blueprint('cardboard_blueprint', __name__,  static_folder='../cardboard_ui/dist', static_url_path='/')


@cardboard_blueprint.route('/')
def serve_react_app():
    """
    Serve index.html from vite dist
    """
    return send_from_directory(cardboard_blueprint.static_folder, 'index.html')


@cardboard_blueprint.route('/<path:path>')
def serve_static(path):
    """
    Serve static files from vite dist
    """
    return send_from_directory(cardboard_blueprint.static_folder, path)


@cardboard_blueprint.route("/board")
def board():
    cards_config = os.environ.get("CARDS_CONFIG", default="./tests/data/cards.json")
    if os.path.exists(cards_config):
        board_json = {}
        with open(cards_config, "r") as f:
            board_json = json.load(f)

        return jsonify(board_json)
    
    return jsonify({"error": f"{cards_config} not found."})


@cardboard_blueprint.route("/start")
def start():
    card_id = request.args.get("card")
    type = request.args.get("type")
    url = request.args.get("url")
    print(f"start {type} card {card_id} on {url}")
    retval = start_card(card_id, type, url)
    return jsonify(retval)


@cardboard_blueprint.route("/stop")
def stop():
    card_id = request.args.get("card")
    print(f"stop card {card_id}")
    retval = stop_card(card_id)
    return jsonify(retval)

######################

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

    providers = data_providers[card_id]
    if providers is not None:
        for provider in providers:
            if provider.is_running():
                provider.stop()

    return {"status": "success", "message": f"Stopped card {card_id}"}


def start():
    print(f"STARTUP")
    global card_dict
    global data_providers

    if len(card_dict) > 0:
        shutdown()
    
    cards_config = os.environ.get("CARDS_CONFIG", default="./tests/data/cards.json")
    if os.path.exists(cards_config):
        print(f"Loading board configuration...")
        board_json = {}
        with open(cards_config, "r") as f:
            board_json = json.load(f)

        for column in board_json["board"]["columns"]:

            column_name = column["name"]
            column_cards = column["cards"]

            for card_json in column_cards:

                card_id = card_json["title"]
                card_title = card_json["title"]
                card_type = card_json["type"]
                card_url = card_json["url"]

                card = None
                if card_type == "Data":
                    card = DataCard(title=card_title, url=card_url)
                    card.groups = card_json["groups"]
                elif card_type == "Plot":
                    card = PlotCard(title=card_title, url=card_url)
                elif card_type == "Form":
                    card = FormCard(title=card_title, url=card_url)
                else:
                    card = Card(title=card_title, url=card_url)

                if card is not None:
                    card_dict[card_id] = card

    print(f"Starting card sockets...")
    for card in card_dict.values():
        card.start()

    print(f"Starting default data providers...")
    for card in card_dict.values():
        if card.type == "Data":
            print(f"Create default provider for {card.url}")
            data_provider = TimeProvider(listener=card.socket)
            data_provider.start()

            card_id = card.title
            data_providers[card_id] = []
            data_providers[card_id].append(data_provider)


def shutdown():
    print(f"SHUTDOWN")
    global data_providers
    global card_dict

    print(f"Stopping card sockets...")
    for card in card_dict.values():
        card.stop()

    print(f"Stopping default data providers...")
    for data_provider_list in data_providers.values():
        for data_provider in data_provider_list:
            data_provider.stop()

    data_providers = {}
    card_dict = {}


def is_running():
    running = True
    
    while running:
        count = 0
        for card in card_dict.values():
            if not card.is_running():
                count = count+1
            if count == len(card_dict):
                running = False
    return running