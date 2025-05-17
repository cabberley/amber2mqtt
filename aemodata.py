import json
import requests
import asyncio
from datetime import datetime
import time

from const import (
    AEMO_NEM_SUMMARY_URI,
)




apiCurrentUrl = (AEMO_NEM_SUMMARY_URI)
#aemoPriceFirm = False

    # Get current price data from the API and parse the JSON

def reset_aemo_price_firm():
    global aemoPriceFirm
    aemoPriceFirm = False

async def get_aemo_current_data():
    # Get current price data from the API and parse the JSON
    try:
        apiResponse = requests.get(
            apiCurrentUrl, headers={"accept": "application/json"}, timeout=10
        )
        apiResponse.raise_for_status()
        aemodata = apiResponse.json()
        for interconnector in aemodata["ELEC_NEM_SUMMARY"]:
            interconnector["INTERCONNECTORFLOWS"] = json.loads(interconnector["INTERCONNECTORFLOWS"])
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"API request failed: {e}") from e
    return aemodata

def check_aemo_settlement_date(settlementData):
    #global aemoPriceFirm
    settlementDate = datetime.strptime(settlementData["SETTLEMENTDATE"], "%Y-%m-%dT%H:%M:%S")
    timeNow = datetime.now()
    #print(settlementDate.minute/5)
    #print(timeNow.minute/5)
    aemoPriceFirmCheck = False
    settlementMinute = (settlementDate.minute/5) if (settlementDate.minute) < 60 else (60/5)
    if int(settlementMinute)-1 == int(timeNow.minute/5):
        print("Settlement Date is current")
        if settlementData["PRICE_STATUS"] == "FIRM":
            aemoPriceFirmCheck = True
    return aemoPriceFirmCheck

def poll_aemo_current_data():
    aemoPriceFirm = False
    if not aemoPriceFirm:
        try:
            aemoData = get_aemo_current_data()
            check_aemo_settlement_date(aemoData["ELEC_NEM_SUMMARY"][0])
            #print(aemoPriceFirm)
            if aemoPriceFirm:
                print("Price is firm")

        except Exception as e:
            print(f"Error: {e}")
    return aemoPriceFirm


#test = get_aemo_current_data()

#check_aemo_settlement_date(test["ELEC_NEM_SUMMARY"][0]) #["SETTLEMENTDATE"])
#print(aemoPriceFirm)
#if aemoPriceFirm:
#    print("Price is firm")
#test = poll_aemo_current_data()    
#print(test)