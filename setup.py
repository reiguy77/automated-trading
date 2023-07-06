from robinhoodDB import *
import robin_stocks.robinhood as r
import sqlite3
import requests
from datetime import date, datetime, timedelta, timezone
from requests import Session

# Keeps track on if the user is logged in or not.
LOGGED_IN = False
# The session object for making get and post requests.
SESSION = Session()
SESSION.headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "en-US,en;q=1",
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "X-Robinhood-API-Version": "1.315.0",
    "Connection": "keep-alive",
    "User-Agent": "*"
}

markets = ['healthcare','energy', 'technology','biopharmaceutical',
		'real-estate', 'banking', 'automotive', 'china' ,'uk','canada',
		'apparel','food','alcohol','travel','metal','oil','agriculture',
		'media','mining', 'hotel','retail','aerospace','construction',
		'education','entertainment','etf']

#Initiate day trade information	
def add_day_trade_information(conn):
	create_day_trade(conn, date.today() - timedelta(days=0))
	create_day_trade(conn, date.today() - timedelta(days=0))

def add_last_stock_update_day(conn):
	curr_market = ("last_stock_update_day", date.today() - timedelta(days=1))
	create_global_variable(conn, curr_market)

def add_curr_market_id(conn):
	curr_market = ("curr_market_id", 1)
	create_global_variable(conn, curr_market)
	
#Add all markets and their associated stock symbols to the database
def add_markets(conn):
	count = 1
	for market in markets:
		create_market(conn, market)
		url = market_category_url(market)
		data = request_get(url, 'regular')
		data = filter_data(data, 'instruments')  
		symbols = [get_symbol_by_url(x) for x in data]  
		for stock in symbols:
			create_marketSym(conn, stock, count)
		count = count + 1
	add_crypto_market(conn)

#Add crypto market and associated symbols to database
def add_crypto_market(conn):
	database_id = create_market(conn, 'crypto')
	crypto_currencies = r.get_crypto_currency_pairs()
	for currency in crypto_currencies:
		if(currency.get('tradability') == 'tradable'):
			create_marketSym(conn, currency.get('symbol').replace('-USD', ''), database_id)
#Setup database
def setup(conn):
	sql = "DROP TABLE markets"
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()
	sql = "DROP TABLE marketSymbols"
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()
	sql = "DROP TABLE globalVariables"
	cur = conn.cursor()
	cur.execute(sql)
	conn.commit()
	initiate_tables(conn)
	add_markets(conn)
	# add_day_trade_information(conn)
	# add_curr_market_id(conn)
	# add_last_stock_update_day(conn)

def market_category_url(category):
    return('https://api.robinhood.com/midlands/tags/tag/{}/'.format(category))
def request_get(url, dataType='regular', payload=None, jsonify_data=True):
    """For a given url and payload, makes a get request and returns the data.
    :param url: The url to send a get request to.
    :type url: str
    :param dataType: Determines how to filter the data. 'regular' returns the unfiltered data. \
    'results' will return data['results']. 'pagination' will return data['results'] and append it with any \
    data that is in data['next']. 'indexzero' will return data['results'][0].
    :type dataType: Optional[str]
    :param payload: Dictionary of parameters to pass to the url. Will append the requests url as url/?key1=value1&key2=value2.
    :type payload: Optional[dict]
    :param jsonify_data: If this is true, will return requests.post().json(), otherwise will return response from requests.post().
    :type jsonify_data: bool
    :returns: Returns the data from the get request. If jsonify_data=True and requests returns an http code other than <200> \
    then either '[None]' or 'None' will be returned based on what the dataType parameter was set as.
    """
    if (dataType == 'results' or dataType == 'pagination'):
        data = [None]
    else:
        data = None
    res = None
    if jsonify_data:
        try:
            res = SESSION.get(url, params=payload)
            res.raise_for_status()
            data = res.json()
        except (requests.exceptions.HTTPError, AttributeError) as message:
            print(message, file=get_output())
            return(data)
    else:
        res = SESSION.get(url, params=payload)
        return(res)
    # Only continue to filter data if jsonify_data=True, and Session.get returned status code <200>.
    if (dataType == 'results'):
        try:
            data = data['results']
        except KeyError as message:
            print("{0} is not a key in the dictionary".format(message), file=get_output())
            return([None])
    elif (dataType == 'pagination'):
        counter = 2
        nextData = data
        try:
            data = data['results']
        except KeyError as message:
            print("{0} is not a key in the dictionary".format(message), file=get_output())
            return([None])

        if nextData['next']:
            print('Found Additional pages.', file=get_output())
        while nextData['next']:
            try:
                res = SESSION.get(nextData['next'])
                res.raise_for_status()
                nextData = res.json()
            except:
                print('Additional pages exist but could not be loaded.', file=get_output())
                return(data)
            print('Loading page '+str(counter)+' ...', file=get_output())
            counter += 1
            for item in nextData['results']:
                data.append(item)
    elif (dataType == 'indexzero'):
        try:
            data = data['results'][0]
        except KeyError as message:
            print("{0} is not a key in the dictionary".format(message), file=get_output())
            return(None)
        except IndexError as message:
            return(None)

    return(data)

def filter_data(data, info):
    """Takes the data and extracts the value for the keyword that matches info.
    :param data: The data returned by request_get.
    :type data: dict or list
    :param info: The keyword to filter from the data.
    :type info: str
    :returns:  A list or string with the values that correspond to the info keyword.
    """
    if (data == None):
        return(data)
    elif (data == [None]):
        return([])
    elif (type(data) == list):
        if (len(data) == 0):
            return([])
        compareDict = data[0]
        noneType = []
    elif (type(data) == dict):
        compareDict = data
        noneType = None

    if info is not None:
        if info in compareDict and type(data) == list:
            return([x[info] for x in data])
        elif info in compareDict and type(data) == dict:
            return(data[info])
        else:
            print(error_argument_not_key_in_dictionary(info), file=get_output())
            return(noneType)
    else:
        return(data) 
def get_symbol_by_url(url):
    """Returns the symbol of a stock from the instrument url. Should be located at ``https://api.robinhood.com/instruments/<id>``
    where <id> is the id of the stock.
    :param url: The url of the stock as a string.
    :type url: str
    :returns: [str] Returns the ticker symbol of the stock.
    """
    data = request_get(url)
    return filter_data(data, info='symbol')

conn = create_connection(database)
# setup(conn)