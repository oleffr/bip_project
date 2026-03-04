from flask import Blueprint
from flask import render_template, session

from ..total_pages_functions import login_required

admin_pages_routes = Blueprint('admin', __name__)


@admin_pages_routes.route("/admin_lk", methods=["GET"])
@login_required(role="admin")
def admin_lk():
    print(session["username"])
    return render_template("/admin/index.html")