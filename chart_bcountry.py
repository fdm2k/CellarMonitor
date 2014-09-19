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
    dbfile = '/home/pi/scripts/CellarMon/beerlist.db'

    conn=sqlite3.connect(dbfile)
    curs=conn.cursor()

    cursor = conn.execute("SELECT COUNT(brewcountry) FROM beers")
    for row in cursor:
        totalrows = str(row[0]).replace(" ","")

    for row in curs.execute("select brewcountry, count(brewcountry) as bc_count from beers group by brewcountry order by bc_count desc;"):
        rownum += 1
        string = string+"['"+str(row[0])+"',"+str(row[1])+"]"
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
                <li><a href="/cgi-bin/chart_stats.py"><span class="glyphicon glyphicon-list"></span> Statistics</a></li>
                <li><a href="/cgi-bin/chart_rt.py"><span class="glyphicon glyphicon-dashboard"></span> Real-time</a></li>
		<li class="active"><a href="/cgi-bin/chart_bcountry.py"><span class="glyphicon glyphicon-globe"></span> Beer #2</a></li>
                <li><a href="/cgi-bin/chart_1hr.py"><span class="glyphicon glyphicon-stats"></span> Last 3 hrs</a></li>
                <li><a href="/cgi-bin/chart.py"><span class="glyphicon glyphicon-stats"></span> Last 24 hrs</a></li>
                <li><a href="/cgi-bin/chart_7day.py"><span class="glyphicon glyphicon-stats"></span> Last 7 days</a></li>
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
        <div class="page-header">
          <h2>CellarMon <small>Beer brewery map</small></h2>
	</div>"""

# Main program body
def main():
    # print out the header section
    printHTTPheader()

    # this string contains the web page that will be served
    page_str="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
        google.load("visualization", "1", {packages:["geochart"]});
        google.setOnLoadCallback(drawRegionsMap);

      function drawRegionsMap() {
        var data = google.visualization.arrayToDataTable([
	  ['Country','Beer Count'],
	  %s
	  ]);

	var options = {};

        var chart = new google.visualization.GeoChart(document.getElementById('chart_div'));

	chart.draw(data, options);
      }
    </script>
	<div class="row center-block">
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
