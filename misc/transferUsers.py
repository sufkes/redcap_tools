#!/usr/bin/env python

# Standard modules
import sys
import pycurl, cStringIO
import json
import argparse

# My modules in current directory
from ApiSettings import ApiSettings

def transferUsers(api_url_1, api_url_2, api_key_1, api_key_2):
    """Add users and user permissions from one REDCap project to another.
Parameters
----------
    api_url_1 : str
        API URL for project from which users are being exported
    api_url_2 : str
        API URL for project to which users are being imported
    api_key_1 : str
        API token for project from which users are being exported
    api_key_2 : str
        API token for project to which users are being imported

Returns
-------
    None"""
    buf = cStringIO.StringIO()
    data = {
        'token': api_key_1,
        'content': 'user',
        'format': 'json',
        'returnFormat': 'json'
       }
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url_1)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    other_buf_json = json.loads(buf.getvalue())
    buf.close()
    
    # Remove data access groups and forms permissions (if incompatible).
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
    ch.setopt(ch.URL, api_url_2)
    ch.setopt(ch.HTTPPOST, data.items())
    ch.setopt(ch.WRITEFUNCTION, buf.write)
    ch.perform()
    ch.close()
    print buf.getvalue()
    buf.close()
    return

if (__name__ == '__main__'):
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.
    
    ## Create argument parser.
    description = """Transfer users from one REDCap project to another. Data access group ID numbers, and users roles are not preserved.

Specify the code names (or API tokens) of two projects. The first project is the one from which users will be exported; the second project is the one to which users will be imported."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.

    ## Define keyword arguments.
    # Add arguments for API URL, API key, and code name of project used to retreive these.
    parser = api_settings.addApiArgs(parser, num_projects=2) # Adds args "-n", "--code_names", "-k", "--api_keys", "-u", "--api_urls" to the argument parser.
        
    # Print help message if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()
    
    # Parse arguments.
    args = parser.parse_args()
    
    # Determine the API URL and API token based on the users input and api_keys.json file.
    api_url_1, api_key_1, code_name_1 = api_settings.getApiCredentials(api_url=args.api_urls[0], api_key=args.api_keys[0], code_name=args.code_names[0])
    api_url_2, api_key_2, code_name_2 = api_settings.getApiCredentials(api_url=args.api_urls[1], api_key=args.api_keys[1], code_name=args.code_names[1])

    # Transfer users
    transferUsers(api_url_1, api_url_2, api_key_1, api_key_2)
