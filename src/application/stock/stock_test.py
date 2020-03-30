from Stock import Stock
google = Stock('TSLA')
print("The current asking price for "+google.getTicker()+ " is "+str(google.getCurrentPrice()))
for i in range(100):
    print("The current asking price for "+google.getTicker()+ " is "+str(google.getAllInfo()))
