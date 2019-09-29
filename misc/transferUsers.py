#!/usr/bin/env python

api_key_1 = str(sys.argv[1])
api_key_2 = str(sys.argv[2])

import pprint
import pycurl, cStringIO
import json
buf = cStringIO.StringIO()
data = {
    'token': api_key_1,
    'content': 'user',
    'format': 'json',
    'returnFormat': 'json'
}
ch = pycurl.Curl()
ch.setopt(ch.URL, 'https://redcapexternal.research.sickkids.ca/api/')
ch.setopt(ch.HTTPPOST, data.items())
ch.setopt(ch.WRITEFUNCTION, buf.write)
ch.perform()
ch.close()
other_buf_json = json.loads(buf.getvalue())
buf.close()

# Remove data access groups and forms persmissions (if incompatible).
# The group_id appears to change, so only the group name should be transfered.
for user_index in range(len(other_buf_json)):
    for key in ["data_access_group_id", "forms"]: # "data_access_group", "data_access_group_id", "forms" 
        other_buf_json[user_index].pop(key, None)


# Convert to JSON result string in Python.
other_buf_json = json.dumps(other_buf_json)

buf = cStringIO.StringIO()
data = {
    'token': api_key_2,
    'content': 'user',
    'format': 'json',
    'data': other_buf_json,
    'returnFormat': 'json'
}
ch = pycurl.Curl()
ch.setopt(ch.URL, 'https://redcapexternal.research.sickkids.ca/api/')
ch.setopt(ch.HTTPPOST, data.items())
ch.setopt(ch.WRITEFUNCTION, buf.write)
ch.perform()
ch.close()
print buf.getvalue()
buf.close()
