import pycurl, cStringIO, json

def exportRepeatingFormsEvents(api_url, api_key, project_repeating):
    """This function is used to export the instrument-event mapping. This functionality
    is not included in PyCap, so a custom function is defined here."""
    
    if (project_repeating):
        buf = cStringIO.StringIO()
        data = {'token': api_key, 'content': 'repeatingFormsEvents', 'format': 'json', 'returnFormat': 'json'}
        ch = pycurl.Curl()
        ch.setopt(ch.URL, api_url)
        ch.setopt(ch.HTTPPOST, data.items())
        ch.setopt(ch.WRITEFUNCTION, buf.write)
        ch.perform()
        ch.close()
        repeating_forms_events = json.loads(buf.getvalue())
        buf.close()
    else: 
        repeating_forms_events = None
    return repeating_forms_events
