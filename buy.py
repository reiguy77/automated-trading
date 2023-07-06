import robin_stocks.robinhood as r
import sqlite3
import time
from robinhoodDB import *
from datetime import date, datetime, timedelta, timezone
import dateutil
import random
import time
from random import choices

markets = ['healthcare','energy', 'technology','biopharmaceutical',
		'real-estate', 'banking', 'automotive', 'china' ,'uk','canada',
		'apparel','food','alcohol','travel','metal','oil','agriculture',
		'media','mining', 'hotel','retail','aerospace','construction',
		'education','entertainment','etf']

crypto_market_id = len(markets)+1
total_markets = len(markets)+1
		
#Use available funds to buy new stocks
def buy_new_stocks(conn, total_cash, general_market_open):
	time.sleep(60)
	if(total_cash>=total_markets*10):
		num_markets = total_markets
	else:
		num_markets = round(total_cash/10)
	price_amount = total_cash/num_markets
	cur = conn.cursor()
	success_count = 0
	market_count = 0
	count = 1
	curr_market_id = random.randrange(1,total_markets)
	while(market_count < total_markets + 1  and success_count < num_markets + 1):
		if(count == 10):
			time.sleep(60)
			count = 0
		curr_market_id = (curr_market_id) % (total_markets) + 1
		sql = 'SELECT sym FROM marketSymbols where marketId = ?'
		cur.execute(sql, (curr_market_id,))
		symbols = cur.fetchall()
		randomNum = random.randrange(1,len(symbols))
		randomSym = symbols[randomNum][0]
		try:
			if(curr_market_id == crypto_market_id):
				# continue
				# sql = 'SELECT id FROM stocks where sym = ? and crypto = 1 and sell_allowed = 1 '
				# cur.execute(sql, (randomSym,))
				# stock = [dict(row) for row in cur.fetchall()]
				# if(len(stock) == 0):
				buy_info = r.order_buy_crypto_by_price(randomSym, price_amount)
				# 	crypto = 1
				# else:
				# 	continue
			elif(general_market_open):
				buy_info = r.order_buy_fractional_by_price(randomSym, price_amount)
				crypto = 0
			else:
				market_count = market_count + 1
				continue
		except Exception as e:
			print(e)
			# delete_marketSym(conn, randomSym)
			# print(randomSym,' is deleted')
			market_count = market_count + 1
			continue
		count = count + 1
		market_count = market_count + 1
		# stock_info = (randomSym, date.today(),'NULL',buy_info.get('price'),'NULL', buy_info.get('quantity'), 1, crypto)
		# delete_stock(conn, randomSym)
		if (buy_info.get('price') != None):
			success_count = success_count + 1
			print("buy: ", randomSym, buy_info.get('quantity'), buy_info.get('price'))
			# create_stock(conn, stock_info)
	update_global_variable(conn, curr_market_id, "curr_market_id")
	