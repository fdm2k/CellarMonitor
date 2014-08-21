#!/usr/bin/env python
import cgi
import cgitb
import sqlite3
import time

# enable tracebacks of exceptions
cgitb.enable()

# grab the current, most recent readings from the sensors
def get_stats(column_name):
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    # open a connection to the database
    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    # get result
    for row in curs.execute("SELECT min("+column_name+"), max("+column_name+"), avg("+column_name+") FROM temps"):
	#result = str(row[0])+","+str(row[1])
	result = str(row[0])+","+str(row[1])+","+str(row[2])

    return result

# print an HTTP header
def printHTMLheader():
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
      <link href="/custnav.css" rel="stylesheet">

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
              <ul class="nav navbar-nav custom">
                <li class="active"><a href="/cgi-bin/chart_stats.py">Statistics</a></li>
                <li><a href="/cgi-bin/chart_rt.py">Real-time</a></li>
                <li><a href="/cgi-bin/chart_1hr.py">Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py">Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py">Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon: Beer Cellar Temp Monitor</h2>
	      </div>"""

# build the table header
def printHTMLTableHeader():
    print """
    <div class="row">
        <div class="col-md-6 table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Statistic</th>
                <th>Min</th>
                <th>Max</th>
		<th>Avg</th>
              </tr>
            </thead>"""

# build the table rows
def printHTMLResult(colour, column_name):
    rmin, rmax, ravg = get_stats(column_name).split(",")
    
    print """
            <tbody>
              <tr class="%s">
                <td>%s</td>
                <td>%0.2f</td>
                <td>%0.2f</td>
		<td>%0.2f</td>
              </tr>
            </tbody>""" % (colour, column_name, float(rmin), float(rmax), float(ravg))

# build the table footer
def printHTMLTableFooter():
    print """
          </table>
        </div>"""

# finish the HTML
def printHTMLfooter():
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
    # print out the header section
    printHTMLheader()

    # build the table of results
    printHTMLTableHeader()
    printHTMLResult("info", "ambient_temp")
    printHTMLResult("","fridge_temp")
    printHTMLResult("info","fridge_humidity")
    printHTMLResult("","outside_temp")
    printHTMLTableFooter()

    # print the HTTP footer
    printHTMLfooter()

if __name__=="__main__":
    main()
