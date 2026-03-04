from dataclasses import dataclass

from flask import request, session, url_for, redirect

from .api.api import api_routes
from .pages.admin_pages import admin_pages_routes
from .pages.user_pages import user_pages_routes
from .pages.general_pages import general_routes

@dataclass
class AppBlueprints:
    """
    Для удобства все blueprints собрал в dataclass, чтобы при добавлении путей в приложение не теряться
    """
    api = api_routes
    admin = admin_pages_routes
    user = user_pages_routes
    general = general_routes