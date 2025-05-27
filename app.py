""" main code to run the app and set the schedules for the 5 minute price updates from Amber and AEMO"""
import json
import logging
import os
from datetime import datetime as dt
import time as time
from apscheduler.schedulers.background import BackgroundScheduler
import aemodata as aemo
import amberdata as al
#import datalog as dl
import send2mqtt as a2m

#if os.path.isfile("options.json"):
#    with open("options.json", "r") as f:
#        config = json.load(f)

if os.path.isfile("/data/options.json"):
    with open("/data/options.json", "r") as f:
        config = json.load(f)
else: 
    with open("./data/options.json", "r") as f:
        config = json.load(f)

#LOG_5MIN_FORECASTS = True if config["Log_database"]["log_amber_5min_forecasts"].lower() == "true" else False
#LOG_5MIN_VALUES = True if config["Log_database"]["log_amber_5min_current_values"].lower() == "true" else False
LOG_FORMAT = '%(asctime)s : %(message)s'

amberSiteId = config["amber"]["site_id"]
amberApiToken   = config["amber"]["access_token"]
amberPriceSeconds = config["amber"]["amber5minPrice_seconds"]
amberPriceMinutes = config["amber"]["amber5minPrice_minutes"]
aemoPriceSeconds = config["aemo"]["aemo5minPrice_seconds"]
aemoPriceMinutes = config["aemo"]["aemo5minPrice_minutes"]
amber2mqtt = True if config["integration"]["amber2mqtt"].lower() == "true" else False
mqttDebug = True if config["mqtt"]["debug"].lower() == "true" else False

amber5minForecast = False
amber30minForecast = False
amberUserForecast = False
amber288Forecast = False
for key in config["amber"]:
    if key == "forecast5min":
        #test =(config["amber"]["forecast5min"].lower() )
        amber5minForecast = True if config["amber"]["forecast5min"].lower() == "true" else False
    if key == "forecast30min":
        amber30minForecast = True if config["amber"]["forecast30min"].lower() == "true" else False
    if key == "forecastUser":
        amberUserForecast = True if config["amber"]["forecastUser"].lower() == "true" else False
    if key == "forecast288":
        amber288Forecast = True if config["amber"]["forecast288"].lower() == "true" else False
if amber288Forecast:
    amber5minForecast = True
    amber30minForecast = True
amberEstimatePrice = True
aemoPriceFirm = False


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
            if amber5minForecast:
                amberData5 = al.getAmberData(amberApiToken, amberSiteId,15,0,5)
                a2m.publishAmberState5MinForecasts(client, amberData5)
            if amber30minForecast:
                amberData30 = al.getAmberData(amberApiToken, amberSiteId,99,0,30)
                a2m.publishAmberState30MinForecasts(client, amberData30)
            if amberUserForecast:
                amberData = al.getAmberData(amberApiToken, amberSiteId,288,0,0)
                a2m.publishAmberStateUserForecasts(client, amberData)
            if amber288Forecast:
                amberData288 = al.create_288_5min_intervals(amberData5, amberData30)
                a2m.publishAmberState5MinExtendedForecasts(client, amberData288)
       

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
    scheduler.configure(job_defaults={'max_instances': 2})
    # setting the scheduled task
    client = a2m.mqttConnectBroker()
    #amber5minPrice()
    if mqttDebug:
        client.enable_logger(mqttLogger)
    client.loop_start()
    client.subscribe("homeassistant/status")
    a2m.PublishDiscoveryAmberEntities(client)
    a2m.PublishDiscoveryAemoEntities(client)
    a2m.PublishDiscoveryAmberForecastEntities(client,amber5minForecast,amber30minForecast,amberUserForecast,amber288Forecast)
    
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
