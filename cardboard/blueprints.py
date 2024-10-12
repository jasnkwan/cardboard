from flask import Blueprint, jsonify, send_from_directory, request
from cardboard.cardboard import start_card, stop_card
from cardboard import cardboard


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
    if cardboard.board_json is not None:
        return jsonify(cardboard.board_json)
    
    return jsonify({"error": f"{cardboard.board_json} not set."})


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