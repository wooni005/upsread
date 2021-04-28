# upsread
 APC UPS status via MQTT

## Install python modules
The following python3 modules are needed:
```
$ sudo pip3 install simplejson paho-mqtt subprocess32
```

## Install apcupsd
Docs: http://www.apcupsd.org/manual/manual.html

The APC UPS daemon service is used to read out the data from the UPS.

Install apcupsd:
```
$ sudo apt install apcupsd
```

Check if the device is connected:
```
$ usb-devices -d
T:  Bus=01 Lev=03 Prnt=04 Port=00 Cnt=01 Dev#=  5 Spd=1.5 MxCh= 0
D:  Ver= 1.10 Cls=00(>ifc ) Sub=00 Prot=00 MxPS= 8 #Cfgs=  1
P:  Vendor=051d ProdID=0002 Rev=01.06
S:  Manufacturer=APC
S:  Product=Back-UPS ES 550G FW:870.O3 .I USB FW:O3 
S:  SerialNumber=5B1534T03413  
C:  #Ifs= 1 Cfg#= 1 Atr=e0 MxPwr=2mA
I:  If#=0x0 Alt= 0 #EPs= 1 Cls=03(HID  ) Sub=00 Prot=00 Driver=usbhid
```

Configuration file:
```
$ sudo vi /etc/apcupsd/apcupsd.conf
## apcupsd.conf v1.1 ##
UPSCABLE usb
UPSTYPE usb
DEVICE
LOCKFILE /var/lock
UPSCLASS standalone
UPSMODE disable
```

## APC test tool
APC UPS daemon package also contains a test tool. First stop the apcupsd service and start the test tool

```
$ sudo systemctl stop apcupsd.service
$ sudo apctest 


2021-04-28 09:51:12 apctest 3.14.14 (31 May 2016) debian
Checking configuration ...
sharenet.type = Network & ShareUPS Disabled
cable.type = USB Cable
mode.type = USB UPS Driver
Setting up the port ...
Doing prep_device() ...

You are using a USB cable type, so I'm entering USB test mode
Hello, this is the apcupsd Cable Test program.
This part of apctest is for testing USB UPSes.

Getting UPS capabilities...SUCCESS

Please select the function you want to perform.

1)  Test kill UPS power
2)  Perform self-test
3)  Read last self-test result
4)  View/Change battery date
5)  View manufacturing date
6)  View/Change alarm behavior
7)  View/Change sensitivity
8)  View/Change low transfer voltage
9)  View/Change high transfer voltage
10) Perform battery calibration
11) Test alarm
12) View/Change self-test interval
 Q) Quit
```
