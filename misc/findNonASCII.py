#!/usr/bin/env python
from exportRecords import exportRecords
import sys

#record_id_list = ["7-1001", "292", "155", "559-2"]
record_id_list = None
data = exportRecords('https://redcapexternal.research.sickkids.ca/api/', str(sys.argv[1]), record_id_list=record_id_list, events=None, fields=None, forms=None, format='json', quiet=False, chunk_thres=1000000, chunk_size=400)

for row_index in range(len(data)):
    row = data[row_index]
    for key in row:
        elem = row[key]
        if (key == "redcap_repeat_instance"):
            continue
        try:
            utf = elem.encode('ascii')
        except UnicodeEncodeError:
            print "Non-ascii character in record "+str(row["ipssid"])+", field "+key+", event "+str(row["redcap_event_name"])+" "+str(row["redcap_repeat_instance"])
