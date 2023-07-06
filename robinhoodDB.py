import sqlite3
import pandas as pd
import os.path
from sqlite3 import Error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database = os.path.join(BASE_DIR, "robinhoodHistory.db") 

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

def create_table(conn, create_table_sql):
     try:
        c = conn.cursor()
        c.execute(create_table_sql)
     except Error as e:
        print(e)

def create_stock(conn, stock):
     sql = '''    INSERT INTO stocks(sym,begin_date,end_date,begin_price, end_price, num_shares, sell_allowed, crypto)
                  VALUES(?,?,?,?,?,?, ?, ?) ''' 
     cur = conn.cursor()
     cur.execute(sql, stock)
     conn.commit()
     return cur.lastrowid 

def delete_stock(conn, stockSym):
    sql = '''   DELETE FROM stocks WHERE sym = ? '''
    cur = conn.cursor()
    cur.execute(sql, (stockSym,))
    conn.commit()

def update_stock(conn, price, quantity, stock_id):
    sql = ''' UPDATE stocks SET begin_price = ?, num_shares = ?, end_date = 'NULL', sell_allowed = 1 where id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (price, quantity, stock_id))
    conn.commit()



def create_market(conn, marketName):
     sql = '''    INSERT INTO markets(marketName)
                  VALUES(?) ''' 
     cur = conn.cursor()
     cur.execute(sql, (marketName,))
     conn.commit()
     return cur.lastrowid 

def delete_market(conn, marketName):
    cur = conn.cursor()
    sql = '''   DELETE FROM markets WHERE marketName = ? '''
    cur.execute(sql, (marketName,))
    conn.commit()


def create_marketSym(conn, sym, marketId):
     sql = '''    INSERT INTO marketSymbols(sym, marketId)
                  VALUES(?,?) ''' 
     cur = conn.cursor()
     cur.execute(sql, (sym, marketId,))
     conn.commit()
     return cur.lastrowid 

def delete_marketSym(conn, marketSym):
    sql = '''   DELETE FROM marketSymbols WHERE sym = ? '''
    cur = conn.cursor()
    cur.execute(sql, (marketSym,))
    conn.commit()

def create_global_variable(conn, variable):
     sql = '''    INSERT INTO globalVariables(name,value) VALUES (?,?) ''' 
     cur = conn.cursor()
     cur.execute(sql, variable)
     conn.commit()

def delete_global_variable(conn, variableName):
    sql = '''   DELETE FROM globalVariables WHERE name = ? '''
    cur = conn.cursor()
    cur.execute(sql, (variableName,))
    conn.commit()

def update_global_variable(conn, value, variableName):
    sql = ''' UPDATE globalVariables SET value = ? where  name = ? '''
    cur = conn.cursor()
    cur.execute(sql, (value, variableName))
    conn.commit()

def create_day_trade(conn, day_trade):
     sql = '''    INSERT INTO dayTrades(day) VALUES (?) ''' 
     cur = conn.cursor()
     cur.execute(sql, (day_trade,))
     conn.commit()


def print_table(conn, tableName):
    sql = 'Select * FROM ' + tableName
    sql_result = execute_sql(conn, sql, True)
    for each in sql_result:
        message = ''
        for each2 in each:
            message = message + (str(each2)) +' | '
        print(message)

def execute_sql(conn, sql, needs_return_value,params=''):
    cur = conn.cursor()
    cur.execute(sql,params)
    conn.commit()
    if(needs_return_value):
        result = pd.DataFrame(cur.fetchall()).values.tolist()
        cur.close()
        return result
    cur.close()

def initiate_tables(conn):
    sql_create_stocks_table = """ CREATE TABLE IF NOT EXISTS stocks (
                                        id integer PRIMARY KEY,
                                        sym text NOT NULL,
                                        begin_date text NOT NULL,
                                        end_date text,
                                        begin_price real NOT NULL,
                                        end_price real,
                                        num_shares real,
                                        sell_allowed integer NOT NULL
                                    ); """    
    sql_create_markets_table = """ CREATE TABLE IF NOT EXISTS markets (
                                        id integer PRIMARY KEY,
                                        marketName text NOT NULL
                                        );"""
    sql_create_marketSymbols_table = """ CREATE TABLE IF NOT EXISTS marketSymbols (
                                        id integer PRIMARY KEY,
                                        sym text NOT NULL,
                                        marketId integer NOT NULL
                                    );"""
    sql_create_globalVariables_table = """ CREATE TABLE IF NOT EXISTS globalVariables (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        value integer NOT NULL
                                    );"""
    sql_create_dayTrades_table = """ CREATE TABLE IF NOT EXISTS dayTrades (
                                        id integer PRIMARY KEY,
                                        day text NOT NULL
                                    );"""

    create_table(conn, sql_create_stocks_table)
    create_table(conn, sql_create_markets_table)
    create_table(conn, sql_create_marketSymbols_table)
    create_table(conn, sql_create_globalVariables_table)
    create_table(conn, sql_create_dayTrades_table)
def main():
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # cur = conn.cursor()
        # sql = 'DROP TABLE dayTrades'
        # cur.execute(sql)
        # conn.commit()
        # initiate_tables(conn)
        # delete_market(conn,'crypto')
        # print_table(conn, 'globalVariables')
        # print_table(conn, 'marketSymbols')
        # print_table(conn, 'markets')
        print_table(conn,'marketSymbols')
        # cur = conn.cursor()
        # sql = 'SELECT sym FROM marketSymbols where marketId = ?'
        # cur.execute(sql, (2,))
        # print(cur.fetchall())
        # conn.commit()
        # print_table(conn, "stocks")
        # amount = len(cur.fetchall())
        # print(amount)
        
    else:
        print("Error! cannot create the database connection.")
    
    conn.close()
'''Used to create initial stocks table: 
    sql_create_stocks_table = """ CREATE TABLE IF NOT EXISTS stocks (
                                        id integer PRIMARY KEY,
                                        sym text NOT NULL,
                                        begin_date text NOT NULL,
                                        end_date text,
                                        begin_price real NOT NULL,
                                        end_price real
                                        sellAllowed integer NOT NULL
                                    ); """  
        create_table(conn, sql_create_stocks_table)
                                    '''


