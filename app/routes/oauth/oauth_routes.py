from flask import Blueprint

oauth_routes = Blueprint('oauth', __name__)

@oauth_routes.route("/oauth_callback", metods=["GET"])
def oauth_callback():
    pass