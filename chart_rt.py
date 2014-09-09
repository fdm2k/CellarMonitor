#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

# unicode degrees symbol
degsym ='\u00b0'

# enable tracebacks of exceptions
cgitb.enable()

# grab the current, most recent sensor readings from the database
def get_latest_readings():
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    # setup database connection for querying
    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    # pull out latest db entries
    for row in curs.execute("SELECT datetime, ambient_temp,fridge_temp,fridge_humidity,outside_temp FROM temps ORDER BY datetime DESC LIMIT 1"):
      cur_reading = "['"+str(row[0])+"',"+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])+"]"

    # this will get revised in time - currently leaving it as-is for functionality
    return str(row).replace("(u'","").replace("'","").replace(")","")

# print an HTTP header
def printHTTPheader():
    # note: content-type must be printed first otherwise Server 500
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
      <div class="container center-block">
        <div class="navbar navbar-default">
          <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="/cgi-bin/chart_stats.py">CellarMon Home</a>
            </div>
            <div class="navbar-collapse collapse">
              <ul class="nav navbar-nav custom">
                <li><a href="/cgi-bin/chart_stats.py"><span class="glyphicon glyphicon-list"></span> Statistics</a></li>
                <li class="active"><a href="/cgi-bin/chart_rt.py"><span class="glyphicon glyphicon-dashboard"></span> Real-time</a></li>
                <li><a href="/cgi-bin/chart_1hr.py"><span class="glyphicon glyphicon-stats"></span> Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py"><span class="glyphicon glyphicon-stats"></span> Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py"><span class="glyphicon glyphicon-stats"></span> Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon <small>Real-Time Gauges</small></h2>
	      </div>"""

def printGauge(gauge_name, reading, yellowTo, redFrom, resultPercent=False):
    # set where the green band starts and finishes on the gauge
    greenFrom = int(yellowTo)
    greenTo = int(redFrom)

    printStr = """    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
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
        };""" % (gauge_name, float(reading), int(redFrom), int(greenFrom), int(greenTo), int(yellowTo))

    # check whether we're showing a percentage gauge or normal number
    if resultPercent:
	printStr = printStr+"""var formatter = new google.visualization.NumberFormat(
	{suffix: '%',pattern:'#'}
	);
	formatter.format(data,1);"""
    else:
        printStr = printStr+"""var formatter = new google.visualization.NumberFormat(
        {suffix: '%sC',pattern:'#'}
        );
        formatter.format(data,1);""" % degsym

    # wanted to split these up because of percentile formatting
    printStr = printStr+"""new google.visualization.Gauge(document.getElementById('%s')).draw(data, options);
	}
    </script>""" % gauge_name

    print printStr

# draw each gauge HTML
def printResultRow(gauge_name):
    print """      <div class="col-xs-12 col-sm-6 col-lg-3"><div id="%s" style="width: 146px; margin:auto"></div></div>""" % gauge_name

# finish the HTML
def printHTTPfooter():
    print """    </div>
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
    printGauge('Ambient', cur_ambient_temp.strip(" "), Ambient_yellowTo, Ambient_redFrom)
    printGauge('Fridge', cur_fridge_temp.strip(" "), Fridge_yellowTo, Fridge_redFrom)
    printGauge('Humidity', cur_fridge_humidity.strip(" "), Humidity_yellowTo, Humidity_redFrom, True)
    printGauge('Outside', cur_outside_temp.strip(" "), Outside_yellowTo, Outside_redFrom)
    print """    <div class="row container center-block">"""
    printResultRow('Ambient')
    printResultRow('Fridge')
    # fix responsive grid rendering weirdness
    print """      <div class="clearfix visible-sm-block"></div>"""
    printResultRow('Humidity')
    printResultRow('Outside')
    # fix responsive grid rendering weirdness
    print """      <div class="clearfix visible-sm-block"></div>"""
    print """      <div class="clearfix visible-lg-block"></div>"""
    # datetime stamp when the latest data was sucked in
    print "<small>Readings last updated: <code>"+str(cur_datetime)+"</code></small>"

    printHTTPfooter()

if __name__=="__main__":
    main()
