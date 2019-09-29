import pycurl, cStringIO, json

def exportFormsOrdered(api_url, api_key):
    """This script returns information about each data instrument (e.g. the name of the instrument,
    the instrument name which appears online). While the instrument names can be gotten using PyCap
    in the attribute project.forms, this attribute does not have the same ordering of the forms as
    online. This script preserves ordering."""
    buf = cStringIO.StringIO()
    data = {
        'token': api_key,
        'content': 'instrument',
        'format': 'json',
        'returnFormat': 'json'
    }
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    forms = json.loads(buf.getvalue())
    buf.close()
    return forms
