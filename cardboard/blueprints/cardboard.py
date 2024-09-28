from flask import render_template


def register_routes(blueprint):
    @blueprint.route('/board')
    def board():
        return render_template('test.html')
    