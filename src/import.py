import mysql.connector
import rjis
import re

# connect to the mysql database
database = mysql.connector.connect(
    host="localhost",
    user="user",
    passwd="password"
)

rjis.process('../sample-data')

