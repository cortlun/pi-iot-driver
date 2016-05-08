import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

import subprocess

# ID of the device we care about
DEV_ID = 'D8_D1_CB_A6_66_DA'

dbus_loop = DBusGMainLoop()
bus = dbus.SystemBus(mainloop=dbus_loop)

# Figure out the path to the headset
man = bus.get_object('org.bluez', '/')
iface = dbus.Interface(man, 'org.bluez.Manager')
adapterPath = iface.DefaultAdapter()

iphone = bus.get_object('org.bluez', adapterPath + '/dev_' + DEV_ID)
print (iphone)

def cb(iface=None, mbr=None, path=None):
	print("iface: " + iface)
	print("mbr: " + mbr)
	print("path: " + path)

headset.connect_to_signal("Connected", cb, interface_keyword='iface', member_keyword='mbr', path_keyword='path')
headset.connect_to_signal("Disconnected", cb, interface_keyword='iface', member_keyword='mbr', path_keyword='path')

loop = gobject.MainLoop()
loop.run()