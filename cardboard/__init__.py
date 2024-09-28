"""
Initialize the package and setup Blueprints.
"""

from flask import Blueprint
from .blueprints.cardboard import register_routes
# Create a Blueprint named 'cardboard'
cardboard = Blueprint(
    'cardboard',
    __name__,
    template_folder='templates'
)

register_routes(cardboard)