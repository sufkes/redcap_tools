#!/usr/bin/env python

import sys, argparse
from importRecords import importRecords

# Create argument parser.
description = """Import records to a REDCap project from a CSV file. The fields to be imported must 
already be defined in the project. The record IDs in the import file need not exist in the project."""
parser = argparse.ArgumentParser(description=description)

# Define positional arguments 
parser.add_argument("api_key", help="API key of the project to which you wish to import data")
parser.add_argument("in_path", help="file path of CSV file to be imported")

# Define positional arguments
parser.add_argument("-u", "--api_url", help="API URL. Default: 'https://redcapexternal.research.sickkids.ca/api/'", default="https://redcapexternal.research.sickkids.ca/api/")
parser.add_argument("--overwrite", help="erase values stored in the database if not specified in the input file", action="store_const", const="overwrite", default="normal") # CURRENTLY NOT SET UP.
parser.add_argument("-q", "--quick", help="Do not summarize changes to be made to destination project before importing (much quicker).", action='store_true')

# Print help message if no args input
if (len(sys.argv) == 1):
    parser.print_help()
    sys.exit()

# Parse arguments
args = parser.parse_args()

# Convert input csv file to string.
with open(args.in_path, 'rb') as data_file:
    data_string = data_file.read()
    # type(data_string) = str (with hopefully UTF-8 encoding)

# Import data.
importRecords(args.api_url, args.api_key, data_string, overwrite=args.overwrite, format='csv', quick=args.quick)
