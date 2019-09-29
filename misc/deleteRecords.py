#!/usr/bin/env python

"""
Delete records from REDCap project.

Usage:

 ./deleteRecords <API key> <record ID 1> [record ID 2] [record ID 3] ...
"""

import sys
import pycurl, cStringIO

api_key = str(sys.argv[1])

record_list = []
for arg in sys.argv[2:]:
    record_list.append(str(arg))

buf = cStringIO.StringIO()
data = {
    'token': api_key,
    'action': 'delete',
    'content': 'record',
}

for record_index in range(len(record_list)):
    key = "records["+str(record_index)+"]"
    data[key] = record_list[record_index]

print data

ch = pycurl.Curl()
ch.setopt(ch.URL, 'https://redcapexternal.research.sickkids.ca/api/')
ch.setopt(ch.HTTPPOST, data.items())
ch.setopt(ch.WRITEFUNCTION, buf.write)
ch.perform()
ch.close()
print buf.getvalue()
buf.close()

