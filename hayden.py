#!/usr/bin/env python

from datetime import datetime
from os import environ
import pandas
import logging

logger = logging.getLogger('ercot-fetch')
logging.basicConfig(level=environ.get('LOG_LEVEL', 'DEBUG').upper())

start = datetime.today()

logging.info("Running scraper at {datetime}".format(datetime=start.strftime("%Y-%m-%d %H:%M:%S")))

fetch_url = "http://www.ercot.com/content/cdr/html/{today}_real_time_spp".format(today=start.strftime("%Y%m%d"))
logging.info("Opening webpage: {url}".format(url=fetch_url))
response = pandas.read_html(fetch_url, header=0)
number_of_table_rows = len(response[0])
logging.info("Grabbing data. Number of rows: {rows}".format(rows=number_of_table_rows))

# Just a simple list of the columns in the table without the day and hour
data_columns = response[0].columns[2:]
sql_values = []

logging.info("Building SQL Statement")
for index, row in response[0].iterrows():
    # Create a datetime object from date and time fields from the table
    timestamp = datetime.strptime(
        "{date} {time}".format(date=getattr(row, "Oper Day"), time=str(getattr(row, "Interval Ending")).zfill(4)),
        "%m/%d/%Y %H%M")

    # iterate the columns we pulled out back at line 22
    for column_name in data_columns:
        """
        Create a values grouping for the insert query
        
        This does not necessarily accommodate for SQL injection possibilities.
        It could be mitigated using a database framework with prepared statements and parameters
        """
        sql_values.append("(\"{hour}\",\"{zone}\",\"{price}\")".format(
            hour=timestamp.isoformat(),
            zone=column_name,
            price=getattr(row, column_name)
        ))

# Insert the list of value strings into the insert SQL.
sql = "INSERT IGNORE INTO some_table (`hour`, `zone`, `price`) VALUES {sql_values};".format(
    sql_values=",".join(sql_values))

print(sql)

end = datetime.today()
logging.info("Completed scraper at {datetime}".format(datetime=end.strftime("%Y-%m-%d %H:%M:%S")))
