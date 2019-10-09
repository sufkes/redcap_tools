#!/usr/bin/env python

import os, sys
import argparse

if (__name__ == '__main__'):
    # Create argument parser
    description = """Description of function"""
    epilog = '' # """Text to follow argument explantion """
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    
    # Define positional arguments.
#    parser.add_argument("in_path", help="path to DICOM file to be anonymized, or directory containing DICOM files.")
    
    # Define optional arguments.
#    parser.add_argument("-n", "--name", help="Subject ID to set PatientName tags to", type=str)
#    parser.add_argument("-b", "--backup", help="add an option for backup. Do not back up by default.")
#    parser.add_argument("-l", "--level", type=int, default=2, choices=[1,2,3], help="Set degree of anonymization (1: directly identifying information such as patient name, birth date, address, phone number. 2 (default): indirectly identifying information such as weight, age, physicians etc. 3: information about institution which performed scan, such as address, department etc.)")
#    parser.add_argument('-m', "--modify_pid", help="Change PatientID to specified Subject ID. Default: False", action="store_true")
#    parser.add_argument('-p', '--print-only', help='Print PHI-containing tags. Do not anonymize.', action='store_true')
#    parser.add_argument('-r', '--recursive', action='store_true', help='if in_path is a directory, find and anononymize all files in that directory.')
#    parser.add_argument("-r", "--records", help="list of records to export. Default: Export all records.", nargs="+", metavar=("ID_1", "ID_2"))

    # Print help if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()

    # Parse arguments.
    args = parser.parse_args()

    # Do stuff.
