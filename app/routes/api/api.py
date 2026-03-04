from flask import Blueprint
from flask import jsonify, redirect, url_for, request, session

api_routes = Blueprint('api', __name__)
from ..total_pages_functions import login_required
#Чисто проверка, что api работает
@api_routes.route("/ping", methods=["GET"])
def check_route_enable():
    return jsonify({"status":"ok"})

#Временная заглушка для read операции админа
@api_routes.route("/get_user", methods=["POST"])
@login_required(role="admin")
def get_user_info():
    print(request.json)
    return jsonify({"exists": True})

#Ну и вход/регистрация. Пока-на заглушках. После добавления ORM-вставить проверку существования и совпадения данных
@api_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    print(data)
    if data["username"] == "admin" and data["password"] == "admin":
        return jsonify({'success':True,'redirect_url':'/admin/admin_lk'})
    elif data["username"] == "user" and data["password"] == "user":
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    return jsonify({'success':False})

@api_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    print(data)
    if data["username"] == "admin":
        session['username'] = "admin"
        return jsonify({'success':True,'redirect_url':'/admin/admin_lk'})
    elif data["username"] == "user":
        session['username'] = "user"
        return jsonify({'success':True,'redirect_url':'/user/user_lk'})
    return jsonify({'success':False})