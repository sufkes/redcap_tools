#!/usr/bin/env python

# Standard modules
import os, sys 
import argparse

# My modules in current directory
from ApiSettings import ApiSettings

# Other modules
import redcap # PyCap

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
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.
    
    description = """Export users from REDCap project."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("out_path", help="file path to write the data to")

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
    
    # Get users
    users = exportUsers(api_url, api_key, format='csv')

    # Save users string to csv file.
    with open(args.out_path, 'wb') as handle:
        handle.write(users)
