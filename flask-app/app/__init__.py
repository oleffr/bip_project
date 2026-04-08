from flask import Flask

from .routes import AppBlueprints

import secrets
from datetime import timedelta
class App:
    def __init__(self):
        self.bp = AppBlueprints
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(16)
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
        """
        Ниже идет установка префиксов до нужных страниц. Все разбиты на 4 группы, представленные ниже
        Пример обращения: http://localhost:5000/admin/admin_lk
        Все пути находятся в папке routes
        """
        self.app.register_blueprint(self.bp.admin, url_prefix = "/admin")
        self.app.register_blueprint(self.bp.user, url_prefix = "/user")
        self.app.register_blueprint(self.bp.general, url_prefix = "/")
        self.app.register_blueprint(self.bp.api, url_prefix = "/api")
        self.app.register_blueprint(self.bp.oauth, url_prefix = "/oauth")
    
    def run_app(self, host = "localhost", port=5000):
        self.app.run(host=host, port=port)
