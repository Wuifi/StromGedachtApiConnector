#!/usr/bin/python3

# import standard modules
import logging
import json
import requests
import json
#import pprint
#import time
from datetime import datetime, timedelta
from pytz import timezone
#import math
import numpy as np


def getDataStatesForecast(stromgedachtURL,zip_code):
    response = None
    try:
        # only look forward with the forecast. 
        ## get the time range for states request:
        #time format required for API:
        # starttime="2023-05-01T00%3A00%3A00%2B02%3A00"
        # endtime="2023-05-07T23%3A59%3A59%2B02%3A00"
        starttime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        starttime = starttime.replace(":","%3A")+"%2B02%3A00"
        endtime = (datetime.utcnow().date()+ timedelta(days=2)).strftime("%Y-%m-%d") +"T23%3A59%3A59%2B02%3A00"

        # the API only provides data for up to four days in the past and two days in the future
        requestURL = stromgedachtURL+"states?zip="+str(zip_code)+"&from="+starttime+"&to="+endtime
        #print(requestURL)
        # stromgedachtURL = "https://api.stromgedacht.de/v1/states?zip=70173&from=2023-04-11T00%3A00%3A00%2B02%3A00&to=2023-04-17T23%3A59%3A59%2B02%3A00"

        response = requests.get(requestURL, headers = {"accept":"application/json"})
        
    except Exception as e:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_str, ex)
        logging.error("Error while getting data from API: %s", str(e))
    return response

def timestamp_convert(s):
    #from input format s='2023-05-01T00:00:00+02:00'
    #to output format timestamp_convert(s)
    #"2023-05-01T00:00:00Z"
    s=datetime.strptime(s,"%Y-%m-%dT%H:%M:%S%z") 
    s = s.astimezone(timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ") 
    return s

def convert_dataset2influx(response,config):
    
    outDB=[]
    try:
        content = json.loads(response.text)
        status_code = response.status_code
        states = content["states"]
        # not sure, how the response is structured in case there is a restriction in future.
        #assumption: the states are listed with several timestamps.
        state_id_list= np.linspace(0, 1, len(states), endpoint=False, dtype=int)
        for state_id in state_id_list:
            starttime = timestamp_convert(states[state_id]["from"])
            endtime = timestamp_convert(states[state_id]["to"])
            state = states[state_id]["state"]

            outDB_new = {'measurement': config.get('influxdb', 'measurement_name'),
                             'tags': {'location': config.get('StromGedacht', 'location'),
                                      'zip_code': config.get('StromGedacht', 'zip_code')},
                             'fields': {'state': state},
                             'time':starttime}
            outDB.append(outDB_new)
            outDB_new = {'measurement': config.get('influxdb', 'measurement_name'),
                             'tags': {'location': config.get('StromGedacht', 'location'),
                                      'zip_code': config.get('StromGedacht', 'zip_code')},
                             'fields': {'state': state},
                             'time':endtime}
            outDB.append(outDB_new)            
    except Exception as e:
        logging.error(str(e))
        logging.error(str(states))
        status_code = 999
    
                
    outDB_new = {'measurement': config.get('influxdb', 'measurement_name'),
                             'tags': {'location': config.get('StromGedacht', 'location'),
                                      'zip_code': config.get('StromGedacht', 'zip_code')},
                             'fields': {'status_code': status_code},
                             'time':starttime}
    outDB.append(outDB_new)
    return(outDB)




# ###################################################
# #convert data to pandas df instead of influx
# def stromgedacht2df(result_dict):
#     import pandas as pd    
#     try:
#         messdaten=result_dict[0]
#         df=pd.DataFrame.from_dict(messdaten['datapoints'])
#         df['datetime']=pd.to_datetime(df[1])
#         df[messdaten['target']]=df[0]
#         df=df.drop([0,1], axis=1)
#     except Exception as e:
#         logging.error(str(e))
#     return df