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
import ipss
from ipss.getIPSSIDs import getIPSSIDs

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
events = getEvents(project, project_info, project_longitudinal)
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
    record_ids_vips_enrolled = getIPSSIDs(db='vips2', inc_non_vips_enrolled=False)
    records = exportRecords(api_url, api_key, record_id_list=record_ids_vips_enrolled)
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


# Generate a non redundant list of record IDs. 
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
