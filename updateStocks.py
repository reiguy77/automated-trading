import robin_stocks.robinhood as r
import sqlite3
from robinhoodDB import *
from datetime import date, datetime, timedelta, timezone

#Retrieve Robinhood information, update database		
def update_my_stocks(conn):
	# if(not stocks_updated_today(conn)):
		# r.deposit_funds_to_robinhood_account("https://api.robinhood.com/ach/relationships/9a53e307-a603-4780-af09-6b0e740325d5/", 10)
	my_stocks = r.build_holdings()
	update_current_stock_database(conn, my_stocks)
		# print("updated stocks and deposited $10")
	# my_crypto_stocks = r.get_crypto_positions()
	# update_current_crypto_stocks_database(conn, my_crypto_stocks)

# Check if stock database has been updated today
def stocks_updated_today(conn):
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	sql = 'SELECT value FROM globalVariables WHERE name = ?'
	cur.execute(sql,("last_stock_update_day",))
	curr_day_sql = [dict(row) for row in cur.fetchall()]
	if(len(curr_day_sql) == 0):
		last_stock_update = ("last_stock_update_day", date.today())
		create_global_variable(conn, last_stock_update)
		return False
	curr_day = datetime.strptime(curr_day_sql[0].get('value'), '%Y-%m-%d').date()
	if((curr_day-date.today()).days == 0):
		return True
	else:
		update_global_variable(conn, date.today(), "last_stock_update_day")
		return False

# updates the database in the case of purchases/sales not being complete
def update_current_stock_database(conn, my_stocks):     
	sql = 'UPDATE stocks SET sell_allowed = 0 where crypto = 0'
	cur = conn.cursor()
	cur.execute(sql) 
	conn.commit()  
	for key,value in my_stocks.items():
		conn.row_factory = sqlite3.Row
		sql = 'SELECT id, num_shares FROM stocks WHERE sym = ? and crypto = 0 ORDER BY id DESC LIMIT 1'
		cur = conn.cursor()
		cur.execute(sql, (key,))
		stock = [dict(row) for row in cur.fetchall()]
		quantity = value.get('quantity')
		price = value.get('average_buy_price')
		if(len(stock) > 0):
			curr_stock = stock[0]
			if(curr_stock.get("num_shares")!=quantity):
				update_stock(conn, price, quantity, stock[0].get("id"))
		else:
			stock_info = (key, date.today(),'NULL', price,'NULL', quantity, 1, 0)
			create_stock(conn, stock_info)

# updates the database in the case of crypto purchases/sales not being complete
def update_current_crypto_stocks_database(conn, my_crypto_stocks):
	sql = 'UPDATE stocks SET sell_allowed = 0 where crypto = 1'
	cur = conn.cursor()
	cur.execute(sql) 
	conn.commit()
	for crypto_stock in my_crypto_stocks:
		crypto_sym = crypto_stock.get('currency').get('code')
		quantity = float(crypto_stock.get('quantity'))
		if(quantity != 0):
			price = float(crypto_stock.get('cost_bases')[0].get('direct_cost_basis'))/float(quantity)
		else:
			continue
		conn.row_factory = sqlite3.Row
		sql = 'SELECT id, begin_price, num_shares FROM stocks WHERE sym = ? and crypto = 1 ORDER BY id ASC LIMIT 1'
		cur = conn.cursor()
		cur.execute(sql, (crypto_sym,))
		stock = [dict(row) for row in cur.fetchall()]
		if(len(stock) > 0):
			curr_stock = stock[0]
			if(curr_stock.get("num_shares")!=quantity):
				update_stock(conn, price, quantity, curr_stock.get("id"))
		else:
			print("crypto stock added to database: "+ crypto_sym)
			stock_info = (crypto_sym, date.today(),'NULL',price,'NULL', quantity, 1, 1)
			create_stock(conn, stock_info)
