#!/usr/bin/env python

import sys, argparse

from exportRecords import exportRecords

### Handle command-line argumnets
## Create argument parser.
description = """Export records from a REDCap project to a csv file. By default, all records, fields, 
and events are exported. Use optional arguments to export data for only certain records, fields, or 
events."""
parser = argparse.ArgumentParser(description=description)

## Define positional arguments.
parser.add_argument("api_key", help="API key of the project from which you wish to export data")
parser.add_argument("out_path", help="file path to write the data to")

## Define optional arguments.
parser.add_argument("-r", "--records", help="list of records to export. Default: Export all records.", nargs="+", metavar=("ID_1", "ID_2"))
parser.add_argument("-e", "--events", help="list of events to export. Note that an event's name may differ from the event's label. For example, and event with label 'Acute' may have name 'acute_arm_1'. Default: Export all events.", nargs="+", metavar=("event_1", "event_2"))
parser.add_argument("-f", "--fields", help="list of fields to export. Default: export all fields. To export checkbox fields, specify the base variable name (e.g. 'cb_var' instead of 'cb_var___1', 'cb_var___2', ...)", nargs="+", metavar=("field_1", "field_2"))
parser.add_argument("-i", "--instruments", help="list of data instrument names to export. Note that an instrument's name (shown in the data dictionary) may differ from an instrument's label (shown in the Online Designer). Default: export all instruments.", nargs="+", metavar=("form_1", "form_2"))
parser.add_argument("-c", "--export_form_completion", help="export the fields which store the completion state of a form for the specific forms requested, or for all forms if specific fields or forms are not requested. Default: False", action="store_true")
parser.add_argument("-q", "--quiet", help="do not print export progress. Default: False", action="store_true")
parser.add_argument("-l", "--label", help="label cells as HIDDEN or INVALID if hidden by branching logic or invalid (event, form, instance) combinations. Warning: this is still experimental.", action="store_true")
parser.add_argument("-o", "--label_overwrite", help="if the -l --label is specified, using this option will overwrite fields containing entries with labels.", action="store_true")
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

# Export records.
records = exportRecords(api_url, args.api_key, record_id_list=args.records, events=args.events, fields=args.fields, forms=args.instruments, export_form_completion=args.export_form_completion, quiet=args.quiet, format='csv', label=args.label, label_overwrite=args.label_overwrite)

# Save string to csv file. This saves in the same format as a REDCap export, except that the completion
# state of each form is excluded.
with open(args.out_path, 'wb') as handle:
    handle.write(records)
