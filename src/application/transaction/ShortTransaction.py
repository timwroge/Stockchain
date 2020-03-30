import datetime as dt

class ShortTransaction(object):
    def __init__(self, time, shares, stock):
        '''This is the user object'''
        self.time = time
        self.shares = shares
        self.stock = stock

    def getTime(self):
        return self.time

    def setTime(self, newTime):
        self.time  = newTime

    def getShares(self):
        return self.shares

    def setShares(self, newShares):
        self.shares = newShares

    def getStock(self):
        return self.stock

    def setStock(self, newStock):
        self.stock = newStock

    def perform(self):
        self.price = self.shares * ( self.stock.getPrice() - self.getCurrentPrice() )
        return True
