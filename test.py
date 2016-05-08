import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import subprocess

# ID of the device we care about
DEV_ID = 'D8_D1_CB_A6_66_DA '

dbus_loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=dbus_loop)

# Figure out the path to the headset
man = bus.get_object('org.bluez', '/')
iface = dbus.Interface(man, 'org.bluez.Manager')
adapterPath = iface.DefaultAdapter()

headset = bus.get_object('org.bluez', adapterPath + '/dev_' + DEV_ID)