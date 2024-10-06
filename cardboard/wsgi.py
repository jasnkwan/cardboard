"""
WSGI app
"""


from cardboard.server import app
import os


if __name__ == "__main__":
    HOST = os.environ.get("HOST", default="127.0.0.1")
    PORT = int(os.environ.get("PORT", default="5000"))
    DEBUG = bool(os.environ.get("DEBUG", default="False"))
    
    app.run(host=HOST, port=PORT, debug=DEBUG)