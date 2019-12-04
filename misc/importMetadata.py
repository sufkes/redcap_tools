#!/usr/bin/env python

import sys, argparse

import pycurl, cStringIO
import StringIO

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
    ## Create argument parser.
    description = """Import a data dictionary CSV to a REDCap project.
Overwrites current data dictionary."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("api_key", help="API key of the project to import to")
    parser.add_argument("in_path", type=str, help="file path of metadata CSV file to import")

    ## Define keyword arguments.
    # API URL argument (API URL determines the REDCap instance from which data will be exported. E.g. External (default), internal, Staff Surveys, or a specified URL.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--api_url", help="API URL. Default: 'https://redcapexternal.research.sickkids.ca/api/'", default="https://redcapexternal.research.sickkids.ca/api/")
    group.add_argument("--int", help="set api_url to the SickKids internal REDCap API URL.", action='store_true')
    group.add_argument("--stf", help="set api_url to the SickKids Staff Surveys (AKA clinical) REDCap API URL.", action='store_true')

    # Print help message if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()

    # Parse arguments.
    args = parser.parse_args()

    # Set the API URL which determines the REDCap instance from which data will be exported.
    if args.int:
        api_url = 'https://redcapinternal.research.sickkids.ca/api/'
    elif args.stf:
        api_url = 'https://staffsurveys.sickkids.ca/api/'
    else:
        api_url = args.api_url

    # Read CSV file to string
    with open(args.in_path, 'rb') as handle:
        csv_string = handle.read()

    ## Import metadata
    importMetadata(api_url=args.api_url, api_key=args.api_key, csv_string=csv_string)
