import pycurl, cStringIO, json

def exportProjectInfo(api_url, api_key):
    """This function is used to export the high-level information about the project
    (e.g. project name, whether longitudinal, whether repeating events are used). This 
    functionality is not included in PyCap, so a custom function is defined here."""
    buf = cStringIO.StringIO()
    data = {'token': api_key, 'content': 'project', 'format': 'json', 'returnFormat': 'json'}
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    project_info = json.loads(buf.getvalue())
    buf.close()
    return project_info
