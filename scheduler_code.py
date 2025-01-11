import json
from datetime import datetime as dt
import time as time
from apscheduler.schedulers.background import BackgroundScheduler
import Amberloop as al
import datalog as dl
import homeassistant as ha
import amber2mqtt as a2m

with open("./config/config.json", "r") as f:
    config = json.load(f)

amberSiteId = config["amber"]["site_id"]
amberApiToken   = config["amber"]["access_token"]
amberPriceSeconds = config["amber"]["amber5minPrice_seconds"]
amberPriceMinutes = config["amber"]["amber5minPrice_minutes"]
log_5min_values = False
log_5min_forecasts = False
if config["Log_database"]["log_amber_5min_current_values"].lower() == "true":
    log_5min_values = True
if config["Log_database"]["log_amber_5min_forecasts"].lower() == "true":
    log_5min_forecasts = True
    
amberEstimatePrice = True
amber2mqtt = True if config["integration"]["amber2mqtt"].lower() == "true" else False
home_assistant = True if config["integration"]["home_assistant"].lower() == "true" else False


if log_5min_values:
    logs = dl.DataLog()
    logs.create_table_amber()
    logs.conn.close()


def amberResetEstimatePrice():
    global amberEstimatePrice    
    amberEstimatePrice = True
    return amberEstimatePrice

def amber5minPrice():
    global amberEstimatePrice
    if amberEstimatePrice:
        #print("amberEstimatePrice is: ", amberEstimatePrice)
        requestTime = dt.now()
        amberData = al.get_amber_data(amberApiToken, amberSiteId,  13,5,5)
        responseTime = dt.now()
        amberEstimatePrice = amberData["current"]["general"].estimate
        if not amberEstimatePrice:
            if amber2mqtt:
                a2m.publishhastate_current(client, amberData)
                a2m.publishhastate_periods(client, amberData)
            if home_assistant:
                ha.post5MinPrice(amberData)
                ha.post5minPeriods(amberData)
        if log_5min_values:
            logamber = dl.DataLog()
            logamber.log_amber_data(requestTime, responseTime, amberData)
            logamber.conn.close() # .close_connection()


if __name__ == '__main__':
    # creating the BackgroundScheduler object
    scheduler = BackgroundScheduler()
    # setting the scheduled task
    client = a2m.connect_mqtt()
    client.loop_start()
    a2m.discoveryha(client)

    scheduler.add_job(amberResetEstimatePrice, 'cron', minute='0,5,10,15,20,25,30,35,40,45,50,55' ,second=5)
    scheduler.add_job(amber5minPrice, 'cron', minute=amberPriceMinutes ,second=amberPriceSeconds)
    # starting the scheduled task using the scheduler object
    scheduler.start()
    try:
        # To simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary but recommended
        scheduler.shutdown()
    client.loop_stop()
