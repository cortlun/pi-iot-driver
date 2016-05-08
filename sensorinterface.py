import random
import time

class SensorInterface:
    """Name this class whatever you'd like and put it in your iot.config file. 
    Be sure to implement the check_sensor method and return a dictionary object
    of key/value pairs from your sensor."""
    def check_sensor( self ):
        return '"payload":{"randomnum":' + str(random.random() * 100) + '}'

if __name__ == "__main__":
    test = SensorInterface()
    while True:
        print(test.check_sensor())
        time.sleep(5)
        
