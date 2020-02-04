import yfinance
class Stock(object):
    def __init__(self, ticker='TSLA'):
        self.ticker = ticker
        self.price = self.getCurrentPrice()
    def getCurrentPrice(self):
        ticker_socket = yfinance.Ticker(self.ticker)
        return ticker_socket.get_info()['ask']
    def getTicker(self):
        return self.ticker
    def getPrice(self):
        return self.price
