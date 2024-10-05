from flask import Flask, send_from_directory, jsonify, Blueprint
from cardboard import cardboard

app = Flask(__name__, static_folder='../cardboard_ui/dist', static_url_path='/')

cardboard_bp = Blueprint('cardboard', __name__)
cardboard.register_routes(cardboard_bp)
app.register_blueprint(cardboard_bp)

@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (JS, CSS, etc.)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/foo')
def foo():
    return jsonify({"foo": "bar"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)