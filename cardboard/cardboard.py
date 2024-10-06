from flask import jsonify, request
from cardboard.cards import Card, DataCard, PlotCard
import os
import json




'''
temp_card = DataCard(title="Temperature", port=6001)
humidity_card = DataCard(title="Humidity", port=6002)

temp_card.groups.append({
    "label": "Group 0",
    "items": [
        {"label": "Label 0", "value": 0.0},
        {"label": "Label 1", "value": 1.0}
    ]
})
temp_card.groups.append({
    "label": "Group 1",
    "items": [
        {"label": "Label 2", "value": 2.0},
        {"label": "Label 3", "value": 3.0}
    ]
})

humidity_card.groups.append({
    "label": "Group 0",
    "items": [
        {"label": "Label 0", "value": 0.0},
        {"label": "Label 1", "value": 1.0}
    ]
})
humidity_card.groups.append({
    "label": "Group 1",
    "items": [
        {"label": "Label 2", "value": 2.0},
        {"label": "Label 3", "value": 3.0}
    ]
})

card_data = [
    temp_card.to_dict(),
    humidity_card.to_dict()
]

card_dict = {
    "Temperature": temp_card,
    "Humidity": humidity_card
}

#temp_card.start()
#humidity_card.start()
'''

card_dict = {}



def register_routes(blueprint):

    #print(f"cardboard register_routes")

    @blueprint.route("/cards")
    def cards():
        card_data = []
        for card in card_dict.values():
            card_data.append(card.to_dict())
        print(f"route cards/: card_dict={card_dict}")
        print(f"route cards/: card_data={card_data}")
        return jsonify(card_data)
    

    @blueprint.route("/start")
    def start_card():
        card_id = request.args.get("card")
        if card_id is None:
            return jsonify({"error": "Card id not specified."})
        
        card = card_dict[card_id]
        if card is None:
            return jsonify({"error": f"No card for id {card_id}"})
        
        if card.is_running():
            return jsonify({"error": f"Card {card_id} is already running"})
        
        card.start()

        return jsonify({"message": "ok"})
  

    @blueprint.route("/stop")
    def stop_card():
        card_id = request.args.get("card")
        if card_id is None:
            return jsonify({"error": "Card id not specified."})
        
        card = card_dict[card_id]
        if card is None:
            return jsonify({"error": f"No card for id {card_id}"})
        
        if not card.is_running():
            return jsonify({"error": f"Card {card_id} is not running"})

        card.stop()

        return jsonify({"message": "ok"})
    

def start():

    cards_config = os.environ.get("CARDS_CONFIG", default="./tests/data/cards.json")
    if os.path.exists(cards_config):
        print(f"Loading board configuration...")
        cards_json = {}
        with open(cards_config, "r") as f:
            cards_json = json.load(f)

        global card_dict
        for card_json in cards_json["board"]["cards"]:

            card_id = card_json["title"]
            card_title = card_json["title"]
            card_type = card_json["type"]
            card_host = card_json["socket"]["host"]
            card_port = int(card_json["socket"]["port"])
            card_url = f"ws://{card_host}:{card_port}"

            card = None
            if card_type == "Data":
                card = DataCard(title=card_title, host=card_host, port=card_port)
                card.groups = card_json["groups"]
            elif card_type == "Plot":
                card = PlotCard(title=card_title, host=card_host, port=card_port)
            else:
                card = Card(title=card_title, host=card_host, port=card_port)

            if card is not None:
                card_dict[card_id] = card

    print(f"Starting cards...")
    for card in card_dict.values():
        card.start()

def shutdown():
    print(f"SHUTDOWN")
    for card in card_dict.values():
        card.stop()

def is_running():
    running = True
    
    while running:
        count = 0
        for card in card_dict.values():
            if not card.is_running():
                count = count+1
            if count == len(card_dict):
                running = False

    print(f"cardboard running: {running}")
    return running