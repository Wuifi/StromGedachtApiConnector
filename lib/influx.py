#!/usr/bin/env python3

# import standard modules
import logging
import influxdb
from datetime import datetime


#influx dB client functions
def initinfluxDBclient(config):
    try:
        influxdb_client = influxdb.InfluxDBClient(
            config.get('influxdb', 'hostname'),
            config.getint('influxdb', 'port', fallback=8086),
            config.get('influxdb', 'username'),
            config.get('influxdb', 'password'),
            config.get('influxdb', 'database'),
            config.getboolean('influxdb', 'ssl', fallback=False),
            config.getboolean('influxdb', 'verify_ssl', fallback=False))
    except Exception as e:
        logging.error('Problem initialising influxDBclient: %s', str(e))
    return influxdb_client


def check_db_status(db_handler, db_name):
    """
    Check if InfluxDB handler has access to a database.
    If it doesn't exist try to create it.
    Parameters
    ----------
    db_handler: influxdb.InfluxDBClient
        InfluxDB handler object
    db_name: str
        Name of DB to check
    """
    try:
        dblist = db_handler.get_list_database()
    except Exception as e:
        logging.error('Problem connecting to database: %s', str(e))
        return
    if db_name not in [db['name'] for db in dblist]:
        logging.info(f'Database <{db_name}> not found, trying to create it')
        try:
            db_handler.create_database(db_name)
        except Exception as e:
            logging.error('Problem creating database: %s', str(e))
            return
    else:
        logging.debug(f'Influx Database <{db_name}> exists')
    logging.info(f'Connection to InfluxDB established and database <{db_name}> present')
    return




def write2influx(data,influxdb_client,config):
    try:
        #logging.info("Writing data to InfluxDB")

        logging.debug("InfluxDB - measurement: %s" % data) #.get("measurement")

        influxdb_client.write_points(data,
                                     database= config.get('influxdb', 'database'),
                                     #measurement= config.get('influxdb', 'measurement_name'),
                                    time_precision="ms",
                                    batch_size=10000,
                                    protocol='json')
    except Exception as e:
        logging.error("Failed to write to InfluxDB <%s>: %s" % (config.get('influxdb', 'hostname'), str(e)))
        logging.error("out_influxDB <%s>: ",  data)

    return ()
