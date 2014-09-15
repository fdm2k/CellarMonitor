#!/usr/bin/python
import sqlite3

dbfile = '/home/pi/scripts/CellarMon/beerlist.db'
rowcount = 1

# Top 5 beers to drink now
top5drink_sql = "SELECT brewer, beer, type, bestbefore FROM beers WHERE status <> 'D' ORDER BY bestbefore ASC LIMIT 5;"

conn=sqlite3.connect(dbfile)
cur=conn.cursor()

# print table headers
sHTML = """<table>
  <th>Pos</th><th>Brewer</th><th>Beer</th><th>Type/Style</th><th>Best Before</th>\n"""

for row in cur.execute(top5drink_sql):
	sHTML = sHTML + "  <tr><td>"+str(rowcount)+"</td><td>"+str(row[0])+"</td><td>"+str(row[1])+"</td><td>"+str(row[2])+"</td><td>"+str(row[3])+"</td></tr>\n"
	rowcount += 1

sHTML = sHTML+"</table>"

print sHTML
conn.close()
