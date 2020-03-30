import yfinance
class Stock(object):
    def __init__(self, ticker='TSLA'):
        self.ticker = ticker
        self.price = 1
    def getCurrentPrice(self):
        # new = Stock(self.ticker)
        # del self
        # self = new
        ticker_socket = yfinance.Ticker(self.ticker)
        price = ticker_socket.get_info()['ask']
        return price
    def getTicker(self):
        return self.ticker
    def getPrice(self):
        return self.price

    def getAllInfo(self):
        ticker_socket = yfinance.Ticker(self.ticker)
        data = ticker_socket.get_info()
        return data
