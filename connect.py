#!/usr/bin/env python

from subprocess import Popen, PIPE
import os
import urllib
import sys
import time

def spawn_child_process(args):
  p = Popen(args, stdout=PIPE, stderr=PIPE)
  out, err = p.communicate()
  if p.returncode == 0:
      return out.decode("utf-8")
  else:
      return err.decode("utf-8")

if __name__ == "__main__":
    disconnected = True
    try:
        print("Attempting initial connectivity check")
        urllib.urlopen("http://checkip.amazonaws.com")
        print("success")
        disconnected = False
        spawn_child_process(["sudo", "python", "/home/pi/rpi-iot-driver/run.py"])
    except:
        print("Initial connectivity check failed")
        
    if (disconnected):
        m = spawn_child_process(["sudo", "pand", "-c", "D8:D1:CB:A6:66:DA", "-role", "PANU", "--persist", "30"])
        print("sudo pand complete: " + m)
    
    while disconnected:
        try:
            print("attempting urllib.urlopen")
            urllib.urlopen("http://checkip.amazonaws.com")
            print("success")
            disconnected = False
            spawn_child_process(["sudo", "python", "/home/pi/rpi-iot-driver/run.py"])
        except:
            print("excetion attempting attempting urllib.open")
            time.sleep(10)
    
    print("exiting")
    sys.exit(0)
