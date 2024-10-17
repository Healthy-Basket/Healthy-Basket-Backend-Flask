from flask import Blueprint, request

fitbit = Blueprint('fitbit', __name__, url_prefix='/api/v1')