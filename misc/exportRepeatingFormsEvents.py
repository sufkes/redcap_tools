import pycurl, cStringIO, json

def exportRepeatingFormsEvents(api_url, api_key, project_repeating):
    """This function is used to export the instrument-event mapping. This functionality
    is not included in PyCap, so a custom function is defined here.

    Returns:
        list of dicts (one for each repeating instrument in each event) of the form:
        {u'event_name': u'event_1_arm_1', u'form_name': u'form_1', u'custom_form_label': u'[field_in_event]'}
"""
    
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
