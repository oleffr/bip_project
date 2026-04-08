class Admins:
    """
    Отдельно класс для таблицы с админами. Пока считаем, что админы "статичны"
"""
    data = [{"username":"admin", "password":"admin"}]
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
    def check_pass(self, username, password):
        for i in self.data:
            if i["username"] == username:
                if i["password"] == password:
                    return True
        return False