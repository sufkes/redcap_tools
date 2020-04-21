#!/usr/bin/env python

# Standard modules
import sys
import argparse
import pycurl, cStringIO
import StringIO

# My modules is current directory
from ApiSettings import ApiSettings

def importMetadata(api_url, api_key, csv_string):

    buf = cStringIO.StringIO()
    data = {
        'token': api_key,
        'content': 'metadata',
        'format': 'csv',
        'data': csv_string,
        'returnFormat': 'json'
        }
    ch = pycurl.Curl()
    ch.setopt(ch.URL, api_url)
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
    description = """Import a data dictionary CSV to a REDCap project.
Overwrites current data dictionary."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("in_path", type=str, help="file path of metadata CSV file to import")

    ## Define keyword arguments.
    # Add arguments for API URL, API key, and code name of project used to retreive these.
    parser = api_settings.addApiArgs(parser) # Adds args "-n", "--code_name", "-k", "--api_key", "-u", "--api_url" to the argument parser.
    
    # Print help message if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()

    # Parse arguments.
    args = parser.parse_args()

    # Determine the API URL and API token based on the users input and api_keys.json file.
    api_url, api_key, code_name = api_settings.getApiCredentials(api_url=args.api_url, api_key=args.api_key, code_name=args.code_name)
    
    # Read CSV file to string
    with open(args.in_path, 'rb') as handle:
        csv_string = handle.read()

    ## Import metadata
    importMetadata(api_url=api_url, api_key=api_key, csv_string=csv_string)
