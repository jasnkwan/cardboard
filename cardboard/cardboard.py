from flask import jsonify, request
from cardboard.cards import DataCard


def register_routes(blueprint):

    print(f"cardboard register_routes")

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

    temp_card.start()
    humidity_card.start()
    

    @blueprint.route("/cards")
    def cards():
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