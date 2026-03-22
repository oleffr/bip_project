class User_lk:
    """
    Возможные поля через OAUTH. Просто оставлю как описание. Оставить можно чисто логин, имя, фамилию, адрес ЭП. Здесь считаем, что пользователи тут-только пользователи
    Без админов


    Логин, имя и фамилия, пол;
Портрет пользователя;
Адрес электронной почты;
Номер телефона;
Дата рождения.
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

    def check_pass(self, username, password):
        return True