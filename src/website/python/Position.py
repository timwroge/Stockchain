# Represents a Position that a user holds (parent of Long and Short)
class Position(object):
    def __init__(self, stock, shares, currentValue):
        self.stock = stock
        self.shares = shares
        self.currentValue = currentValue

    def getStock(self):
        return self.stock

    def getShare(self):
        return self.shares

    def getCurrentValue(self):
        return self.currentValue

    def setStock(self, newStock):
        self.stock = newStock

    def setShares(self, newShares):
        self.shares = newShares

    def setCurrentValue(self, newValue):
        self.currentValue = newValue
