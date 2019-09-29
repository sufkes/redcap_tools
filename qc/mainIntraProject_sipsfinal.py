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
from checkDriver_sipsfinal import checkDriver
from saveData import saveData
from recordsFromFile import saveRecords
from isProjectCompatible import isProjectCompatible

# My modules from other directories
sufkes_git_repo_dir = "/Users/steven ufkes/scripts" # change this to the path to which the sufkes Git repository was cloned.
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_misc"))
from exportProjectInfo import exportProjectInfo
from getEvents import getEvents
from exportFormEventMapping import exportFormEventMapping
from exportRepeatingFormsEvents import exportRepeatingFormsEvents
from exportFormsOrdered import exportFormsOrdered
from createFormRepetitionMap import createFormRepetitionMap
from parseMetadata import parseMetadata
from exportRecords import exportRecords
from createRecordIDMap import createRecordIDMap
from getDAGs import getDAGs
from createDAGRecordMap import createDAGRecordMap
sys.path.append(os.path.join(sufkes_git_repo_dir, "misc"))
from Color import Color
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_special"))
from getIPSSIDs import getIPSSIDs

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
    check_path = check_name+".py"
    if not os.path.exists(check_path):
        check_paths_exists = False
        print "ERROR: Path does not exist:", check_path
        sys.exit()


# Do checks for SIPS II cohort I and cohort II.
for cohort_name in ['I','II']:
    
    
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
    

    if (cohort_name == 'I'):
        record_id_list = getIPSSIDs(inc_non_sips2_cohort1=False)
    elif (cohort_name == 'II'):
        record_id_list = getIPSSIDs(inc_non_sips2_cohort2=False)

    # Load all records.
    records = exportRecords(api_url, api_key, record_id_list=record_id_list)

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
    if (cohort_name == 'I'):
        print "createChecklist()"
        s = time.time()
        checklist_full = createChecklist(check_name_list)
        e = time.time()
        print "createChecklist(): "+"{:.3g}".format(e-s)+"s"
        checklist = checklist_full[:1] # only do the first check in the checklist (the cohort I check)
    elif (cohort_name == 'II'):
        checklist = checklist_full[1:] # only do the second check in the checklist (the cohort II check)

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
