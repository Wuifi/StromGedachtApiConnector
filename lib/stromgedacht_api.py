#!/usr/bin/python3

# import standard modules
import logging
import requests
from datetime import datetime, timedelta



default_log_level = logging.INFO


########################################
## get data
def getDataNow(stromgedachtURL,zip_code):
    response = None
    try:
        requestURL = stromgedachtURL+"now?zip="+str(zip_code)
        response = requests.get(requestURL, headers = {"accept":"application/json"})
    except Exception as e:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        logging.error("Error while getting data from API: %s", str(e))
    return response

def getDataStates(stromgedachtURL,zip_code):
    response = None
    try:
        ## get the time range for states request:
        #time format required for API:
        # starttime="2023-05-01T00%3A00%3A00%2B02%3A00"
        # endtime="2023-05-07T23%3A59%3A59%2B02%3A00"
        
        # the API only provides data for up to four days in the past and two days in the future
        starttime = (datetime.utcnow().date() - timedelta(days=4)).strftime("%Y-%m-%d") +"T00%3A00%3A00%2B02%3A00"
        endtime = (datetime.utcnow().date()+ timedelta(days=2)).strftime("%Y-%m-%d") +"T23%3A59%3A59%2B02%3A00"
        requestURL = stromgedachtURL+"states?zip="+str(zip_code)+"&from="+starttime+"&to="+endtime
        print(requestURL)
        # stromgedachtURL = "https://api.stromgedacht.de/v1/states?zip=70173&from=2023-04-11T00%3A00%3A00%2B02%3A00&to=2023-04-17T23%3A59%3A59%2B02%3A00"

        response = requests.get(requestURL, headers = {"accept":"application/json"})
        
    except Exception as e:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        logging.error("Error while getting data from API: %s", str(e))
    return response