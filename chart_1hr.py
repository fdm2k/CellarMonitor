#!/usr/bin/env python
import cgi
import cgitb
import sqlite3

# enable tracebacks of exceptions
cgitb.enable()

# grab the current, most recent readings from the sensors
def get_latest_readings():
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    for row in curs.execute("SELECT datetime, ambient_temp,fridge_temp,fridge_humidity,outside_temp FROM temps ORDER BY datetime DESC LIMIT 1"):
      cur_reading = "['"+str(row[0])+"',"+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])+"]"

    #return cur_datetime, cur_ambient_temp, cur_fridge_temp, cur_fridge_humidity, cur_outside_temp
    return str(row).replace("(u'","").replace("'","").replace(")","")

# print data from a file formatted as a javascript array
# return a string containing the table
def print_table():
    rownum = 0
    string = ""
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    cursor = conn.execute("SELECT COUNT(datetime) FROM temps")
    for row in cursor:
        totalrows = str(row[0]).replace(" ","")

    for row in curs.execute("SELECT datetime, ambient_temp, fridge_temp, fridge_humidity, outside_temp FROM temps WHERE datetime >= datetime('now','+6.5 hours')"):
        rownum += 1
        string = string+"['"+str(row[0])+"',"+str(row[1])+","+str(row[2])+","+str(row[3])+"]"
        if str(rownum) <> str(totalrows):
	    string = str(string)+",\n\t  "
        else:
	    string = str(string)+"\n"

    conn.close()
    return string

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
              <a class="navbar-brand" href="/cgi-bin/chart_stats.py">CellarMon Home</a>
            </div>
            <div class="navbar-collapse collapse">
              <ul class="nav navbar-nav">
		<li><a href="/cgi-bin/chart_stats.py">Statistics</a></li>
                <li><a href="/cgi-bin/chart_rt.py">Real-time</a></li>
                <li class="active"><a href="/cgi-bin/chart_1hr.py">Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py">Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py">Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon: Beer Cellar Temp Monitor</h2>
	</div>"""

# Main program body
def main():
    # get the latest temp readings
    cur_datetime, cur_ambient_temp, cur_fridge_temp, cur_fridge_humidity, cur_outside_temp = str(get_latest_readings()).split(",")

    # print out the header section
    printHTTPheader()

    # this string contains the web page that will be served
    page_str="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load("visualization", "1", {packages:["corechart"]});
        google.setOnLoadCallback(drawChart);

      function drawChart() {
        var data = google.visualization.arrayToDataTable([
	  ['Date Time','Ambient Temp','Fridge Temp','Fridge Humidity'],
	  %s
	  ]);

        var options = {
          title: 'Last 3 hours',
          titleFontSize: 20,
	  curveType: 'function',
	  lineWidth: 2,
	  vAxes: {
		0: {
	           // options for left y-axis
		   title: 'Temperatures'
	    	},
		1: {
        	   // options for right y-axis
		   minValue: 0,
		   maxValue: 100,
		   title: 'Humidity'
		}
	  },
	  hAxis: {
		format: 'HH:MM',
                textStyle:{fontSize: 12},
	  },
	  series: {
          	0: { targetAxisIndex: 0, color: '#5F79AB' },
          	1: { targetAxisIndex: 0, color: '#51B85C' },
        	2: { targetAxisIndex: 1, color: '#99A3CC', lineDashStyle: [4, 1] },
	  },
	  legend: { position: 'bottom' }
	  
        };

        new google.visualization.AreaChart(document.getElementById('chart_div')).draw(data, options);
      }
    </script>
	<div class="row">
	  <div class="col-sm-6 col-lg-3" id="chart_div" style="width: 900px; height: 500px"></div>
	</div>
    
      <!-- Bootstrap core JavaScript
      ================================================== -->
      <!-- Placed at the end of the document so the pages load faster -->
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
      <script src="../dist/js/bootstrap.min.js"></script>
      <script src="../assets/js/docs.min.js"></script>
  </body>
</html>""" % print_table()

    # serve the page with the data table embedded in it
    print page_str

if __name__=="__main__":
    main()
