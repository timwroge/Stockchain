# The User object. Has a username and email
class User(object):
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
        }
