from google.cloud import datastore
from datetime import datetime
import json

# must import the relevant objects
import sys
sys.path.insert(1, '/src/website/python')
sys.path.insert(1, '/src/application/')
from src.website.python import User
from src.application.stock.Stock import Stock

# this is a helper class that main.py uses to handle calls to the datastore

# gets the datastore client object
def get_client():
    return datastore.Client()


# loads datastore key using given client, kind, and id if provided
def load_key(client, kind, entity_id=None, parent_key=None):
    # if we do not pass in an id, it is none, else it is what we set is as
    # id is the "name" (string or int) can be auto generated as an int if not given
    # the key is the identifier, which is made of a kind and a name(id)

    key = None
    if entity_id: #if we are given an id, use it
        key = client.key(kind, entity_id, parent=parent_key)
    else: # if we are not given an id, we will let datastore generate an int for us
        key = client.key(kind)
    return key


# Load a datstore entity using a particular client, and the ID.
def load_entity(client, kind, entity_id, parent_key=None):
    key = load_key(client, kind, entity_id, parent_key)
    entity = client.get(key)
    return entity


# writes this User and password hash to the datastore
def save_user(user, passwordhash):
    # get datastore client
    client = get_client()

    # create entity - needs a datastore key, which we get from load_key
    # pass in client, kind, id
    entity = datastore.Entity(load_key(client, 'User', user.email))

    # key is set, now set entity values from the user object and passwordhash
    entity['username'] = user.username
    entity['email'] = user.email
    entity['passwordhash'] = passwordhash
    entity['Cash'] = 1000.00

    # save the entity to the datastore
    client.put(entity)


# check the datastore for a user with matching username and passhash (hashword)
def load_user(email, passwordhash):
    # get datastore client
    client = get_client()

    # create a datastore query for kind username, with username and passhash filters
    q = client.query(kind='User')
    q.add_filter('email', '=', email)
    q.add_filter('passwordhash', '=', passwordhash)

    # call the query fetch and return User object if we find the user in datastore
    for user in q.fetch():
        return User.User(user['username'], user['email'])
    return None


# adds a position for this user to the db
def buy_position(user, position):
    # get datastore client
    client = get_client()

    with client.transaction():
        # query to see if they have a position already
        q = client.query(kind='Position')
        q.add_filter('Username', '=', user)
        q.add_filter('Ticker', '=', position['ticker'])
        q.add_filter('positionType', '=', position['positionType'])

        # get the matching user entity
        results = list(q.fetch())
        pos = None
        cost = int(position['shares']) * int(position['currVal'])
        # ensure that they have enough money
        if(cost <= json.loads(get_cash(user))):
            if results:
                print("Buying more shares of an existing position")
                # if there is an existing position, set the entity
                pos = results[0]
                nShares = int(position['shares']) + pos['shares']
                pos.update({
                    'shares': nShares
                })
            else:
                print("Buying a new position")
                # if there is no existing position, we will create one
                key = client.key('Position')
                pos = datastore.Entity(key)
                pos.update({
                    'Username': user,
                    'Ticker': position['ticker'],
                    'positionType': position['positionType'],
                    'shares': int(position['shares'])
                })

            client.put(pos)
            history_dict = \
                    { \
                    "ticker": position['ticker'], \
                    "positionType" : 'Long', \
                    "interactionType" : 'Buy', \
                    "shares" : position['shares'] , \
                    "price" :  position['currVal']\
                    }
            add_history(user, history_dict)

            # make a call that removes the money they spent
            if(int(position['shares']) > 0):
                print("Removing $", cost, " from users account for ", int(position['shares']), " at $", int(position['currVal']), " per share")
                add_cash(user, str(cost*-1))
        else:
            print("Insufficient funds")

# adds a position for this user to the db
def short_position(user, position):
    # get datastore client
    client = get_client()

    with client.transaction():
        # query to see if they have a position already
        q = client.query(kind='Position')
        q.add_filter('Username', '=', user)
        q.add_filter('Ticker', '=', position['ticker'])
        q.add_filter('positionType', '=', position['positionType'])

        # get the matching user entity
        results = list(q.fetch())
        pos = None
        cost = 0
        if results:
            if results:
                print("Buying more shares of an existing position")
                # if there is an existing position, set the entity
                pos = results[0]
                nShares = int(position['shares']) + pos['shares']
                pos.update({
                    'shares': nShares
                })
        else:
            print("Shorting a new position")
            # if there is no existing position, we will create one
            key = client.key('Position')
            pos = datastore.Entity(key)
            pos.update({
                'Username': user,
                'Ticker': position['ticker'],
                'positionType': position['positionType'],
                'shares': int(position['shares'])
            })

        client.put(pos)
        history_dict = \
                { \
                "ticker": position['ticker'], \
                "positionType" : 'Short', \
                "interactionType" : 'Buy', \
                "shares" : position['shares'] , \
                "price" :  position['currVal']\
                }
        add_history(user, history_dict)


# attempts a sell of the given position
def sell_position(user, position):
    # get datastore client
    client = get_client()

    # want to sell shares amount of ticker stock positions that they own for shares*currVal

    with client.transaction():
        # query to see if they own this position 
        q = client.query(kind='Position')
        q.add_filter('Username', '=', user)
        q.add_filter('Ticker', '=', position['ticker'])
        q.add_filter('positionType', '=', "Long")

        # get the matching user entity
        results = list(q.fetch())
        earnings = 0
        nShares = -1
        pos = None

        if results:
            print("Selling shares of an existing position")
            # if there is an existing position we can sell shares
            pos = results[0]
            if(pos['shares'] >= int(position['shares'])):
                # extra check that they have enough shares - this should be verified already
                # decrement amount of shares they have left, get earnings
                nShares = pos['shares'] - int(position['shares'])
                earnings = int(position['shares']) * int(position['currVal'])
                # update the position
                pos.update({
                    'shares': nShares
                })
                # write back
                client.put(pos)
                # ticker, positionType, shares, price
                history_dict = \
                        { \
                        "ticker": position['ticker'], \
                        "positionType" : 'Long', \
                        "interactionType" : 'Sell', \
                        "shares" :  position['shares'], \
                        "price" :  position['currVal']\
                        }
                add_history(user, history_dict) 


        #if nshares is 0, they sold all their shares, we can delete this position
        if(nShares == 0):
            print("Sold position has no more shares, deleting position")
            client.delete(pos.key)
        # and add the cash to their account
        if(earnings > 0):
            print("Adding $", earnings, " to users account")
            add_cash(user, str(earnings))

#this will take a whole position passed in and pass back out the position with the actual short value I guess
def get_short_value(user, position, current_price):
     # get datastore client
    client = get_client()

    # want to sell shares amount of ticker stock positions that they own for shares*currVal

    # before we do anything, we need to query the history table to find all the previous buys and sells of short positions
    # need to do this because may have bought 3 sold 2 and then bought more, so each needs to be sold at correct price
    q = client.query(kind='History')
    q.add_filter('username', '=', user)
    q.add_filter('ticker', '=', position['Ticker'])
    q.add_filter('positionType', '=', "Short")
    #q.order('-interactionTime')

    res1 = list(q.fetch())

    # this is a count for the amount it cost at buying
    totalAmm = 0
    totalShares = int(position['shares'])

    if res1:
        # then you look at the most recent by time and see if you have enough to sell just those and loop down while adding value!
        for el in res1:
            if totalShares > 0:
                print(" interactionType" + el['interactionType'])
                if el['interactionType'] == 'Buy' :
                    print("buy")
                    totalShares -= int(el['shares']) #idk why I have to do this???
                    if totalShares >= 0 : 
                        totalAmm += float(el['shares'])*el['price']
                    else:
                        totalAmm += (totalShares + (int(el['shares']))) * el['price']
        # This computes the amount that the user profits from this transaction
        print(totalAmm)
        netVal = totalAmm - current_price*int(position['shares'])
        print(netVal)
    else:
        print("nothing in query")
        #print(position['ticker'])
        netVal = 0

    return netVal



def sell_short_position(user, position):
    # get datastore client
    client = get_client()

    # want to sell shares amount of ticker stock positions that they own for shares*currVal

    # before we do anything, we need to query the history table to find all the previous buys and sells of short positions
    # need to do this because may have bought 3 sold 2 and then bought more, so each needs to be sold at correct price
    q = client.query(kind='History')
    q.add_filter('username', '=', user)
    q.add_filter('ticker', '=', position['ticker'])
    q.add_filter('positionType', '=', "Short")
    #q.order('-interactionTime')

    res1 = list(q.fetch())

    # this is a count for the amount it cost at buying
    totalAmm = 0
    totalShares = int(position['shares'])

    if res1:
        # then you look at the most recent by time and see if you have enough to sell just those and loop down while adding value!
        for el in res1:
            if totalShares > 0:
                print(" interactionType" + el['interactionType'])
                if el['interactionType'] == 'Buy' :
                    print("buy")
                    totalShares -= int(el['shares']) #idk why I have to do this???
                    if totalShares >= 0 : 
                        totalAmm += float(el['shares'])*el['price']
                    else:
                        totalAmm += (totalShares + (int(el['shares']))) * el['price']
        # This computes the amount that the user profits from this transaction
        print(totalAmm)
        netVal = totalAmm - position['currVal']*int(position['shares'])
        print(netVal)
    else:
        print("nothing in query")
        print(position['ticker'])
        netVal = 0


    with client.transaction():

        # query to see if they own this position 
        q = client.query(kind='Position')
        q.add_filter('Username', '=', user)
        q.add_filter('Ticker', '=', position['ticker'])
        q.add_filter('positionType', '=', "Short")

        # get the matching user entity
        results = list(q.fetch())
        earnings = 0
        nShares = -1
        pos = None

        if results:
            print("Selling shares of an existing position")
            # if there is an existing position we can sell shares
            pos = results[0]
            if(pos['shares'] >= int(position['shares'])):
                # extra check that they have enough shares - this should be verified already
                # decrement amount of shares they have left, get earnings
                nShares = int(pos['shares']) - int(position['shares'])
                # update the position
                pos.update({
                    'shares': nShares
                })
               # write back
                client.put(pos)
                # ticker, positionType, shares, price
                history_dict = \
                        { \
                        "ticker": position['ticker'], \
                        "positionType" : 'Short', \
                        "interactionType" : 'Sell', \
                        "shares" :  int(position['shares']), \
                        "price" :  float(position['currVal'])\
                        }
                add_history(user, history_dict) 

                #if nshares is 0, they sold all their shares, we can delete this position
                if(nShares == 0):
                    print("Sold position has no more shares, deleting position")
                    client.delete(pos.key)

                # here
                # may want to add caveat where if they are gonna go negative then just reduce to 0 dollars!
                
                print("Adding $", netVal, " to users account")
                add_cash(user, str(netVal))
        else:
            print("Position does not exist, no shares to sell")

        
        



# get json array of positions for this user, to return to the portfolio page
def get_positions(user):
    # get datastore client
    client = get_client()

    q = client.query(kind='Position')
    q.add_filter('Username', '=', user)

    positions = []

    # for each Position fetched, add it to array
    for position in q.fetch():
        current_stock = Stock(position['Ticker'])
        current_price = current_stock.getCurrentPrice()
        if position['positionType'] == "Short" :
            #call the find real value
            total_price = get_short_value(user, position, current_price)
        else:
            total_price = current_price*position['shares']
        positions.append({
            "shares": position['shares'],
            "ticker": position['Ticker'],
            "type": position['positionType'],
            "value": "${0:.2f}".format(total_price)
        })
    # value? -> value we need to get from stock data?

    # then we turn the entire array into JSON and send it to the client
    array_json = json.dumps(positions, indent=4) #, cls=dataClasses.ClothingEncoder)
    return array_json

# get json array of positions for this user, to return to the portfolio page
def get_portfolio_value(user):
    # get datastore client
    client = get_client()

    q = client.query(kind='Position')
    q.add_filter('Username', '=', user)

    positions = []

    # for each Position fetched, add it to array
    total_value = 0
    for position in q.fetch():
        current_stock = Stock(position['Ticker'])
        current_price = current_stock.getCurrentPrice()
        if position['positionType'] == "Short" :
            #call the find real value
            total_price = get_short_value(user, position, current_price)
        else:
            total_price = current_price*position['shares']
        total_value += total_price

    # value? -> value we need to get from stock data?
    # then we turn the entire array into JSON and send it to the client
    return json.dumps(total_value)

# gets all transactions for this user's transaction history
def get_history(user):
    # get datastore client
    client = get_client()

    q = client.query(kind='History')
    q.add_filter('username', '=', user)

    history = []
    # of positions fetched
    for historyItem in q.fetch():
        history.append({
            "time" : historyItem['interactionTime'],
            "shares" : historyItem['shares'],
            "ticker" : historyItem['ticker'],
            "positionType" : historyItem['positionType'],
            "interactionType" : historyItem['interactionType'],
            "value" : historyItem['price']
        })

    array_json = json.dumps(history, indent=4, default=str)
    return array_json


#adds a history element for this user to the db
def add_history(user, item):
    # get datastore client
    client = get_client()
    

    # idea is to use a transaction that either gets the entity or creates it if there is none
    with client.transaction():
        # key is based on Position kind, datastore will give us an int identifier
        key = client.key('History')

        # Make a Position entity for this item
        history = datastore.Entity(key)

        # User who owns the position (for query)
        history['username'] = user
        # the ticker
        history['ticker'] = item["ticker"]
        # the positionType
        history['positionType'] = item["positionType"]
        # number of shares
        history['shares'] = item["shares"]
        # price of stock
        history['price'] = item["price"]

        history['interactionType'] = item["interactionType"]
        # get datetime
        history['interactionTime'] = datetime.now()

        # put item into datastore

        client.put(history)


#return the user's cash amount
def get_cash(user):
    #get datastore client
    client = get_client()

    q = client.query(kind = 'User')
    q.add_filter('username', '=', user)

    # get the matching user entity
    results = list(q.fetch())
    usr = results[0]
    cash = usr['Cash']

    print("Cash is ", cash)

    # I hope that this still works? not srue if anything is different about this
    cash_string = json.dumps(cash, indent=4)
    return cash_string


# This will take in a cash amount and user and add it to the amount in the datbase!
def add_cash(user, cash):
    # get datastore client
    client = get_client()

    # creates a query based on the data
    q = client.query(kind='User')
    q.add_filter('username', '=', user)

    # our fancy currency input is a string, so need to remove the , and $ that it adds in so we can make this a float
    cash_as_fp = float(cash.replace(',','').replace('$',''))

    # get the matching user entity
    results = list(q.fetch())
    usr = results[0]

    # update cash amount with existing amount
    newCash = cash_as_fp + usr['Cash']

    # update entity
    usr.update({
        'Cash': newCash
    })

    # write back
    client.put(usr)


#remove position
def remove_position(user, ticker):
    #get datastore client
    client = get_client()

    #creates a query based on the data
    q = client.query(kind='Position')
    q.add_filter('username', '=', user)
    q.add_filter('ticker', '=', ticker)


    for item in q.fetch():
        # I don't think this can be more than one
        client.delete(item.key)
        break
    
    #I was confused why this code was here
    q = client.query(kind='Position')
    q.add_filter('username', '=', user)
    q.add_filter('ticker', '=', ticker)

# update position 
# I am not sure what obj will be passed into this
def update_position(user, ticker, shares):
    #get datastore client
    client = get_client()

    #creates a query based on the data
    q = client.query(kind='Position')
    q.add_filter('username', '=', user)
    q.add_filter('ticker', '=', ticker)

    # This will only return one, but I am not sure what q.fetch returns
    for pos in q.fetch():
        # I don't think this can be more than one
        task = client.get(pos.key)
        currShares = task[shares]
        task[shares] = currShares + shares
        break


    client.put(task)
