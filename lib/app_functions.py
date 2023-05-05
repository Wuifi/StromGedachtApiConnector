#!/usr/bin/python3

# import standard modules
import logging
import json

# import 3rd party modules
import paho.mqtt.client as mqtt
mqttc = mqtt.Client()
import paho.mqtt.publish as publish


default_log_level = logging.INFO


def convert2json(response):
    #pprint.pprint(response.status_code)        
    state_dict={0:'undefined', 1: "green", 2: "yellow", 3: "orange", 4: "red"}
    content= []
    state=0
    status_code = 404
    
    try:
        content = json.loads(response.text)
        state = content["state"]
        
        status_code = response.status_code

    except Exception as e:
        logging.error("Failed to convert message <%s>: " % str(e))
        status_code = 999
    
    state_string =state_dict[state]    
    
    json_string = {"STATE":{"value":state,"string":state_string},
                           "DEBUG":{"status_code":status_code}}
    return json_string

## publish data 2 mqtt
def convert_to_mqtt_msg(dict_input,topic):
    try:
        # Serializing json   
        json_object = json.dumps(dict_input, indent = 4)  
        #print(json_object)
        #print(type(json_object))
        msg = {'topic':topic, 'payload':json_object}
        #print(msg)
        #print(type(msg))
    except Exception  as e:
        logging.error("Error while converting data to json: ",str(e))
    return msg


def publish2mqtt(MQTT_msg,config):
    try:
        #print(MQTT_msg)   
        msgs = [MQTT_msg]
    # print(msgs)
        publish.multiple(
            msgs, hostname=config.get('mqtt', 'hostname'),
            port=config.getint('mqtt', 'port'),
            client_id=None,#config.get('mqtt', 'client_id'),
            keepalive=config.getint('mqtt', 'keepalive'),
            will=None,#config.get('mqtt', 'will'),
            auth=None,#config.get('mqtt', 'auth'),
            tls=None,#config.get('mqtt', 'tls'),
            protocol=mqtt.MQTTv311,#config.get('mqtt', 'protocol'),
            transport=config.get('mqtt', 'transport')
            )
    except Exception as e:
        logging.error("Failed to publish to MQTT <%s>: %s" % (config.get('mqtt', 'hostname'), str(e)))
    return 