import json
import sqlite3
#import amberelectric
#from amberelectric.rest import ApiException
import utils as ut


with open("./config/config.json", "r") as f:
    config = json.load(f)

class DataLog:
    def __init__(self):
        self.db_path = config["Log_database"]["db_name"]
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_time TEXT,
            response_time TEXT,
            amber_time TEXT,
            price_estimate REAL)''')
        self.conn.commit()
        
    def create_table_amber(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs_amber
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_time TEXT,
            response_time TEXT,
            amber_time TEXT,
            price_estimate REAL,
            price_general REAL,
            price_feedin REAL,
            forecast_count INTEGER)''')
        self.conn.commit()


    def log_data(self, request_time, response_time, amber_time, price_estimate):
        self.cursor.execute('''INSERT INTO logs (request_time, response_time, amber_time, price_estimate)
            VALUES (?, ?, ?, ?)''', (request_time, response_time, amber_time, price_estimate))
        self.conn.commit()

    def log_amber_data(self, request_time, response_time, amber_data):
        self.cursor.execute('''INSERT INTO logs_amber (request_time, response_time, amber_time, price_estimate, price_general, price_feedin, forecast_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', (
            request_time,
            response_time,
            amber_data["current"]["general"].start_time.isoformat(),
            amber_data["current"]["general"].estimate,
            ut.format_cents_to_dollars(amber_data["current"]["general"].per_kwh),
            (ut.format_cents_to_dollars(amber_data["current"]["feed_in"].per_kwh * -1)),
            len(amber_data["forecasts"]["general"])))
        self.conn.commit()

    def __del__(self):
        self.conn.close()