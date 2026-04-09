from flask import Blueprint
from flask import render_template
general_routes = Blueprint('general', __name__)


@general_routes.route("/", methods=["GET"])
def main_page():
    return render_template("/general/main_page.html")



@general_routes.route("/login", methods=["GET"])
def login():
    return render_template("/general/login_page.html")


@general_routes.route("/login", methods=["POST"])
def login_post():
    return render_template("/general/login_page.html")


@general_routes.route("/register", methods=["GET"])
def register():
    return render_template("/general/register.html")
