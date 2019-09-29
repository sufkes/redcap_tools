#!/usr/bin/env python
import sys, argparse

from exportRecords import exportRecords
from importRecords import importRecords

# Create argument parser.
description = """Export records from a REDCap project, modify the exported records, and import the 
modified data to another REDCap project."""
parser = argparse.ArgumentParser(description=description)

# Define positional arguments.
parser.add_argument("api_key_from", help="API key of the project from which you wish to export data")
parser.add_argument("api_key_to", help="API key of the project to which you wish to import data")

# Define optional arguments.
parser.add_argument("-u1", "--api_url_from", help="API URL of project from which you wish to export data. Default: 'https://redcapexternal.research.sickkids.ca/api/'", default="https://redcapexternal.research.sickkids.ca/api/")
parser.add_argument("-u2", "--api_url_to", help="API URL of project from which you wish to export data. Default: 'https://redcapexternal.research.sickkids.ca/api/'", default="https://redcapexternal.research.sickkids.ca/api/")
parser.add_argument("-r", "--records", help="list of records to export. Default: Export all records.", nargs="+", metavar=("ID_1", "ID_2"))
parser.add_argument("-e", "--events", help="list of events to export. Default: Export all events.", nargs="+", metavar=("event_1", "event_2"))
parser.add_argument("-f", "--fields", help="list of fields to export. Default: export all fields. To export checkbox fields, specify the base variable name (e.g. 'cb_var' instead of 'cb_var___1', 'cb_var___2', ...)", nargs="+", metavar=("field_1", "field_2"))
parser.add_argument("-i", "--instruments", help="list of data instruments to export. Default: export all instruments.", nargs="+", metavar=("form_1", "form_2"))
parser.add_argument("-m", "--mod_script", help="path to script which will modify the data.")

# Print help message if no args input.
if (len(sys.argv) == 1):
    parser.print_help()
    sys.exit()

# Parse arguments.
args = parser.parse_args()

# Export specified records from first project.
records = exportRecords(args.api_url_from, args.api_key_from, record_id_list=args.records, events=args.events, fields=args.fields, forms=args.instruments, format='json')

# Modify records from first project. Ensure that modified data is compatible with destination project.
if (args.mod_script != None): # if a modification script was specified.
    module_name = args.mod_script[:-3] # remove '.py' from specified script for import
    exec "from "+module_name+" import modifyRecords"
    records_to_import = modifyRecords(records)
else:
    records_to_import = records

# Import modified records to second project.
importRecords(args.api_url_to, args.api_key_to, records_to_import, format='json')
