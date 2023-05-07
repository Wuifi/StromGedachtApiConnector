#!/usr/bin/env python3

self_description = """
StromGedachtApiMqttConnector is a tiny daemon written to fetch data from the StromGedacht-API and
sends it to an mqtt-broker instance.
"""

# import standard modules
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import configparser
import logging
import os
import signal
import time
from datetime import datetime

# import app specific functions
from lib.basic_functions import *
from lib.app_functions import *
from lib.influx import *
from lib.stromgedacht_api import *
from lib.forecast import *

__version__ = "0.0.1"
__version_date__ = "2023-05-05"
__description__ = "StromGedachtApiMqttConnector"
__license__ = "MIT"

# default vars
running = True
default_config = os.path.join(os.path.dirname(__file__), 'config.ini')
default_log_level = logging.INFO
#default_log_level = logging.DEBUG



def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    # parse command line arguments
    args = parse_args()
    # set logging
    log_level = logging.DEBUG if args.verbose is True else default_log_level
    if args.daemon:
        # omit time stamp if run in daemon mode
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s: %(message)s')
    # read config from ini file
    config = read_config(args.config_file)
    # set up influxdb handler
    influxdb_client = None
    try:
        #influxdb_client = influxdb.InfluxDBClient(
        #    config.get('influxdb', 'host'),
        #    config.getint('influxdb', 'port', fallback=8086),
        #    config.get('influxdb', 'username'),
        #    config.get('influxdb', 'password'),
        #    config.get('influxdb', 'database'),
        #    config.getboolean('influxdb', 'ssl', fallback=False),
        #    config.getboolean('influxdb', 'verify_ssl', fallback=False)
        #)
        measurement_name=config.get('influxdb', 'measurement_name')
        
        influxdb_client = initinfluxDBclient(config)
        
        
        # test more config options and see if they are present
        _ =config.get('StromGedacht', 'url')
        #_ =config.get('StromGedacht', 'username')
        #_ =config.get('StromGedacht', 'password')
        _ =config.getint('StromGedacht', 'request_interval')
        _ =config.get('StromGedacht', 'location')
        _ =config.get('StromGedacht', 'zip_code')

        #_ = config.get('influxdb', 'measurement_name')
    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    except ValueError as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    # check influx db status
    #check_db_status(influxdb_client, config.get('influxdb', 'database'))

    # create authenticated api client handler
    api_response = None
    #result_dict={}
    request_interval = 60
    try:
        request_interval = config.getint('StromGedacht', 'request_interval', fallback=60)
        url =config.get('StromGedacht', 'url')
        zip_code =config.get('StromGedacht', 'zip_code')
        #location =config.get('StromGedacht', 'location')
        api_response= getDataNow(url,zip_code)
        mqtt_topic = config.get('mqtt', 'topic')
        
        check_db_status(influxdb_client, config.get('influxdb', 'database'))   
        
    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    except BaseException as e:
        logging.error("Failed to connect to API  '%s'" % str(e))
        exit(1)

    # test connection
    try:
        api_response
    except Exception as e:
        if "401" in str(e):
            logging.error("Failed to connect to API")# '%s' using credentials. " %
                          #config.get('StromGedacht', 'username'))
        if "404" in str(e):
            logging.error("Failed to connect to API '%s'. Check url!" %
                          config.get('StromGedacht', 'url'))
        else:
            logging.error(str(e))
        exit(1)

    logging.info("Successfully connected to the StromGedacht API")

    logging.info("Starting main loop - wait  '%s' seconds until first request!",request_interval)
    duration=0
    time.sleep(request_interval) # wait, otherwise Exception 429, 'Limitation: maximum number of requests per second exceeded']
        
    while running:
        logging.debug("Starting API requests")
        start = int(datetime.utcnow().timestamp() * 1000)
        
        #processing data for actual state (NOW)
        api_response_now =getDataNow(url,zip_code)
        json_string = convert2json(api_response_now)
        #print(json_string)
        MQTT_msg=convert_to_mqtt_msg(json_string,mqtt_topic)
        publish2mqtt(MQTT_msg,config)
        
        duration= int(datetime.utcnow().timestamp() * 1000) - start
        logging.debug("Duration of requesting and sending data to MQTT: %0.3fs" % (duration / 1000)) 
        
                
        #wait x-sec to get data for forecaset
        # just sleep for interval seconds - last run duration
        for _ in range(0, int(((request_interval * 1000) - duration) / 100)):
            if running is False:
                break
            time.sleep(0.0965)
            
        start = int(datetime.utcnow().timestamp() * 1000)
        #processing data for forecast state (STATES)
        response_forecast=getDataStatesForecast(url,zip_code)
        json_string = convert_dataset2influx(response_forecast,config)
        write2influx(json_string,influxdb_client,config)
        
        duration= int(datetime.utcnow().timestamp() * 1000) - start
        logging.debug("Duration of requesting and sending data to Influx: %0.3fs" % (duration / 1000)) 
    
        # just sleep for interval seconds - last run duration
        for _ in range(0, int(((request_interval * 1000) - duration) / 100)):
            if running is False:
                break
            time.sleep(0.0965)
            
            
if __name__ == "__main__":
    main()
