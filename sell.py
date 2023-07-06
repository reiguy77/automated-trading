import robin_stocks.robinhood as r
import sqlite3
import time
from robinhoodDB import *
from datetime import date, datetime, timedelta, timezone
import dateutil



stock_hopeful_returns = [1.01,1.00,.99]
stock_hopeful_days = [12,20]
crypto_hopeful_returns = [1.01, 1.00, .99]
crypto_hopeful_days = [2, 4]
count = 1


#Use stored values and current date to determine the hopeful return
def calculate_hopeful_return(start_date, curr_date, high_return, middle_return, low_return,high_days, middle_days):
	hopeful_return = high_return
	date_diff = (curr_date-start_date).days
	if (date_diff>high_days and date_diff<middle_days):
		hopeful_return = middle_return
	if(date_diff>middle_days):
		hopeful_return = low_return
	return hopeful_return

#Checks to see what stocks can be sold immediately
#Sells when market-price is 1% higher than buy-price within
#12 days, 0% within 20 days, and -1% til infinity
def check_to_sell(conn, general_market_open):
	global count
	my_stocks = r.build_holdings()
	for sym,value in my_stocks.items():
		if(count == 10):
			time.sleep(60)
			count = 1
		# start_date = datetime.strptime(s.get('begin_date'), '%Y-%m-%d').date()
		# curr_date = date.today()
		# if(s.get('crypto')==1):
		# 	handle_crypto_sale(conn, s,start_date,curr_date)

		# if (curr_date == start_date):
		# 	if(day_trade_allowed(conn, curr_date)):
		# 		if(handle_stock_sale(conn, s, start_date, curr_date, general_market_open)):
		# 			create_day_trade(conn, curr_date)
		# 	else:
		# 		continue
		
		# if(curr_date != start_date):
		handle_stock_sale(conn,sym, value,  general_market_open)

def check_to_sell_crypto(conn):
	global count
	my_stocks = r.get_crypto_positions()
	for stock in my_stocks:
		if(count == 10):
			time.sleep(60)
			count = 1
		handle_crypto_sale(conn,stock)
		

#Check to see if the day trade limit has been reached(3 in 5 days)
def day_trade_allowed(conn, curr_date):
	cur = conn.cursor()
	sql = 'SELECT * from(SELECT id, day FROM dayTrades ORDER BY id DESC LIMIT 3) order by id ASC'
	cur.execute(sql)
	day_trades = [dict(row) for row in cur.fetchall()]
	oldest_day_trade = datetime.strptime(day_trades[0].get('day'), '%Y-%m-%d').date()
	if ((curr_date - oldest_day_trade).days > 8):		
		return True
	else:
		return False
		
#Sell stock and update database		
def handle_stock_sale(conn, curr_sym, value, general_market_open):
	global count
	if(general_market_open):
		quantity = float(value.get('quantity'))
		start_price = float(value.get('average_buy_price'))
		if(start_price == 0):
			print("no begin price: ",curr_sym)
			return
		#priceType (str) – Can either be ‘ask_price’ or ‘bid_price’. If this parameter is set, then includeExtendedHours is ignored.
		temp_price = r.get_latest_price(curr_sym, None, True)[0]
		if(temp_price!=None):
			curr_price = float(temp_price)
		else:
			curr_price = 0 
		# hopeful_return = calculate_hopeful_return(start_date, curr_date, stock_hopeful_returns[0],stock_hopeful_returns[1],
		# 	stock_hopeful_returns[2],stock_hopeful_days[0],stock_hopeful_days[1])
		
		hopeful_return = 1.005
		curr_return = curr_price/start_price
		today = datetime.now()
		# Get rid of all stocks to start with a clean slate
		sell_no_matter_what = False
		if(today.day == 1 and today.month%2==1):
			sell_no_matter_what = True
		if curr_return >= hopeful_return or sell_no_matter_what:
			#could change to limit order, will make more complicated to ensure it is actually sold
			
			try:
				r.order_sell_fractional_by_quantity(curr_sym, quantity)
				print("normal sale: ",curr_sym, curr_return)
			except:
				return False
			# sql = """	UPDATE stocks SET end_date = ?, end_price = ?, num_shares = 0, sell_allowed = 0 WHERE id = ?"""
			# params = (curr_date, curr_price, stock.get("id"))
			# delete_stock(conn, curr_sym)
			# cur = conn.cursor()
			# cur.execute(sql, params)
			# conn.commit()
			count = count + 1
			return True
	else:
		return False

#sell crypto stock and update the database
def handle_crypto_sale(conn, stock):
	global count
	curr_sym = stock.get("currency").get("code")
	quantity = float(stock.get("quantity_available"))
	start_price = float(stock.get("cost_bases")[0].get("direct_cost_basis"))
	if(start_price == 0):
		print("no begin price: ",curr_sym)
		return
	start_price = start_price/quantity

	#priceType (str) – Can either be ‘ask_price’ or ‘bid_price’. If this parameter is set, then includeExtendedHours is ignored.
	temp_price = r.get_crypto_quote(curr_sym, info='bid_price')

	if(temp_price!=None):
		curr_price = float(temp_price)
	else:
		curr_price = 0 
	
	# hopeful_return = calculate_hopeful_return(start_date, curr_date, stock_hopeful_returns[0],stock_hopeful_returns[1],
	# 	stock_hopeful_returns[2],stock_hopeful_days[0],stock_hopeful_days[1])
	
	hopeful_return = 1.2
	curr_return = curr_price/start_price
	sell_no_matter_what = False
	today = datetime.now()
	if(today.day == 1 and today.month==10):
		sell_no_matter_what = True
	if curr_return >= hopeful_return or sell_no_matter_what:
		#could change to limit order, will make more complicated to ensure it is actually sold
		
		try:
			r.order_sell_crypto_by_quantity(curr_sym, quantity)
			print("crypto sale: ",curr_sym, curr_return)
		except:
			return False
		# sql = """	UPDATE stocks SET end_date = ?, end_price = ?, num_shares = 0, sell_allowed = 0 WHERE id = ?"""
		# params = (curr_date, curr_price, stock.get("id"))
		# delete_stock(conn, curr_sym)
		# cur = conn.cursor()
		# cur.execute(sql, params)
		# conn.commit()
		count = count + 1
		return True
	else:
		return False