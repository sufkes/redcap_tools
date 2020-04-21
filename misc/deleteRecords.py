#!/usr/bin/env python

"""
Delete records from REDCap project.

Usage:

 ./deleteRecords <API key> <record ID 1> [record ID 2] [record ID 3] ...
"""

# "Standard" modules
import os, sys
import pycurl, cStringIO

# "Non-standard" modules
import redcap

# My modules from current directory
from Color import Color
from exportProjectInfo import exportProjectInfo

def deleteRecords(api_url, api_key, record_id_list=None, quiet=False):
    """Remove specified records from a REDCap project. If no record IDs are specifed, all records are deleted."""

    if (not quiet):
        # Ask for user confirmation before proceeding.
        project_info = exportProjectInfo(api_url, api_key)
        print "Records will be permanently deleted from the following project:"
        print "-------------------------------------------------------------------------------------------------"
        print "Project Title: "+Color.blue+project_info["project_title"]+Color.end
        print "Project ID   : "+Color.blue+str(project_info["project_id"])+Color.end
        if (record_id_list == None):
            print "Records      :"+Color.blue+" All"+Color.end
        else:
            print "Records      :", record_id_list
        print "-------------------------------------------------------------------------------------------------"
        cont = bool(raw_input("Continue y/[n]? ") == 'y')
        if (not cont):
            print "Quitting"
            sys.exit()

    # Get list of all records if no record IDs specified.
    if (record_id_list == None):
        project = redcap.Project(api_url, api_key)
        record_id_list = project.export_records(fields=[project.def_field])
        record_id_list = [row[project.def_field] for row in record_id_list]
        record_id_list = list(set(record_id_list)) # remove duplicates
        
    buf = cStringIO.StringIO()
    data = {
        'token': api_key,
        'action': 'delete',
        'content': 'record',
    }

    # Add the list of record IDs to the 'data' dict.
    for record_index in range(len(record_id_list)):
        key = "records["+str(record_index)+"]"
        data[key] = record_id_list[record_index]

    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
#    print buf.getvalue()
    buf.close()

    return
