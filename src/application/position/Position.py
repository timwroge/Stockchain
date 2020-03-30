class Position(object):
    def __init__(self):
        '''This is the user object'''
        self.UserId = UserId
        self.Username = Username
        self.FullName = FullName

    def getUserId(self):
        return self.UserId

    def setUserId(self, newUserId):
        self.UserId = newUserId

    def getUsername(self):
        return self.Username

    def setUsername(self, newUsername):
        self.Username = newUsername

    def getFullName(self):
        return self.FullName

    def setFullName(self, newFullName):
        self.FullName  = newFullName
