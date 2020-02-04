from yfinance import Ticker
tsla = Ticker('TSLA')
print(tsla.ticker+" asking price: "+str(tsla.get_info()['ask']))

