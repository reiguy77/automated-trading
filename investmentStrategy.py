# import robin_stocks.robinhood as r
import pyotp
import signal
import sqlite3
import random
import time
from random import choices
from robinhoodDB import *
from loginInformation import *
from setup import *
from sell import *
from buy import *
from updateStocks import *
from datetime import date, datetime, timedelta, timezone
import dateutil

# Logs user in
def login_to_robinhood():
	totp = pyotp.TOTP(getTOTPCode()).now()
	login = r.login(getUsername(), getPassword(), mfa_code=totp)
def handler(signum, frame):
    print("Forever is over!")
    raise Exception("end of time")
#Buy and Sell commands to be run daily
def daily_run(conn):
	market_hours = r.get_market_today_hours('XNYS')
	general_market_open = True
	if(market_hours.get('is_open')==False):
		general_market_open = False
	else:
		curr_time = dateutil.parser.parse(datetime.now(timezone.utc).isoformat())
		open_time =dateutil.parser.parse( market_hours.get("opens_at"))
		close_time = dateutil.parser.parse(market_hours.get("closes_at"))
		if(curr_time>=open_time and curr_time<=close_time):
			general_market_open = True
		else:
			general_market_open = False

	
	check_to_sell(conn, general_market_open)
	check_to_sell_crypto(conn)
	total_cash = float(r.load_account_profile("crypto_buying_power"))-200
	if(total_cash>10):
		buy_new_stocks(conn, total_cash, general_market_open)

def main():
	login_to_robinhood()
	print('yo')
	conn = create_connection(database)
	if(conn is not None):
		daily_run(conn)
		conn.close()
	else:
		print("Error! cannot create the database connection.")
main()




