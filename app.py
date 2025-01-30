""" main code to run the app and set the schedules for the 5 minute price updates from Amber and AEMO"""
import json
import logging
import os
from datetime import datetime as dt
import time as time
from apscheduler.schedulers.background import BackgroundScheduler
import aemodata as aemo
import amberdata as al
import datalog as dl
import send2mqtt as a2m

if os.path.isfile("/data/options.json"):
    with open("/data/options.json", "r") as f:
        config = json.load(f)
else: 
    with open("./data/options.json", "r") as f:
        config = json.load(f)

LOG_5MIN_FORECASTS = True if config["Log_database"]["log_amber_5min_forecasts"].lower() == "true" else False
LOG_5MIN_VALUES = True if config["Log_database"]["log_amber_5min_current_values"].lower() == "true" else False
LOG_FORMAT = '%(asctime)s : %(message)s'

amberSiteId = config["amber"]["site_id"]
amberApiToken   = config["amber"]["access_token"]
amberPriceSeconds = config["amber"]["amber5minPrice_seconds"]
amberPriceMinutes = config["amber"]["amber5minPrice_minutes"]
aemoPriceSeconds = config["aemo"]["aemo5minPrice_seconds"]
aemoPriceMinutes = config["aemo"]["aemo5minPrice_minutes"]
amber2mqtt = True if config["integration"]["amber2mqtt"].lower() == "true" else False
mqttDebug = True if config["mqtt"]["debug"].lower() == "true" else False

amberEstimatePrice = True
aemoPriceFirm = False

if LOG_5MIN_VALUES:
    logs = dl.DataLog()
    logs.create_table_amber()
    logs.conn.close()

def aemoResetPriceFirm():
    """Reset the AEMO Price Firm to False"""
    global aemoPriceFirm    
    aemoPriceFirm = False
    return aemoPriceFirm

def amberResetEstimatePrice():
    """Reset the Amber Estimate Price to True"""
    global amberEstimatePrice    
    amberEstimatePrice = True
    return amberEstimatePrice

def amber5minPrice():
    """Get the current prices from the Amber API every 5 minutes"""
    global amberEstimatePrice
    if amberEstimatePrice:
        requestTime = dt.now()
        amberData = al.getAmberData(amberApiToken, amberSiteId,  13,5,5)
        responseTime = dt.now()
        amberEstimatePrice = amberData["current"]["general"].estimate
        if not amberEstimatePrice:
            print("Amber Current Period data confirmed")
            if amber2mqtt:
                a2m.publishAmberStateCurrent(client, amberData)
                a2m.publishAmberStatePeriods(client, amberData)
        if LOG_5MIN_VALUES:
            logamber = dl.DataLog()
            logamber.log_amber_data(requestTime, responseTime, amberData)
            logamber.conn.close() # .close_connection()

def aemo5MinCurrentPrice():
    """Get the current price from AEMO every 5 minutes"""
    global aemoPriceFirm
    if not aemoPriceFirm:
        aemoData = aemo.getAemoCurrentData()
        aemoPriceFirm = aemo.checkAemoSettlementDate(aemoData["ELEC_NEM_SUMMARY"][0])
        if aemoPriceFirm:
            if amber2mqtt:
                a2m.publishAemoStateCurrent(client, aemoData)

if __name__ == '__main__':
    # creating the BackgroundScheduler object
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    apScheduleLogger = logging.getLogger('apscheduler').setLevel(logging.ERROR)
    if mqttDebug:
        mqttLogger = logging.getLogger('paho').setLevel(logging.DEBUG)
    scheduler = BackgroundScheduler()
    # setting the scheduled task
    client = a2m.mqttConnectBroker()

    if mqttDebug:
        client.enable_logger(mqttLogger)
    client.loop_start()
    client.subscribe("homeassistant/status")
    a2m.PublishDiscoveryAmberEntities(client)
    a2m.PublishDiscoveryAemoEntities(client)

    scheduler.add_job(
        amberResetEstimatePrice, 'cron', minute='0,5,10,15,20,25,30,35,40,45,50,55' ,second=5)
    scheduler.add_job(
        aemoResetPriceFirm, 'cron', minute='0,5,10,15,20,25,30,35,40,45,50,55' ,second=2)
    scheduler.add_job(
        amber5minPrice, 'cron', minute=amberPriceMinutes ,second=amberPriceSeconds)
    scheduler.add_job(
        aemo5MinCurrentPrice, 'cron', minute=aemoPriceMinutes ,second=aemoPriceSeconds)
    # starting the scheduled task using the scheduler object
    scheduler.start()
    try:
        # To simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    client.loop_stop()
