#!/usr/bin/python
import os
import time
import sys
import Adafruit_DHT
from ds18b20 import DS18B20
import sqlite3

hum_sensor = 22
hum_pin = 17
amb_sensor = DS18B20()

mode = ""
temp1 = ""
temp2 = ""
humidity1 = ""

conn = None
logfile = '/var/www/temp_data.txt'
dbfile = 'templog.db'

# check whether script is run in 'display' mode or 'csv' output mode
if len(sys.argv) > 1:
	if sys.argv[1] == "csv":
		mode = "csv"
	if sys.argv[1] == "db":
		mode = "db"
else:
	mode = "display"

def add_temp_reading (temp1, temp2, humidity1):
    # I used triple quotes so that I could break this string into
    # two lines for formatting purposes
    curs.execute("""INSERT INTO temps values(datetime('now','localtime'), (?), (?), (?), '0')""", (temp1,temp2,humidity1))

    # commit the changes
    conn.commit()

if mode == "csv":
	while True:
		# Try to grab a sensor reading.  Use the read_retry method which will retry up
		# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
		fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
		amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])

		# write to logfile in format: "date,time,ambient_temp,fridge_temp,fridge_humidity"
		print "saving temp information..."
		log_entry = time.strftime("%d/%m/%Y %H:%M:%S")+ ","+\
			str("%0.1f" % amb_temp[0])+","+\
			str("%0.1f" % fridge_temp)+","+\
			str("%0.1f" % fridge_hum)+"\n"

		fo = open(logfile,'a')
		fo.write(log_entry)
		fo.close() # you can omit in most cases as the destructor will call it
		print "CSV_MODE: sleeping 5 mins..."
		time.sleep(300)
elif mode == "db":
	while True:
                fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
                amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])

		# try again just in case you get a dud reading
		if fridge_hum > 100 or fridge_temp < 5 or fridge_humidity < 50:
                    fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
                    amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])

                # write to logfile in format: "date,time,ambient_temp,fridge_temp,fridge_humidity"
                print "DB_MODE: saving temp information to the DB..."
                log_entry = time.strftime("%d/%m/%Y %H:%M:%S")+ ","+\
                        str("%0.1f" % amb_temp[0])+","+\
                        str("%0.1f" % fridge_temp)+","+\
                        str("%0.1f" % fridge_hum)+"\n"

		conn=sqlite3.connect(dbfile)
		curs=conn.cursor()

		# write the current temps into the DB
		add_temp_reading(amb_temp[0],fridge_temp,fridge_hum)

		conn.close()

                print "DB_MODE: sleeping 5 mins..."
                time.sleep(300)
else:
	# Note that sometimes you won't get a reading and the results will be null (because Linux can't
	# guarantee the timing of calls to read the sensor). If this happens try again!
	fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
	amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
	print str('Ambient temp: %0.1f' % amb_temp[0])+'*C'

	if fridge_hum is not None and fridge_temp is not None:
        	print 'Fridge temp: {0:0.1f}*C\nFridge humidity: {1:0.1f}%'.format(fridge_temp, fridge_hum)
	else:
        	print 'Failed to get reading. Try again!'
