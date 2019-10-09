#!/usr/bin/env python

def importMetadata(api_url, api_key, metadata, format=):
import pycurl, cStringIO
buf = cStringIO.StringIO()
data = {
    'token': 'B757D6B065DFC9259A05A10C94994C67',
    'content': 'metadata',
    'format': 'csv',
    'data': '',
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
