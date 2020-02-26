#!/usr/bin/env python
# This script backs up REDCap projects.

# input a list of redcap project api keys and api urls. 
# specify an output path.

# directory structure:
# /out_path/YYYY-MM-DD/<project_id>_<project_name>/<date>_<project_id>_<project_name?>_object

# backup will consist of the following:
# project XML without records
# records in csv file
# other stuff?

# Standard modules
import os, sys, argparse
import datetime

# Non-standard modules.
#import redcap # PyCap

# My modules in current directory
from exportProjectXML import exportProjectXML
from exportProjectInfo import exportProjectInfo
from exportRecords import exportRecords

# My scripts in other directories
from Color import Color
#from misc.exportFormEventMapping import exportFormEventMapping
#from mexportRepeatingFormsEvents import exportRepeatingFormsEvents
#from exportFormsOrdered import exportFormsOrdered
#from createFormRepetitionMap import createFormRepetitionMap

def backup_project(api_url, api_key, date_dir, date_string, all=False):
    # Get project info.
    project_info = exportProjectInfo(api_url, api_key)
    if ("error" in project_info):
        print
        print "*************************************"
        print Color.red+"ERROR:"+Color.end
        print project_info["error"]
        print "Project may have failed to backup."
        print "*************************************"
        print
        return
    project_id = str(project_info["project_id"])
    project_title_nospace = project_info["project_title"].replace(" ","_")

    print "Backing up: "+Color.green+project_info["project_title"]+Color.end+" (project ID: "+Color.green+project_id+Color.end+")"

    # Create directory for project.
    project_dir_name = project_id + "_" + project_title_nospace
    project_dir = os.path.join(date_dir, project_dir_name)
    if (not os.path.isdir(project_dir)):
        os.mkdir(project_dir)

    # Define suffix to append to each file.
    file_suffix = "_" + date_string + "_" + project_dir_name

    # Backup project XML (not including records).
    project_xml = exportProjectXML(api_url, api_key)
    project_xml_path = os.path.join(project_dir, "project_xml"+file_suffix+".xml")
    with open(project_xml_path, 'w') as fh:
        fh.write(project_xml)

    # Backup project records.
    records = exportRecords(api_url, api_key, format="csv")
    records_path = os.path.join(project_dir, "records"+file_suffix+".csv")
    with open(records_path, 'w') as fh:
        fh.write(records)
    print 

    return

if (__name__ == "__main__"):
    # Create argument parser.
    description = "Back up a set of REDCap projects (Project XML, records)."
    parser = argparse.ArgumentParser(description=description)

    # Define optional arguments.
    default_in_path = "/Users/steven ufkes/Documents/stroke/backups/project_list.txt"
    default_out_dir = "/Users/steven ufkes/Documents/stroke/backups/"
    parser.add_argument("-i", "--in_path", help="path to text file specifying projects to back up. File should contain 1 space-separated (API URL, API KEY) pair per line.", type=str, default=default_in_path)
    parser.add_argument("-o", "--out_dir", help="path to output directory where backups will be saved", type=str, default=default_out_dir)
    parser.add_argument("-a", "--all", help="backup all API-exportable items. By default, only the project XML (without records), and a separate file containing all records are exported. These two items consititute the entire project, but it is possible to export, e.g., the Instrument-Event mappings by itself, which can be useful to store separately.", action="store_true") 
    parser.add_argument("-m", "--modification_notes", action='store', type=str, help='Notes about why a backup is being performed. For example, if data is about to be imported into a project, the user should not the project which will be modified and what changes will be made, back up the project, and then perform the changes. ')
    parser.add_argument("-p", "--pids", help="list of project IDs to back up. Default: Back up all projects in the list of projects.", nargs="+", metavar=("PID1", "PID2"))
    parser.add_argument("-t", "--timestamp", help="Include the time of day at which the backup was performed in the backup directory name. By default, on the date is used.", action='store_true')
    
    # Parse arguments.
    args = parser.parse_args()

    # Check that output directory exists.
    if (not os.path.isdir(args.out_dir)):
        cont = raw_input("The specified output directory does not exist. Create directory? [y]/n? ")
        if (cont.lower() in ["y", "yes"]):
            os.mkdirs(args.out_dir)
        elif (cont.lower() in ["n", "no"]):
            print "Quitting"
            sys.exit()
        else:
            print "Error: Unrecognized response. Quitting"
            sys.exit()
    
    # Check that input path exists.
    if (not os.path.exists(args.in_path)):
        print "Error: Input file does not exist. Quitting."
        sys.exit()

    # Build list of API (url, key) tuples.
    with open(args.in_path, 'r') as fh:
        try:
            api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
        except IndexError:
            print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
            sys.exit()

    # Create subdirectory for current date.
    if (not args.timestamp):
        date_string = datetime.datetime.today().strftime('%Y-%m-%d')
    else:
        date_string = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    date_dir = os.path.join(args.out_dir, date_string)
    if (not os.path.isdir(date_dir)):
        os.mkdir(date_dir)

    # MOVE THE REMAINING STUFF TO A SUBROUTINE.
    # Save a message about the reason the backup is being performed in the date_dir.
    if (args.modification_notes == None):
        args.modification_notes = str(raw_input("Please enter reason for performing backup: "))
    modification_notes_path = os.path.join(date_dir, 'README.txt')
    with open(modification_notes_path, 'w') as modification_notes_handle:
        modification_notes_handle.write(args.modification_notes)

    # Loop over projects. 
    for api_pair in api_pairs:
        api_url = api_pair[0]
        api_key = api_pair[1]

        if (not args.pids == None): # If only backing up specific projects.
            pid = str(exportProjectInfo(api_url, api_key)["project_id"])
            if (not pid in args.pids):
                continue
        
        # Backup project
        backup_project(api_url, api_key, date_dir, date_string, all=args.all)
