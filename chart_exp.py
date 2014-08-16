#!/usr/bin/env python
import cgi
import cgitb
import sqlite3

# enable tracebacks of exceptions
cgitb.enable()

# print data from a file formatted as a javascript array
# return a string containing the table
def print_table():
    rownum = 0
    string = ""
    dbfile = '/home/pi/scripts/templog.db'

    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    cursor = conn.execute("SELECT COUNT(datetime) FROM temps")
    for row in cursor:
        totalrows = str(row[0]).replace(" ","")

    for row in curs.execute("SELECT datetime, ambient_temp, fridge_temp, fridge_humidity, outside_temp FROM temps WHERE datetime >= date('now','-1 day')"):
        rownum += 1
        string = string+"[new Date('"+str(row[0])+"'),"+str(row[1])+","+str(row[2])+","+str(row[3])+"]"
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
              <a class="navbar-brand" href="/cgi-bin/chart_rt.py">CellarMon Home</a>
            </div>
            <div class="navbar-collapse collapse">
              <ul class="nav navbar-nav">
                <li><a href="/cgi-bin/chart_rt.py">Real-time</a></li>
                <li class="active"><a href="#">Historical</a></li>
                <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-toggle="dropdown">Chart Types <span class="caret"></span></a>
                  <ul class="dropdown-menu" role="menu">
                    <li><a href="#">Line chart</a></li>
                    <li><a href="#">Bar chart</a></li>
                    <li><a href="#">Awesome chart</a></li>
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

# Main program body
def main():
    # print out the header section
    printHTTPheader()

    # this string contains the web page that will be served
    page_str="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load("visualization", "1", {packages:["corechart"]});
        google.setOnLoadCallback(drawChart);

      function drawChart() {
        var data = google.visualization.DataTable();
	data.addColumn('datetime','Datetime');
	data.addColumn('number',''Ambient Temp');
	data.addColumn('number','Fridge Temp');
	data.addColumn('number','Fridge Humidity');
	data.addRows([
	  %s
	  ]);

        var options = {
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
	  hAxis: {format: 'YYYY-MM-DD HH:MM'},
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
	  <div class="col-sm-6 col-lg-3" id="chart_div" style="width: 100%%; height: 500px">Container #1</div>
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
