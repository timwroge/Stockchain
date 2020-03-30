import datetime as dt

class Position(object):
    def __init__(self, currentValue, shares, stock):
        '''This is the Position object'''
        self.shares = shares
        self.stock = stock
        self.currentValue = currentValue

    def getCurrentValue(self):
        return self.currentValue

    def setCurrentValue(self, newValue):
        self.currentValue  = newValue

    def getShares(self):
        return self.shares

    def setShares(self, newShares):
        self.shares = newShares

    def getStock(self):
        return self.stock

    def setStock(self, newStock):
        self.stock = newStock
