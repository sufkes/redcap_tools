#!/usr/bin/env python

import os, sys 
import argparse

import redcap

def exportUsers(api_url, api_key, format='csv'):
    """export users from REDCap project
    Parameters:
        api_url: str, API URL for REDCap project
    Returns:
        users: str, user information for REDCap project in CSV format."""

    # Load project.
    project = redcap.Project(api_url, api_key)

    # Export users.
    users = project.export_users(format=format)

    # Encode 'users' (currently unicode) as UTF-8.
    users = users.encode('utf-8')

    return users

if (__name__ == '__main__'): 
    description = """Export users from REDCap project."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("api_key", help="API key of the project from which you wish to export data")
    parser.add_argument("out_path", help="file path to write the data to")

    ## Define optional arguments.
#    parser.add_argument("-q", "--quiet", help="do not print export progress. Default: False", action="store_true")
    
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

    # Get users
    users = exportUsers(args.api_url, args.api_key, format='csv')

    # Save users string to csv file.
    with open(args.out_path, 'wb') as handle:
        handle.write(users)
