import os
from gps import *
from time import *
import time
import threading
import sensorinterface
from initfirewallconfigs import FirewallRuleConfig, FirewallRuleInstance
from dataproducer import IotProducer
import logging
import importlib

gpsd = None #global gpsd variable
configs = {} #dictionary object to store configs
sensorinterface = None

class GeoTagger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd
        gpsd = gps(mode=WATCH_ENABLE)
        self.current_value = None
        self.running = True
        
    def run(self):
        global gpsd
        while self.running:
            gpsd.next()


#get configs from boot directory.  the following configs may need to be available:
#DISCRIMINATOR=
#AWS_SECURITY_GROUP_NAME=
#AWS_KEY=
#AWS_SECRET_KEY=
#KAFKA_IP_PORT=
#ENQUEUE_SECONDS=
def set_configs():
    configfile = os.path.join("/boot", "iot.config")
    lines = list(open(configfile))
    global configs
    for line in lines:
        parts = line.split("=")
        configs[parts[0]] = parts[1]
    
def open_firewall():
    logging.info("creating rules")
    fwrules = [FirewallRuleInstance(configs['KAFKA_IP_PORT'].split(':')[1], 'tcp')]
    logging.info("config with group: " + configs['AWS_SECURITY_GROUP_NAME'].replace('\n', '').replace('\r', '').replace(' ', ''))
    fwconfig = FirewallRuleConfig(configs['AWS_SECURITY_GROUP_NAME'].replace('\n', '').replace('\r', '').replace(' ', ''), fwrules)
    logging.info("opening firewall")
    fwconfig.open_firewall()

#def init_aws_creds():
    #os.environ['AWS_ACCESS_KEY_ID'] = configs['AWS_KEY']
    #os.environ['AWS_SECRET_ACCESS_KEY'] = configs['AWS_SECRET_KEY']
    #os.environ['AWS_DEFAULT_REGION'] = configs['AWS_REGION']

def check_geotag():
    return '"geotag":{"lat":' + str(gpsd.fix.latitude) + ',"lon":' + str(gpsd.fix.longitude) + ',"time":' + str(gpsd.utc) + str(gpsd.fix.time) + ',"alt":' + str(gpsd.fix.altitude) + ',"cnt":' + str(len(gpsd.satellites)) + '}'
    
def create_json(geotag, payload):
    return '{"message": {' + geotag + "," + payload + "}}"

if __name__ == "__main__":
    logging.basicConfig(filename="/home/pi/logs/iot.out",level=logging.INFO)
    #get environment configs
    logging.info("setting configs...")
    set_configs()
    
    #set aws values
    #init_aws_creds()
    
    #create firewall rules
    logging.info("creating firewall rules...")
    try:
        open_firewall()
    except:
        pass
    #start geotagger
    logging.info("starting geotagger...")
    gt = GeoTagger()
    gt.start()
    
    #create sensorinterface
    logging.info("creating sensor...")
    module = importlib.import_module("sensorinterface")
    sensor = getattr(module, configs["SENSOR_INTERFACE"].replace('\n', '').replace('\r', '').replace(' ', ''))()
    
    #create kafka producer
    logging.info("starting kafka producer...")
    ip = configs['KAFKA_IP_PORT'].replace('\r', '').replace('\n','').replace(' ','')
    logging.info("ip: " + ip)
    d = configs['DISCRIMINATOR'].replace('\n','').replace('\r','').replace(' ','')
    logging.info(d)
    try :
        producer = IotProducer(ip, d)
    except Exception as e: 
        logging.info("Exception creating producer:" + str(e))
        sys.exit(1)
    
    #create and enqueue json every x seconds
    try :
        while True:
            payload = sensor.check_sensor()
            geotag = check_geotag()
            m = create_json(geotag, payload)
            logging.info("whole message: " + m)
            producer.enqueue(m)
            logging.info("enqueue succeeded!!!!!!!!!!")
            time.sleep(float(configs['ENQUEUE_SECONDS']))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.info("exception: " + str(e))
        sys.exit(1)

    logging.info("shutting down.")
    sys.exit(0)
