from flask import Blueprint, request

auth = Blueprint('auth', __name__, url_prefix='/api/v1')