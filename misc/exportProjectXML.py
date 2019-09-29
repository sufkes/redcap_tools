import pycurl, cStringIO

def exportProjectXML(api_url, api_key):
    buf = cStringIO.StringIO()
    data = {
        'token': api_key,
        'content': 'project_xml',
        'format': 'json',
        'returnMetadataOnly': 'true',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
        }
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
#    with open('ipss.xml', 'w') as fh:
#        fh.write(buf.getvalue())
    project_xml = buf.getvalue()
    buf.close()
    return project_xml
