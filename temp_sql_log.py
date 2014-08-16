#!/usr/bin/python
import os
import time
import sys
import Adafruit_DHT
from ds18b20 import DS18B20
import sqlite3

# setup GPIO variables
hum_sensor = 22
hum_pin = 17
amb_sensor = DS18B20()

# define variables
mode = ""
temp1 = ""
temp2 = ""
humidity1 = ""
db_loopcount = 0

# setup relevant files and DBs
conn = None
logfile = '/var/www/temp_data.txt'
dbfile = 'templog.db'

# check whether script is run with parameters for writing to CSV or DB (or nothing)
if len(sys.argv) > 1:
	# don't bother looking for more than 1 arg
	if sys.argv[1] == "csv":
		mode = "csv"
	if sys.argv[1] == "db":
		mode = "db"
else:
	# default to stdout
	mode = "display"

def add_temp_reading (temp1, temp2, humidity1):
    # insert the latest sensor readings based on what's passed to the function
    curs.execute("""INSERT INTO temps values(datetime('now','localtime'), (?), (?), (?), '0')""", (temp1,temp2,humidity1))

    # commit the changes
    conn.commit()

if mode == "csv":
	while True:
		# grab a sensor reading for each of the DHT22 and DS18B20 sensors
		fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
		# if anyone knows how to just get DegC, I'm all ears :)
		amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])

		# write to logfile in format: "date,time,ambient_temp,fridge_temp,fridge_humidity"
		print "saving temp information..."
		# format the string into CSV format prior to writing
		log_entry = time.strftime("%d/%m/%Y %H:%M:%S")+ ","+\
			str("%0.1f" % amb_temp[0])+","+\
			str("%0.1f" % fridge_temp)+","+\
			str("%0.1f" % fridge_hum)+"\n"

		# open the logfile and append
		fo = open(logfile,'a')
		fo.write(log_entry)
		fo.close()
		print "CSV_MODE: sleeping 5 mins..."
		# wait 5 mins before taking another sensor reading
		time.sleep(300)

elif mode == "db":
	# keep looping forever (well, until the RPi shits itself or something similar)
	while True:
		# grab some sensor readings on both the DHT22 and DS18B20 sensors
	        fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
        	amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])

		# try again just in case you get a dud reading
		if fridge_hum > 100 or fridge_temp < 5 or fridge_hum < 50:
			while fridge_hum > 100 or fridge_temp < 5 or fridge_hum < 50 or db_loopcount <= 5:

				# try to grab the temp values once more
            			fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
            			amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
            
            			# limit how many times we retry; give in eventually
            			db_loopcount += 1

            			# retry at the interval so we don't overload the sensor or get erroneous values
				time.sleep(2)

        	# write to the database in format: "datetime,ambient_temp,fridge_temp,fridge_humidity, outside_temp"
        	print "DB_MODE: saving temp information to the DB..."
        
        	# write the current temps into the DB and clean up
		conn=sqlite3.connect(dbfile)
		curs=conn.cursor()
		
		add_temp_reading(amb_temp[0],fridge_temp,fridge_hum)

		conn.close()
		db_loopcount = 0

		# wait 5 mins before grabbing next set of readings
        	print "DB_MODE: sleeping 5 mins..."
        	time.sleep(300)
else:
	# grab the latest sensor readings from the DHT22 and DS18B20 and report results to stdout 
	fridge_hum, fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
	amb_temp = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
	print str('Ambient temp: %0.1f' % amb_temp[0])+'*C'

	if fridge_hum is not None and fridge_temp is not None:
        	print 'Fridge temp: {0:0.1f}*C\nFridge humidity: {1:0.1f}%'.format(fridge_temp, fridge_hum)
	else:
        	print 'Failed to get reading. Try again!'
