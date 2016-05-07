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
configs = {} #dictionary object to store configs
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
    configfile = os.path.join("/boot", "iot.config")
    lines = list(open(configfile))
    global configs
    for line in lines:
        print("in for")
        parts = line.split("=")
        print("part 0: " + parts[0])
        print("part 1: " + parts[1])
        configs[parts[0]] = parts[1]
    
def open_firewall():
    print("creating rules")
    fwrules = [FirewallRuleInstance(config['KAFKA_IP_PORT'].split(':')[1], 'tcp')]
    print("config with group: " + config['AWS_SECURITY_GROUP_NAME'])
    fwconfig = FirewallRuleConfig(config['AWS_SECURITY_GROUP_NAME'], fwrules)
    print("opening firewall")
    fwconfig.open_firewall()

def init_aws_creds():
    os.environ['AWS_ACCESS_KEY_ID'] = config['AWS_KEY']
    os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS_SECRET_KEY']
    os.environ['AWS_DEFAULT_REGION'] = config['AWS_REGION']

def check_geotag():
    return '"geotag":{"lat":' + gpsd.fix.latitude + ',"lon":' + gpsd.fix.longitude + ',"time":' + gpds.utc + gpsd.fix.time + ',"alt":' + gpsd.fix.altitude + ',"cnt":' + len(gpsd.satellites) + '}'
    
def create_json(geotag, payload):
    return '{"message": {' + check_geotag() + "," + get_payload() + "}}"

if __name__ == "__main__":
    #get environment configs
    print("setting configs...")
    set_configs()
    
    #create firewall rules
    print("creating firewall rules...")
    open_firewall()
    
    #start geotagger
    print("starting geotagger...")
    gt = GeoTagger()
    gt.start()
    
    #create sensorinterface
    print("creating sensor...")
    sensor = SensorInterface()
    
    #create kafka producer
    print("starting kafka producer...")
    producer = IotProducer(configs['KAFKA_IP_PORT'], config['DISCRIMINATOR'])
    
    #create and enqueue json every x seconds
    while True:
        print("getting payload...")
        payload = sensor.check_sensor()
        print("payload: " + payload)
        geotag = check_geotag()
        print ("geotag: " + geotag)
        m = create_json(geotag, payload)
        print("whole message: " + m)
        producer.enqueue(m)
        print("enqueue succeeded!!!!!!!!!!")
        time.sleep(configs['ENQUEUE_SECONDS'])