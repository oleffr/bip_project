from flask import Blueprint
from flask import render_template, session

from ..total_pages_functions import login_required
user_pages_routes = Blueprint('user', __name__)


@user_pages_routes.route("/user_lk", methods=["GET"])
@login_required(role="user")
def check_route_enable():
    print(session["username"])
    return render_template("/user/index.html")