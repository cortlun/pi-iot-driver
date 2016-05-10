import random
import time
from awsutils import ChildProcessUtils

class TemperatureInterface:
    """Name this class whatever you'd like and put it in your iot.config file. 
    Be sure to implement the check_sensor method and return a dictionary object
    of key/value pairs from your sensor."""
    def check_sensor(self):
        cp = ChildProcessUtils()
        raw_sensor_data = cp.spawn_child_process(["cat", "/sys/bus/w1/devices/28-0000077b0b33/w1_slave"])
        line_1 = raw_sensor_data.split('\n')[0]
        if(line_1[-3:] == "YES"):
            temp_line = raw_sensor_data.split('\n')[1]
            c = float(temp_line[temp_line.index("t=") + len("t="):]) / 1000
            f = c * 1.8 + 32
            k = c + 273.15
            return('"payload":{"fahrenheit":"'+str(f)+'"'+',"celsius":'+'"'+str(c)+'"'+',"kelvin":'+'"'+str(k)+'"'+'}')

if __name__ == "__main__":
    test = TemperatureInterface()
    print(test.check_sensor())
    time.sleep(5)
        
