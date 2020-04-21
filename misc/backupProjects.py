#!/usr/bin/env python

# Standard modules
import os, sys, argparse
import json
import datetime
import warnings
from collections import OrderedDict

# My modules in current directory
from exportProjectXML import exportProjectXML
from exportProjectInfo import exportProjectInfo
from exportRecords import exportRecords
from exportFiles import exportFiles
from Color import Color
from ApiSettings import ApiSettings

warnings.warn("This script does not back up files uploaded to the File Repository.")

def backupProject(api_url, api_key, date_dir, date_string, skip_files=False):
    """Create a backup of a REDCap project, including the """
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

    # Backup files stored in File Upload fields. This does not include files stored in the File Repository.
    if (not skip_files):
        project_files_dir = os.path.join(project_dir, 'files_in_file_upload_fields')
        exportFiles(api_url, api_key, project_files_dir, flat=False)
    print 

    return

def backupProjects(api_key_path, out_dir, code_name_list=None, modification_notes=None, timestamp=False, skip_files=False):
    # Check that output directory exists.
    if (not os.path.isdir(out_dir)):
        while True:
            cont = raw_input("Output directory '"+out_dir+"' does not exist. Create it? [y]/n? ")
            if (cont.lower() in ['', "y", "yes"]):
                os.makedirs(out_dir)
                break
            elif (cont.lower() in ["n", "no"]):
                print "Quitting"
                sys.exit()
            else:
                print "Unrecognized response. Please try again."
                pass
    
    # Check that the json file containing the project API URLs and keys exists
    if (not os.path.exists(api_key_path)):
        raise ValueError("Input API key file '"+api_key_path+"' does not exist.")

    # Create OrderedDict of projects to backup
    with open(api_key_path, 'r') as handle:
        projects_to_back_up = json.load(handle, object_pairs_hook=OrderedDict)

    ## If a specific set of project code names was given, check that their keys exist, and remove all other projects from the OrderedDict.
    if (not code_name_list is None):
        # Check that each code_name appears in the json.
        for code_name in code_name_list:
            if (not code_name in projects_to_back_up.keys()):
                raise ValueError("Requested project code name '"+code_name+"' not found in '"+api_key_path+"'")
        # Remove code names which were not requested.
        projects_to_back_up = OrderedDict([(code_name, projects_to_back_up[code_name]) for code_name in code_name_list])

    # Create subdirectory for current date.
    if (not timestamp):
        date_string = datetime.datetime.today().strftime('%Y-%m-%d')
    else:
        date_string = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    date_dir = os.path.join(out_dir, date_string)
    if (not os.path.isdir(date_dir)):
        os.mkdir(date_dir)

    # Save a message about the reason the backup is being performed in the date_dir.
    modification_notes_path = os.path.join(date_dir, 'README.txt')
    if (modification_notes is None):
        modification_notes = str(raw_input("Please enter reason for performing backup. This entry will be written to '"+modification_notes_path+"' for future reference. (press RETURN to skip): "))
    if (modification_notes != ''):
        with open(modification_notes_path, 'wb') as handle:
            handle.write(modification_notes)

    # Loop over projects.
    for code_name, api_info in projects_to_back_up.iteritems():
        api_url = api_info['url']
        api_key = api_info['key']

        pid = str(exportProjectInfo(api_url, api_key)["project_id"])
        
        # Backup project
        backupProject(api_url, api_key, date_dir, date_string, skip_files=args.skip_files)
        
    return

if (__name__ == "__main__"):
    # Create instance of ApiSettings class, containing default output directory, and default path to api_keys.json file.
    api_settings = ApiSettings()
        
    # Create argument parser.
    description = "Back up a set of REDCap projects (project XML, records, and files uploaded to 'file' fields)."
    parser = argparse.ArgumentParser(description=description)

    # Define optional arguments.
    parser.add_argument("-a", "--api_key_path", type=str, help="path to json file containing API URLs and keys of projects to be backed up. Default: '"+api_settings.settings['api_key_path']+"'", default=api_settings.settings['api_key_path'])
    parser.add_argument("-o", "--out_dir", help="path to output directory where backups will be saved. Default: '"+api_settings.settings['default_backups_dir']+"'", type=str, default=api_settings.settings['default_backups_dir'])
    parser.add_argument("-n", "--code_name_list", help="list of code names of projects to back up. All code names provided must be present in the api_keys.json file.", nargs="+", metavar=("code_name_1","code_name_2"))
    parser.add_argument("-m", "--modification_notes", action='store', type=str, help='Notes about why a backup is being performed. For example, if a project is about to be modified, the user should note the project to be modified and what changes will be made, back up the project, and then perform the changes.')
    parser.add_argument("-t", "--timestamp", help="include the time of day at which the backup was performed in the backup directory name. By default, only the date is used.", action='store_true')
    parser.add_argument("-s", "--skip_files", help="do not back up files stored in File Upload fields. Note that the File Repository is not backed up regardless of this option", action='store_true')   
    
    # Parse arguments.
    args = parser.parse_args()

    # Back up a list of REDCap projects
    backupProjects(args.api_key_path, args.out_dir, code_name_list=args.code_name_list, modification_notes=args.modification_notes, timestamp=args.timestamp, skip_files=args.skip_files)
