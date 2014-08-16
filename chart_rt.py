#!/usr/bin/env python
import cgi
import cgitb
import sqlite3
import Adafruit_DHT
from ds18b20 import DS18B20

# setup GPIO-related variables
hum_sensor = 22
hum_pin = 17
amb_sensor = DS18B20()

# setup gauge limits
Ambient_yellowTo = 5
Ambient_redFrom = 25
Fridge_yellowTo = 9
Fridge_redFrom = 14
Humidity_yellowTo = 50
Humidity_redFrom = 75
Outside_yellowTo = 2
Outside_redFrom = 35

#rt_fridge_humidity, rt_fridge_temp = Adafruit_DHT.read_retry(hum_sensor, hum_pin)
#amb_temp_array = amb_sensor.get_temperatures([DS18B20.DEGREES_C, DS18B20.DEGREES_F, DS18B20.KELVIN])
#rt_ambient_temp = amb_temp_array[0]

#print "Ambient temp: "+str(rt_ambient_temp)
#print "Fridge temp: "+str(rt_fridge_temp)
#print "Fridge humidity: "+str(rt_fridge_humidity)

# enable tracebacks of exceptions
cgitb.enable()

# grab the current, most recent readings from the sensors
def get_latest_readings():
    dbfile = '/home/pi/scripts/templog.db'

    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    for row in curs.execute("SELECT datetime, ambient_temp,fridge_temp,fridge_humidity,outside_temp FROM temps ORDER BY datetime DESC LIMIT 1"):
      cur_reading = "['"+str(row[0])+"',"+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])+"]"

    #return cur_datetime, cur_ambient_temp, cur_fridge_temp, cur_fridge_humidity, cur_outside_temp
    return str(row).replace("(u'","").replace("'","").replace(")","")

# print an HTTP header
def printHTTPheader():
    print "Content-type: text/html"
    print """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    	<meta charset="utf-8">
    	<meta http-equiv="X-UA-Compatible" content="IE=edge">
    	<meta name="viewport" content="width=device-width, initial-scale=1">
    	<meta name="description" content="">
    	<meta name="author" content="">
    	<link rel="icon" href="/favicon.ico">

      <title>CellarMon: Beer Cellar Monitor</title>

	    <!-- Bootstrap core CSS -->
      <link href="/css/bootstrap.min.css" rel="stylesheet">

    	<!-- Custom styles for this template -->
      <link href="/grid.css" rel="stylesheet">

      <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
      <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
      <script src="/assets/js/ie-emulation-modes-warning.js"></script>

      <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
      <script src="/assets/js/ie10-viewport-bug-workaround.js"></script>

      <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
      <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
        <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
      <![endif]-->
    </head>

    <body>
      <div class="container">
        <div class="navbar navbar-default">
          <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="#">CellarMon Home</a>
            </div>
            <div class="navbar-collapse collapse">
              <ul class="nav navbar-nav">
                <li class="active"><a href="/cgi-bin/chart_rt.py">Real-time</a></li>
                <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-toggle="dropdown">Historical Charts<span class="caret"></span></a>
                  <ul class="dropdown-menu" role="menu">
                    <li><a href="/cgi-bin/chart.py">Last 24 hrs</a></li>
                    <li><a href="/cgi-bin/chart_7day.py">Last 7 days</a></li>
                    <li><a href="/cgi-bin/chart_lh.py">Last hour</a></li>
                    <li class="divider"></li>
                    <li><a href="#">Colour scheme #2</a></li>
                  </ul>
                </li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon: Beer Cellar Temp Monitor</h2>
	      </div>"""

def printGauge(gauge_name, reading, yellowTo, redFrom):
    greenFrom = int(yellowTo)
    greenTo = int(redFrom)

    print """
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["gauge"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['%s', %0.1f],
        ]);

        var options = {
          width: 300, height: 150,
          redFrom: %d, redTo: 100,
          greenFrom: %d, greenTo: %d,
          yellowFrom:0, yellowTo: %d,
          minorTicks: 10
        };

        new google.visualization.Gauge(document.getElementById('%s')).draw(data, options);
      }
    </script>""" % (gauge_name, float(reading), int(redFrom), int(greenFrom), int(greenTo), int(yellowTo), gauge_name)

# draw each gauge HTML
def printResultRow(gauge_name):
    print """      <div class="col-sm-6 col-lg-3 center-block" id="%s"></div>""" % gauge_name

# finish the HTML
def printHTTPfooter():
    print """
    </div>
    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="../dist/js/bootstrap.min.js"></script>
    <script src="../assets/js/docs.min.js"></script>
    </body>
</html>"""

# Main program body
def main():
    # get the latest temp readings
    cur_datetime, cur_ambient_temp, cur_fridge_temp, cur_fridge_humidity, cur_outside_temp = str(get_latest_readings()).split(",")

    # print out the header section
    printHTTPheader()

    # print gauges, values and limits
    printGauge('Ambient', cur_ambient_temp.strip(" "),Ambient_yellowTo,Ambient_redFrom)
    printGauge('Fridge', cur_fridge_temp.strip(" "),Fridge_yellowTo,Fridge_redFrom)
    printGauge('Humidity', cur_fridge_humidity.strip(" "),Humidity_yellowTo,Humidity_redFrom)
    printGauge('Outside', cur_outside_temp.strip(" "),Outside_yellowTo,Outside_redFrom)
    print """    <div class="row">"""
    printResultRow('Ambient')
    printResultRow('Fridge')
    print """      <div class="clearfix visible-sm-block"></div>"""
    printResultRow('Humidity')
    printResultRow('Outside')
    print """      <div class="clearfix visible-sm-block"></div>"""
    print """      <div class="clearfix visible-lg-block"></div>"""

    printHTTPfooter()

if __name__=="__main__":
    main()
