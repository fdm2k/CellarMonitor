#!/usr/bin/python
import sqlite3
import time
import cgi
import cgitb

dbfile = '/home/pi/scripts/CellarMon/beerlist.db'

# sql queries below
query_headers = ["Brewer","Beer","Type/Style","ABV"]
query_sql = "SELECT brewer, beer, type, abv2 FROM beers ORDER BY ABV2 DESC LIMIT 10;"

# enable tracebacks of exeptions
cgitb.enable()

# setup the database connection
conn=sqlite3.connect(dbfile)
cur=conn.cursor()

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
                <li><a href="/cgi-bin/chart_stats.py"><span class="glyphicon glyphicon-list"></span> Statistics</a></li>
		<li class="active"><a href="/cgi-bin/chart_beers.py"><span class="glyphicon glyphicon-tint"></span> Beer stats</a></li>
                <li><a href="/cgi-bin/chart_bcountry.py"><span class="glyphicon glyphicon-globe"></span> Beer Charts</a></li>
                <li><a href="/cgi-bin/chart_rt.py"><span class="glyphicon glyphicon-dashboard"></span> Real-time</a></li>
                <li><a href="/cgi-bin/chart_1hr.py"><span class="glyphicon glyphicon-stats"></span> Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py"><span class="glyphicon glyphicon-stats"></span> Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py"><span class="glyphicon glyphicon-stats"></span> Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon <small>Beer Lists</small></h2>
	      </div>"""

# build the table header
def printHTMLTableHeader(header_array, tabledesc = "Blank table", pos = False):
    print """
      <div class="row container">
        <div class="col-md-12 table-responsive">
	<h4>%s</h4>
          <table class="table table-bordered table-striped table-condensed">
            <thead>
              <tr>""" % tabledesc
    if pos:
	print "		<th>Pos.</th>"

    for item in header_array:
        print """		<th>%s</th>""" % item

    # print trailing table row, header and body
    print """              </tr>
            </thead>
	    <tbody>"""

# build the table rows
def printHTMLResult(sql_query, header_array, pos = False):
    rowcount = 1
    i = 0

    for row in cur.execute(sql_query):
        print """              <tr>"""
	if pos:
	  print "    <td><small>%s</small></td>" % str(rowcount)

	for i in range(0,len(header_array)):
	  if "price" in header_array[i].lower() or "spend" in header_array[i].lower():
            print "    <td><small>$%0.2f</small></td>" % float(row[i])
	  else:
	    print "    <td><small>%s</small></td>" % str(row[i])

        print """              </tr>"""
	rowcount += 1

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

def main():
    # print out the header section
    printHTMLheader()

    # build table of results
    printHTMLTableHeader(query_headers, "Beer Listing Test")
    printHTMLResult(query_sql, query_headers)
    printHTMLTableFooter()

    # print the HTTP footer
    printHTMLfooter()
    conn.close()

if __name__=="__main__":
    main()
