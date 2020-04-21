#!/usr/bin/env python
"""This is the main driver for intra-project checks. 

Usage: ./mainIntraProject.py <API URL> <API key> <out dir> <checklist 1> [checklist 2] ...

or:    ./mainIntraProject.py <arg_file>

where 'arg_file' is a text file with one argument per line."""


# Standard modules
import argparse
import os, sys
import time

# Non-standard modules
import redcap # PyCap

# My modules from current directory.
from createChecklist import createChecklist
from checkDriver import checkDriver
from saveData import saveData
from recordsFromFile import saveRecords
from isProjectCompatible import isProjectCompatible

# My modules from other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.exportProjectInfo import exportProjectInfo
from misc.getEvents import getEvents
from misc.exportFormEventMapping import exportFormEventMapping
from misc.exportRepeatingFormsEvents import exportRepeatingFormsEvents
from misc.exportFormsOrdered import exportFormsOrdered
from misc.createFormRepetitionMap import createFormRepetitionMap
from misc.parseMetadata import parseMetadata
from misc.exportRecords import exportRecords
from misc.createRecordIDMap import createRecordIDMap
from misc.getDAGs import getDAGs
from misc.createDAGRecordMap import createDAGRecordMap
from misc.Color import Color

# Parse arguments.
if (len(sys.argv) == 2): # if args are provided in file
    with open(str(sys.argv[1]), "r") as file:
        args = [sys.argv[0]]
        args.extend(file.read().splitlines())
else: # if args are entered directly in command line
    args = sys.argv

api_url = str(args[1])
api_key = str(args[2])
out_dir = str(args[3])

if (not os.path.isdir(out_dir)):
    os.mkdir(out_dir)
    print "Created directory:", out_dir

num_checklists = len(args) - 4 # How many lists of quality checks are used (usually 2 = default + user defined)
check_name_list = [] # list containing the lists of paths to quality control checks to perform (usually contains to checklists: default + user defined)
for list_index in range(4, 4 + num_checklists):
    check_name_list.append(args[list_index])

check_paths_exist = True
for check_name in check_name_list:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    check_path = os.path.join(scriptdir, check_name+".py")
    if not os.path.exists(check_path):
        check_paths_exists = False
        print "ERROR: Path does not exist:", check_path
        sys.exit()


# Load REDCap project (a PyCap object).
project = redcap.Project(api_url, api_key)


# Get the field name of the unique identifying field (e.g. "ipssid").
def_field = project.def_field


# Load high-level projct information.
project_info = exportProjectInfo(api_url, api_key)
project_longitudinal = bool(project_info["is_longitudinal"])
project_repeating = bool(project_info["has_repeating_instruments_or_events"])


# Load list of events
events = getEvents(api_url, api_key)#project, project_info, project_longitudinal)
if (not events == None):
    for event in events:
        event_id = events[event]["event_id"]
        if (not event_id == None):
            print Color.green+event+" "+event_id+Color.end
        else:
            print Color.red+event+" "+'None'+Color.end

# Load raw data dictionary.
metadata_raw = project.export_metadata()


# Load instrument-event mapping
form_event_mapping = exportFormEventMapping(project, project_longitudinal)


# Load information specifying which forms are repeating.
repeating_forms_events = exportRepeatingFormsEvents(api_url, api_key, project_repeating)


# Generate list of forms - list of dicts with two keys: 'instrument_label' and 'instrument_name'
forms = exportFormsOrdered(api_url, api_key)


# Generate a dictionary with form_names as keys; each entry is a dict specifying in which 
# events the form is non-repeating, indpendently repeating, or dependently repeating.
form_repetition_map = createFormRepetitionMap(project_longitudinal, project_repeating, form_event_mapping, repeating_forms_events, forms)


# Gather data about each variable.
metadata = parseMetadata(def_field, project_info, project_longitudinal, project_repeating, events, metadata_raw, form_event_mapping, repeating_forms_events, forms, form_repetition_map)


# Load all records.
# LOAD IPSS RECORDS FROM FILE (DEBUG MODE)
load_records_from_file = 0
save_records_to_file = 0
if load_records_from_file:
    from recordsFromFile import loadRecords
    print "loadRecords()"
    s = time.time()
    records = loadRecords(out_dir)
    e = time.time()
    print "loadRecords():"+"{:.3g}".format(e-s)+"s"
else:
    records = exportRecords(api_url, api_key)
#    records = records[:500] # select subset of records for tests.
    if save_records_to_file:
        print "saveRecords()"
        s = time.time()        
        saveRecords(out_dir, records)
        e = time.time()
        print "saveRecords():"+"{:.3g}".format(e-s)+"s"


# Check for high-level issues in project settings, metadata, records.
print "isProjectCompatible()"
s = time.time()
#print Color.red+"SKIPPING PROJECT COMPATIBILITY CHECK TO SAVE TIME FOR DEBUGGING."+Color.end
project_compatible = isProjectCompatible(metadata, records, def_field)
e = time.time()
print "isProjectCompatible(): "+"{:.3g}".format(e-s)+"s"
#if (not project_compatible):
#    sys.exit()


# Generate a dictionary with record IDs as keys and a list of row numbers corresponding to that record as values.
print "getRecordIDs()"
s= time.time()
# CHANGE NAME TO record_id_map
#record_ids = getRecordIDs(def_field, records)
record_id_map = createRecordIDMap(def_field, records)
e = time.time()
print "createRecordIDMap(): "+"{:.3g}".format(e-s)+"s"


# Generate a list of data access groups if they exist.
print "getDAGs()"
s = time.time()
dags_used, dags = getDAGs(records)
e = time.time()
print "getDAGs(): "+"{:.3g}".format(e-s)+"s"


# Generate a dictionary containing information about each dag (e.g. number of records they contain).
print "createDAGRecordMap()"
s = time.time()
dag_record_map = createDAGRecordMap(def_field, records, record_id_map, dags_used, dags)
e = time.time()
print "createDAGRecordMap(): "+"{:.3g}".format(e-s)+"s"


# Generate list of checks to perform (default & user-defined).
print "createChecklist()"
s = time.time()
checklist = createChecklist(check_name_list)
e = time.time()
print "createChecklist(): "+"{:.3g}".format(e-s)+"s"


# Perform checks on data and report issues.
print "checkDriver()"
s = time.time()
check_results = checkDriver(checklist, out_dir, def_field, forms, project_info, project_longitudinal, project_repeating, events, metadata, form_event_mapping, repeating_forms_events, form_repetition_map, records, record_id_map, dags_used, dags, dag_record_map)
e = time.time()
print "checkDriver(): "+"{:.3g}".format(e-s)+"s"


# Save data exported from REDCap and generated in this script.
print "saveData()"
s = time.time()
saveData(out_dir, project, forms, project_info, metadata, record_id_map, dags_used, dags, check_results)
e = time.time()
print "saveData(): "+"{:.3g}".format(e-s)+"s"


if (__name__ == '__main__'):
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.
    
    ## Create argument parser.
    description = """Export records from a REDCap project to a csv file. By default, all records, fields, and events are exported. Use optional arguments to export data for only certain records, fields, or 
events. User must provide either a project API key or a project code name, not both."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("out_path", help="file path to write the data to")

    ## Define keyword arguments.
    # Add arguments for API URL, API key, and code name of project used to retreive these.
    parser = api_settings.addApiArgs(parser) # Adds args "-n", "--code_name", "-k", "--api_key", "-u", "--api_url" to the argument parser.
        
    parser.add_argument("-r", "--records", help="list of records to export. Default: Export all records.", nargs="+", metavar=("ID_1", "ID_2"))
    parser.add_argument("-e", "--events", help="list of events to export. Note that an event's name may differ from the event's label. For example, and event with label 'Acute' may have name 'acute_arm_1'. Default: Export all events.", nargs="+", metavar=("event_1", "event_2"))
    parser.add_argument("-f", "--fields", help="list of fields to export. Default: export all fields. To export checkbox fields, specify the base variable name (e.g. 'cb_var' instead of 'cb_var___1', 'cb_var___2', ...)", nargs="+", metavar=("field_1", "field_2"))
    parser.add_argument("-i", "--instruments", help="list of data instrument names to export. Note that an instrument's name (shown in the data dictionary) may differ from an instrument's label (shown in the Online Designer). Default: export all instruments.", nargs="+", metavar=("form_1", "form_2"))
    parser.add_argument("-c", "--export_form_completion", help="export the fields which store the completion state of a form for the specific forms requested, or for all forms if specific fields or forms are not requested. Default: False", action="store_true")
    parser.add_argument("-q", "--quiet", help="do not print export progress. Default: False", action="store_true")
    parser.add_argument("-l", "--label", help="label cells as HIDDEN or INVALID if hidden by branching logic or invalid (event, form, instance) combinations. Warning: this is still experimental.", action="store_true")
    parser.add_argument("-o", "--label_overwrite", help="if the -l --label option is specified, using this option will overwrite fields containing entries with labels.", action="store_true")

    # Print help message if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()
    
    # Parse arguments.
    args = parser.parse_args()
    
    # Determine the API URL and API token based on the users input and api_keys.json file.
    api_url, api_key, code_name = api_settings.getApiCredentials(api_url=args.api_url, api_key=args.api_key, code_name=args.code_name)
