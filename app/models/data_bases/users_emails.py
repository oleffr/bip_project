import json
class User_emails():
    """
    primary_key-id пользователей (для скорости), почта (которую чистим)
    """
    data = list()
    def __init__(self):
        try:
            with open('User_emails.json', "r") as f:
                self.data = json.load(f)
        except Exception as e:
            pass

    def add_email(self, user_id, email, password):
        """По хорошему пара user_id-email должна бытьь уникальной"""
        self.data.append({"user":user_id, "email":email, "password": password})
        with open('User_emails.json', "w") as f:
                self.data = json.dump(self.data, f)

    def get_emails(self, user_id):
        out = []
        for i in self.data:
            if i["user"] == user_id:
                out.append(i["email"])
        return out
    
    def delete_email(self, user_id, email):
        position = -1
        for i in range(len(self.data)):
            if self.data[i]["user"] == user_id and self.data[i]["email"]==email:
                position = i
                break
        if position != -1:
            self.data.pop(position)
        with open('User_emails.json', "w") as f:
                self.data = json.dump(self.data, f)