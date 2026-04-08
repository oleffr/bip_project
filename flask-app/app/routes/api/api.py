from flask import Blueprint
from flask import jsonify, redirect, url_for, request, session

api_routes = Blueprint('api', __name__)
from ..total_pages_functions import login_required
from ...models.data_bases.admins import Admins
from ...models.data_bases.user_lk import User_lk
from ...models.data_bases.users_emails import User_emails
#Чисто проверка, что api работает
@api_routes.route("/test", methods=["GET"])
def check_route_enable():
    return jsonify({"success":True, "status":"ok"})

#Временная заглушка для read операции админа
@api_routes.route("/get_user", methods=["POST"])
@login_required(role="admin")
def get_user_info():
    print(request.json)
    usrs = User_lk()
    if usrs.check_user_exist(request.json["username"]):
        return jsonify({"exists": True})
    return jsonify({"exists": False})

#Ну и вход/регистрация. Пока-на заглушках. После добавления ORM-вставить проверку существования и совпадения данных
@api_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    print(data)
    db_admins = Admins()
    db_users = User_lk()
    if db_admins.check_pass(data["username"], data["password"]):
        session["role"] = "admin"
        session["username"] = data["username"]
        return jsonify({'success':True,'redirect_url':'/admin/admin_lk'})
    elif db_users.check_pass(data["username"], data["password"])[0]==True:
        session["role"] = "user"
        session["username"] = data["username"]
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    return jsonify({'success':False})

@api_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    print(data)
    usrs = User_lk()
    if usrs.check_user_exist(data["username"]):
        return jsonify({'success':False, "message":"Unexpected error"})
    usrs.add_user({"username":data["username"], "password":data["password"]})
    return jsonify({'success':True,'redirect_url':'/user/user_lk'})

    if data["username"] == "admin":
        session['username'] = "admin"
        return jsonify({'success':True,'redirect_url':'/admin/admin_lk'})
    elif data["username"] == "user":
        session['username'] = "user"
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    return jsonify({'success':False, "message":"Unexpected error"})

@api_routes.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


"""Для тестов в endpoints ниже используются имена пользователей, а не id. В целом, на маленьких бд, без разницы"""
@api_routes.route("/emails", methods=["GET"])
@login_required(role="user")
def get_emails():
    emls = User_emails()
    data = emls.get_emails(session["username"])
    return jsonify([{"address":i} for i in data])


@api_routes.route("/add-email", methods=["POST"])
@login_required(role="user")
def add_email():
    emls = User_emails()
    emls.add_email(session["username"], request.json["email"], request.json["password"])
    return jsonify({"ok":True})

@api_routes.route("/delete-email", methods=["DELETE"])
@login_required(role="user")
def delete_emails():
    emls = User_emails()
    emls.delete_email(session["username"], request.json["email"])
    return jsonify({"ok":True})

