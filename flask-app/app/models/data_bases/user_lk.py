import json
class User_lk:
    """
    Возможные поля через OAUTH. Просто оставлю как описание. Оставить можно чисто логин, имя, фамилию, адрес ЭП. Здесь считаем, что пользователи тут-только пользователи
    Без админов

ID(primary_key),Электронная почта(primary_key), логин, имя, фамилия, пол, картинка
"""
    data = list()
    def __init__(self):
        try:
            with open('Users_data.json', "r") as f:
                self.data = json.load(f)
        except Exception as e:
            pass


    def check_user_exist(self, username:str):
        """
        username: primary key. В перспективе-изменится под oauth
        """
        for i in self.data:
            if i["username"] == username:
                return True
        return False

    def add_user(self, user_data: dict):
        """
        data-словарь с данными о пользователе
        ! пока чисто username-password
        """
        if not self.check_user_exist(user_data["username"]):
            self.data.append({"username":user_data["username"], "password":user_data["password"]})   
            with open('Users_data.json', "w") as f:
                self.data = json.dump(self.data, f)    


    def delete_user(self, username: str):
        position = -1
        for i in range(len(self.data)):
            if self.data[i]["username"] == username:
                position = i
                break
        if position != -1:
            self.data.pop(position)
        with open('Users_data.json', "w") as f:
                self.data = json.dump(self.data, f)

    def check_pass(self, username, password):
        for i in self.data:
            if i["username"] == username:
                if i["password"] == password:
                    return (True,)
                else:
                    return (False, "Incorrect pass")
        return (False, "Not exist")