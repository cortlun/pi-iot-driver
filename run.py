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
    fwrules = [FirewallRuleInstance(configs['KAFKA_IP_PORT'].split(':')[1], 'tcp')]
    print("config with group: " + configs['AWS_SECURITY_GROUP_NAME'].replace('\n', '').replace('\r', '').replace(' ', ''))
    fwconfig = FirewallRuleConfig(configs['AWS_SECURITY_GROUP_NAME'].replace('\n', '').replace('\r', '').replace(' ', ''), fwrules)
    print("opening firewall")
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
    #get environment configs
    print("setting configs...")
    set_configs()
    
    #set aws values
    #init_aws_creds()
    
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
    ip = configs['KAFKA_IP_PORT'].replace('\r', '').replace('\n','').replace(' ','')
    print("ip: " + ip)
    d = configs['DISCRIMINATOR'].replace('\n','').replace('\r','').replace(' ','')
    print(d)
    producer = IotProducer(ip, d)
    
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
