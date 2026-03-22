class Admins:
    """
    Отдельно класс для таблицы с админами
"""
    def __init__(self):
        pass

    def check_user_exist(self, username:str):
        """
        username: primary key. В перспективе-изменится под oauth
        """
        pass
    def add_user(self, user_data: dict):
        """
        data-словарь с данными о пользователе
        """
        pass
    def delete_iser(self, username: str):
        pass

    def __contains__(self, item):
        #Method in
        if item == "admin":
            return True
        return False
    def check_pass(self, username, password):
        pass