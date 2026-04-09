from flask import Blueprint
from flask import jsonify, redirect, url_for, request, session

api_routes = Blueprint('api', __name__)
from ..total_pages_functions import login_required
from ...models.data_bases.admins import Admins
from ...models.data_bases.user_lk import User_lk

#Чисто проверка, что api работает
@api_routes.route("/test", methods=["GET"])
def check_route_enable():
    return jsonify({"success":True, "status":"ok"})

#Временная заглушка для read операции админа
@api_routes.route("/get_users_tokens", methods=["GET"])
@login_required(role="admin")
def get_user_info():
    usrs = User_lk()
    result = usrs.get_oauth_users()
    return jsonify({"result": True, "tokens": result})

#Ну и вход/регистрация. Пока-на заглушках. После добавления ORM-вставить проверку существования и совпадения данных
@api_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    print(data)
    db_admins = Admins()
    db_users = User_lk()
    if data["type"] == "oauth":
        db_users.add_user({"type":"oauth", "access_token":data["data"]["access_token"], "cid": data["data"]["cid"]})
        session["role"] = "user"
        print(data)
        session["username"] = data["data"]["access_token"]
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    elif db_admins.check_pass(data["username"], data["password"]):
        session["role"] = "admin"
        session["username"] = data["username"]
        return jsonify({'success':True,'redirect_url':'/admin/admin_lk'})
    elif db_users.check_pass(data["username"], data["password"])[0]==True:
        session["role"] = "user"
        session["username"] = data["username"]
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    return jsonify({'success':False})

@api_routes.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


