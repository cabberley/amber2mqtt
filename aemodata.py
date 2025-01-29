"""AEMO Module to poll NEM Report data"""

import json
from datetime import datetime
import requests

from const import (
    AEMO_NEM_SUMMARY_URI,
)

aemoPriceFirm = False

def aemoResetPriceFirm():
    global aemoPriceFirm    
    aemoPriceFirm = False
    return aemoPriceFirm


def getAemoCurrentData():
    """Get current price data from the API and parse the JSON"""
    try:
        apiResponse = requests.get(
            AEMO_NEM_SUMMARY_URI, headers={"accept": "application/json"}, timeout=10
        )
        apiResponse.raise_for_status()
        aemoData = apiResponse.json()
        print(f"The response of AEMO get aemo_price_firm: {aemoData["ELEC_NEM_SUMMARY"][0]["SETTLEMENTDATE"]}\n")
        for interConnector in aemoData["ELEC_NEM_SUMMARY"]:
            interConnector["INTERCONNECTORFLOWS"] = json.loads(
                interConnector["INTERCONNECTORFLOWS"]
            )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"API request failed: {e}") from e
    return aemoData


def checkAemoSettlementDate(settlementData):
    """Check if the settlement date is current and the price is firm"""
    aemoPriceFirmCheck = False
    settlementDate = datetime.strptime(
        settlementData["SETTLEMENTDATE"], "%Y-%m-%dT%H:%M:%S"
    )
    timeNow = datetime.now()
    # print(settlementDate.minute/5)
    # print(timeNow.minute/5)
    settlementMinute = (
        (settlementDate.minute / 5) if (settlementDate.minute) < 60 else (60 / 5)
    )
    if int(settlementMinute) - 1 == int(timeNow.minute / 5):
        print("Settlement Date is current")
        if settlementData["PRICE_STATUS"] == "FIRM":
            aemoPriceFirmCheck = True
    return aemoPriceFirmCheck


def testAemoUnit():
    """Test the AEMO module"""
    global aemoPriceFirm
    test = getAemoCurrentData()
    aemoPriceFirm = checkAemoSettlementDate(test["ELEC_NEM_SUMMARY"][0]) #["SETTLEMENTDATE"])
    print(aemoPriceFirm)
    if aemoPriceFirm:
        print("Price is firm")
    print(test)
    return test

#testAemo = testAemoUnit()
#print(testAemo)