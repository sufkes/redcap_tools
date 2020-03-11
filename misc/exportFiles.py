#!/usr/bin/env python

# Standard modules
import os, sys
import pycurl, cStringIO

# Non-standard modules 
import redcap # PyCap

# My modules in this directory
from exportProjectInfo import exportProjectInfo
from exportRecords import exportRecords

def exportFile(out_dir, api_url, api_key, record, event, instance, field, prefix=None):
    """Export a single file which was uploaded to a REDCap File Upload field. Save the file using the name of the file as stored in REDCap, and a prefix including the record ID, event, instance, and field.
Parameters:
    out_dir: str, directory to save output to
    api_url: str, API URL of REDCap instance
    api_key: str, user's API token
    record: str, record ID to which file was uploaded
    event: str, name of event to which file was uploaded
    instance: str, repeat instance to which file was uploaded
    field: str, name of the 'file' field which is being exported
    prefix: str, text to prepend to file name.
    """
    file_contents_buffer = cStringIO.StringIO()
    header_buffer = cStringIO.StringIO()
    response_code_buffer = cStringIO.StringIO()
    data = {
        'token': api_key,
        'content': 'file',
        'action': 'export',
        'record': record,
        'field': field,
        'repeat_instance': instance,
        'event': event,
        'returnFormat': 'json'}
    
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, file_contents_buffer.write)
    ch.setopt(ch.HEADERFUNCTION, header_buffer.write)
    ch.perform()
    http_response_code = ch.getinfo(pycurl.HTTP_CODE)
    ch.close()

    # Check whether request actually succeeded based on the response HTTP code. I don't know if this is a good way to check.
    if (http_response_code != 200):
        raise ValueError('HTTP request failed with parameters:\n'+str(data)+'\nThe HTTP response header is:\n'+str(header_buffer.getvalue()))
        return
    
    # Get the name of the file as it is stored on REDCap, using the HTTP header. I DON'T KNOW IF THIS METHOD IS SAFE OR PORTABLE. EXCEPT ALL ERRORS WHICH OCCUR IN THIS ATTEMPT, AND SET file_name TO BLANK IF THIS CHECK FAILS.
    header_lines = header_buffer.getvalue().split('\n')
    file_name = ''
    try:
        for line in header_lines: # Get the file name from the HTTP header. 
            if (line[:12] == 'Content-Type'):
                file_name = line.split('name="')[1].split('"')[0]
    except:
        pass
    # Print error if file name was not determined
    if (file_name == ''):
        print "Warning: Unable to determine file name for file retrieved from request with parameters:", data

    # Add prefix to file name if one was specified.
    if (prefix != None):
        file_name = prefix + file_name

    out_path = os.path.join(out_dir, file_name)
        
    with open(out_path, 'wb') as handle:
        handle.write(file_contents_buffer.getvalue())
    file_contents_buffer.close()
    header_buffer.close()
    return 

def exportFiles(api_url, api_key, out_dir, flat=False):
    """Export all files stored in File Upload fields (this does not include files upload to the 'File Repository'.
Parameters:
    api_url: str, API URL of REDCap instance on which project is housed.
    api_key: str, user's API token
    out_dir: str, the directory in which the files
    flat: bool, if True, save all files in the same output directory, if False, create subdirectories to store files from distinct records, events, and instances."""

    ## Determine whether project is longitudinal, and whether it has repeating forms or events.
    project = redcap.Project(api_url, api_key)
    def_field = project.def_field
    project_info = exportProjectInfo(api_url, api_key)
    project_longitudinal = bool(project_info["is_longitudinal"])
    project_repeating = bool(project_info["has_repeating_instruments_or_events"])
    primary_key = [def_field]
    if project_longitudinal:
        primary_key.append('redcap_event_name')
    if project_repeating:
        primary_key.append('redcap_repeat_instrument')
        primary_key.append('redcap_repeat_instance')
    non_data_fields = primary_key + ['redcap_data_access_group']
    
    ## Identify all File Upload fields.
    file_upload_fields = []
    metadata_raw = project.export_metadata() # list of dicts
    for row in metadata_raw:
        if (row['field_type'] == 'file'):
            file_upload_fields.append(row['field_name'])
    
    ## Determine which File Upload fields have an uploaded file. Export and save every file in the File Upload fields.
    if (len(file_upload_fields) == 0):
        return # Quit if there are no File upload fields
        pass
    
    records = exportRecords(api_url, api_key, fields=file_upload_fields) # should contain text like "[document]" to indicate where a file was uploaded
    
    for row in records:
        for field, value in row.iteritems():
            if (field in non_data_fields):
                continue
            if (value != ''): # if field is a File Upload field containing a file.
                record = row[def_field]
                if project_longitudinal:
                    event = row['redcap_event_name']
                else:
                    event = ''
                if project_repeating:
                    instance = str(row['redcap_repeat_instance'])
                else:
                    instance = ''

                # Set the file name prefix and output directory using the record id, event, and instance.
                if flat:
                    prefix = 'record-'+record+'_'
                    if project_longitudinal: # There is always an event name in longitudinal projects.
                        prefix += 'event-'+event+'_'
                    if (instance != ''): # don't add blank instances to prefix.
                        prefix += 'instance-'+instance+'_'
                    prefix += 'field-'+field+'_'
                    prefix += 'filename-'
                    full_out_dir = out_dir # save all files to the same directory
                else:
                    prefix = 'field-'+field+'_'
                    prefix += 'filename-'
                    full_out_dir = os.path.join(out_dir, 'record-'+record)
                    if project_longitudinal: # There is always an event name in longitudinal projects.
                        full_out_dir = os.path.join(full_out_dir, 'event-'+event)
                    if (instance != ''): # don't add blank instances to prefix.
                        full_out_dir = os.path.join(full_out_dir, 'instance-'+instance)
                    if (not os.path.isdir(full_out_dir)):
                        #print "Creating directory: "+full_out_dir
                        os.makedirs(full_out_dir)

                # Export the file.
o                exportFile(full_out_dir, api_url, api_key, record, event, instance, field, prefix=prefix)
