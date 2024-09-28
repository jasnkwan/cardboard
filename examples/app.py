"""
Example Flask App
"""

from flask import Flask, render_template
from cardboard import cardboard

app = Flask(__name__, template_folder="cardboard/templates")

# Register the Blueprint
app.register_blueprint(cardboard)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':

    app.run(debug=True)
