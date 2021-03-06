#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import cgitb
import sqlite3
import time

column_array = ['ambient_temp','fridge_temp','fridge_humidity','outside_temp']
column_headings = ['Ambient temp','Fridge temp','Fridge humidity','Outside temp']
stat_array = ['Min','Max','Avg']

# setup appropriate visual variables
colourbar = 'info'
degsym = "°"

# enable tracebacks of exceptions
cgitb.enable()

def get_rowcount():
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    # open a connection to the database
    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    # get result
    for row in curs.execute("SELECT count(datetime) FROM temps"):
	rowcount = str(row[0])

    return rowcount

# grab the current, most recent readings from the sensors
def get_datetime(first = True):
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    # open a connection to the database
    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    # get result
    if first:
        for row in curs.execute("SELECT datetime FROM temps ORDER BY datetime ASC LIMIT 1"):
          result = str(row[0])
    else:
        for row in curs.execute("SELECT datetime FROM temps ORDER BY datetime DESC LIMIT 1"):
	  result = str(row[0])

    return result

# grab the current, most recent readings from the sensors
def get_stats(stat, column_name, curdate = False):
    dbfile = '/home/pi/scripts/CellarMon/templog.db'

    if curdate:
	sqlquery = "SELECT "+stat+"("+column_name+"), datetime FROM temps where datetime >= '"+time.strftime('%Y-%m-%d')+" 00:00'"
    else:
	sqlquery = "SELECT "+stat+"("+column_name+") FROM temps"
	
    # open a connection to the database
    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    # get result
    for row in curs.execute(sqlquery):
	if curdate:
	  #new_date = time.strptime(row[1], '%y-%m-%j %H:%M:%S')
	  #print new_date
	  result = str(row[0]), row[1]

	else:
	  result = str(row[0])

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
                <li class="active"><a href="/cgi-bin/chart_stats.py"><span class="glyphicon glyphicon-list"></span> Statistics</a></li>
                <li><a href="/cgi-bin/chart_rt.py"><span class="glyphicon glyphicon-dashboard"></span> Real-time</a></li>
                <li><a href="/cgi-bin/chart_beers.py"><span class="glyphicon glyphicon-tint"></span> Beer Stats</a></li>
                <li><a href="/cgi-bin/chart_bcountry.py"><span class="glyphicon glyphicon-globe"></span> Beer Charts</a></li>
                <li><a href="/cgi-bin/chart_1hr.py"><span class="glyphicon glyphicon-stats"></span> Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py"><span class="glyphicon glyphicon-stats"></span> Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py"><span class="glyphicon glyphicon-stats"></span> Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon <small>Temp Statistics</small></h2>
	      </div>"""

# build the table header
def printHTMLTableHeader():
    print """
      <div class="row container">
        <div class="col-md-6 table-responsive">
          <table class="table table-bordered table-striped">
            <thead>
              <tr>
                <th>Statistic</th>"""
    for item in stat_array:
        print """		<th>%s</th>""" % item

    # print trailing table row, header and body
    print """              </tr>
            </thead>
	    <tbody>"""

# build the table rows
def printHTMLResult(colour_state, column_name, friendly_column_name):
    # first determine whether to background-colour the table row or not
    #if colour_state:
    #    print """              <tr class="%s">""" % colourbar
    #else:
    print """              <tr>"""

    print """		<td>%s</td>""" % friendly_column_name

    for item in stat_array:
	result = get_stats(item, column_name)
	if friendly_column_name.find("temp") > 0:
	  print """		<td>%0.1f%s</td>""" % (float(result),degsym)
	else:
	  print """		<td>%0.0f%%</td>""" % float(result)

    print """              </tr>"""

# build the table footer
def printHTMLTableFooter():
    print """	    </tbody>
          </table>
        </div>
    </div>"""

# finish the HTML
def printHTMLfooter():
    print """    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="../dist/js/bootstrap.min.js"></script>
    <script src="../assets/js/docs.min.js"></script>
    </body>
</html>"""

# Main program body
def main():
    # set the colour bar colour for the first row
    colourbar_state = True
    heading = 0

    # print out the header section
    printHTMLheader()

    # build the table of results
    printHTMLTableHeader()
    for item in column_array:
	# loop through each available column and print all the defined stats
	printHTMLResult(colourbar_state, item, column_headings[heading])
	colourbar_state = not colourbar_state
	heading += 1

    printHTMLTableFooter()

    # print latest DB entry date
    print "    <p><small>First reading in database: <code>"+str(get_datetime(True))+"</code></small></p>"
    print "    <p><small>Last reading in database: <code>"+str(get_datetime(False))+"</code></small></p>"
    print "    <p><small>Total rows in database: <code>"+str(get_rowcount())+" rows</code></small></p>"

    # print out max temp so far today
    todays_max = get_stats("max", "fridge_temp", True)
    print "    <p><small>Max fridge_temp for today: <code>%0.2f%sC @ %s</code></small></p>" % (float(todays_max[0]),degsym,str(todays_max[1]))

    # print the HTTP footer
    printHTMLfooter()

if __name__=="__main__":
    main()
