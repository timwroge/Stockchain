from google.cloud import datastore
from datetime import datetime
import json

# must import the relevant objects
import sys
sys.path.insert(1, '/src/website/python')
from src.website.python import User

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

#adds a position for this user to the db
def add_position(user, item):
    # get datastore client
    client = get_client()

    # idea is to use a transaction that either gets the entity or creates it if there is none
    with client.transaction():
        # key is based on Position kind, datastore will give us an int identifier
        key = client.key('Position')

        # Make a Position entity for this item
        position = datastore.Entity(key)

        # User who owns the position (for query)
        position['username'] = user
        # the ticker
        position['Ticker'] = item.ticker
        # the positionType
        position['positionType'] = item.positionType
        # number of shares
        position['shares'] = item.shares
        # put item into datastore
        client.put(position)


# get json array of positions for this user, to return to the portfolio page
def get_positions(user):
    # get datastore client
    client = get_client()

    q = client.query(kind='Position')
    q.add_filter('Username', '=', user)

    positions = []
    # for each Position fetched, add it to array
    for position in q.fetch():
        positions.append({
            "shares": position['shares'],
            "stock_ticker": position['Ticker'],
            "type": position['positionType'],
            "value": 0
        })
    # value? -> value we need to get from stock data?

    # then we turn the entire array into JSON and send it to the client
    array_json = json.dumps(positions, indent=4) #, cls=dataClasses.ClothingEncoder)
    return array_json


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
            "stock_ticker" : historyItem['ticker'],
            "type" : historyItem['interactionType'],
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
        history['Ticker'] = item.ticker
        # the positionType
        history['positionType'] = item.positionType
        # number of shares
        history['shares'] = item.shares
        # price of stock
        history['price'] = item.price
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

    # only one user will be returned so this is all I need
    cash = q.fetch()['cash']

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
