import os
from gps import *
from time import *
import time
import threading
import sensorinterface
from initfirewallconfigs import FirewallRuleConfig, FirewallRuleInstance
from sensorinterface import SensorInterface
from dataproducer import IotProducer

gpsd = None #global gpsd variable
configs = None #dictionary object to store configs
config_location = "/etc/boot"
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
    configfile = os.path.join("etc", "boot", "iot.config")
    lines = list(open(configfile))
    global configs
    for line in lines:
        parts = line.split("=")
        print("line part 0: " line[0])
        print("line part 1: " line[1])
        configs[line[0]] = line[1]
    print("configs: " + configs)
    
def open_firewall():
    fwrules = [FirewallRuleInstance(configs['KAFKA_IP_PORT'].split(':')[1], 'tcp')]
    fwconfig = FirewallRuleConfig(configs['AWS_SECURITY_GROUP_NAME', fwrules])
    fwconfig.open_firewall

def check_geotag():
    {'geotag':
        {
            'lat': gpsd.fix.latitude,
            'lon': gpsd.fix.longitude,
            'time': gpds.utc + gpsd.fix.time,
            'alt': gpsd.fix.altitude,
            'cnt': len(gpsd.satellites)
        }
    }
    
def create_json(geotag, payload):
    {'message': geotag, payload}

if __name__ == "__main__":
    #get environment configs
    set_configs()
    
    #create firewall rules
    open_firewall()
    
    #start geotagger
    gt = GeoTagger()
    gt.start()
    
    #create sensorinterface
    sensor = SensorInterface()
    
    #create kafka producer
    producer = IotProducer(configs['KAFKA_IP_PORT'])
    
    #create and enqueue json every x seconds
    while True:
        payload = sensor.check_sensor()
        geotag = check_geotag()
        m = create_json(geotag, payload)
        producer.enqueue(m)
        time.sleep(configs['ENQUEUE_SECONDS'])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    