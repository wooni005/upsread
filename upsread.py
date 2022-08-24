#!/usr/bin/python3

import simplejson as json
import subprocess   # For OS calls
import time
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client

# external files/classes
import logger
import serviceReport
import settings

# Install APC driver with:
#
# Read https://help.ubuntu.com/community/apcupsd or follow below lines
#
# Quick Install for USB-based APC units
#    install the daemon: apt-get install apcupsd
#    edit /etc/apcupsd/apcupsd.conf and change these lines
#        UPSNAME myownups
#        UPSCABLE usb
#        UPSTYPE usb
#        comment out DEVICE (it contains a TTY link, which will prevent it from working)
#    edit /etc/default/apcupsd
#        change ISCONFIGURED from no to yes
#    /etc/init.d/apcupsd start
#    apcaccess

# Shutdown access to user without password:
#
# sudo visudo -f /etc/sudoers.d/myOverrides
#
# <myusername>    ALL = NOPASSWD: /sbin/shutdown

# MQTT JSON data in MQTT msg
upsStatus = {"lineVoltage": 0.0, "batteryVoltage": 0.0, "upsLoad": 0.0, "batteryCharge": 0.0}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(_client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Client connected successfully")
        _client.subscribe([(settings.MQTT_TOPIC_CHECK, 1)])
    else:
        print(("ERROR: MQTT Client connected with result code %s " % str(rc)))


# The callback for when a published message is received from the server
def on_message(_client, userdata, msg):
    print(('ERROR: Received ' + msg.topic + ' in on_message function' + str(msg.payload)))


###
# Initalisation ####
###
logger.initLogger(settings.LOG_FILENAME)

# Give Home Assistant and Mosquitto the time to startup
time.sleep(2)

# First start the MQTT client
client = mqtt_client.Client()
client.message_callback_add(settings.MQTT_TOPIC_CHECK, serviceReport.on_message_check)
client.on_connect = on_connect
client.on_message = on_message
client.connect(settings.MQTT_ServerIP, settings.MQTT_ServerPort, 60)
client.loop_start()

# Main Loop
mqtt_publish.single("huis/HomeLogic/UPS-Spanningsuitval/bediening", 0, qos=1, hostname="192.168.5.248", retain=True)
print("APC Probe running...")

batt = 100   # Needs to be >MINBATT to not do a false processor stop
dictMQTT = {b'LINEV': 'lineVoltage', b'BATTV': 'batteryVoltage', b'LOADPCT': 'upsLoad', b'BCHARGE': 'batteryCharge'}  # Convert Keyword to Domoticz index.
oldStat = '0'

while True:                  # Endless loop
    res = subprocess.check_output(settings.APCACCESS)
    for line in res.split(b"\n"):
        # print(line)
        (key, spl, val) = line.partition(b": ")
        key = key.rstrip()         # Strip spaces right of text
        val = val.strip()         # Remove outside spaces
        # print(key, val)
        if key == b'STATUS':
            if b'ONBAT' in val:
                stat = '1'
            else:
                stat = '0'
            if oldStat != stat:
                oldStat = stat
                mqtt_publish.single("huis/UPS/UPS-Spanningsuitval/ups", int(stat), qos=1, hostname="192.168.5.248")

            # The real Shutdown of all servers is controlled by home_logic/systemWatch.py
            if (b'ONBATT' in val) and (batt < settings.MINBATT):  # If there is less than 10 percent battery power left, and we are offline then shutdown
                mqtt_publish.single("huis/UPS/UPS-ServerShutdown/ups", '1', qos=1, hostname="192.168.5.248")
                # subprocess.call("sudo shutdown -h now", shell=True)   # Edit /etc/sudoers.d/myOverrides to make shutdown without password work

        val = val.split(b' ', 1)[0]    # Split using space and only take first part

        if key in dictMQTT:
            if key == b'BCHARGE':
                batt = int(float(val))      # Save battery level for Offline mode.
            upsStatus[dictMQTT[key]] = float(val)

    mqtt_publish.single("huis/UPS/UPS-status/ups", json.dumps(upsStatus, separators=(', ', ':')), qos=1, hostname="192.168.5.248", retain=True)
    time.sleep(60)  # Take a minute break
