#!/usr/bin/env python
"""This is the main driver for inter-project checks.

Usage: ./mainInterProject.py <API URL 1> <API URL 2> <API key 1> <API key 2> <out dir> <checklist_1> [checklist_2] ..."""


# Standard modules
import os, sys

# Non-stanard modules
import redcap # PyCap

# My modules from current directory
from createChecklist import createChecklist
from checkDriverInterProject import checkDriverInterProject
from saveData import saveData
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
#sys.path.append(os.path.join(os.path.join(sufkes_git_repo_dir, "misc"))
#from Color import Color
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_special"))
from getIPSSIDs import getIPSSIDs

if (len(sys.argv) == 2): # if args are provided from file
    with open(str(sys.argv[1]), "r") as file:
        args = [sys.argv[0]] 
        args.extend(file.read().splitlines())
else: # if args are entered directly in command line
    args = sys.argv

# Parse arguments.
api_url_list = []
api_url_list.append(str(args[1]))
api_url_list.append(str(args[2]))
api_key_list = []
api_key_list.append(str(args[3]))
api_key_list.append(str(args[4]))
out_dir = str(args[5])

if (not os.path.isdir(out_dir)):
    os.mkdir(out_dir)
    print "Created directory:", out_dir

num_checklists = len(args) - 6
check_name_list = []
for list_index in range(6, 6 + num_checklists):
    check_name_list.append(args[list_index])

check_paths_exist = True
for check_name in check_name_list:
    check_path = check_name+".py"
    if not os.path.exists(check_path):
        check_paths_exists = False
        print "ERROR: Path does not exist:", check_path
        sys.exit()

num_projects = 2

# FOR SOME REASON, I INITIALIZED THESE LISTS INSTEAD OF APPENDNG.
project_list = [None]*num_projects
def_field_list = [None]*num_projects
project_info_list = [None]*num_projects
project_longitudinal_list = [None]*num_projects
project_repeating_list = [None]*num_projects
events_list = [None]*num_projects
metadata_raw_list = [None]*num_projects
form_event_mapping_list = [None]*num_projects
repeating_forms_events_list = [None]*num_projects
forms_list = [None]*num_projects
form_repetition_map_list = [None]*num_projects
metadata_list = [None]*num_projects
records_list = [None]*num_projects
project_compatible_list = [None]*num_projects
record_id_map_list = [None]*num_projects
dags_used_list = [None]*num_projects
dags_list = [None]*num_projects
dag_record_map_list = [None]*num_projects

#for project_index in range(len(api_key_list)): # version without reversing order 
for project_index in range(len(api_key_list))[::-1]: # get data from second project first, to ensure that first project only includes records that also appear in the second project.
    # Load REDCap project (a PyCap object).
    project_list[project_index] = redcap.Project(api_url_list[project_index], api_key_list[project_index])


    # Get the field name of the unique identifying field (e.g. "ipssid").
    
    def_field_list[project_index] = project_list[project_index].def_field


    # Load high-level projct information.
    project_info_list[project_index] = exportProjectInfo(api_url_list[project_index], api_key_list[project_index])
    project_longitudinal_list[project_index] = bool(project_info_list[project_index]["is_longitudinal"])
    project_repeating_list[project_index] = bool(project_info_list[project_index]["has_repeating_instruments_or_events"])

        
    # Load list of events
    events_list[project_index] = getEvents(project_list[project_index], project_info_list[project_index], project_longitudinal_list[project_index])
    

    # Load raw data dictionary.
    metadata_list[project_index] = project_list[project_index].export_metadata()
    
    
    # Load instrument-event mapping
    form_event_mapping_list[project_index] = exportFormEventMapping(project_list[project_index], project_longitudinal_list[project_index])
    
    
    # Load information specifying which forms are repeating.
    repeating_forms_events_list[project_index] = exportRepeatingFormsEvents(api_url_list[project_index], api_key_list[project_index], project_repeating_list[project_index])
    
    
    # Generate list of forms - list of dicts with two keys: 'instrument_label' and 'instrument_name'
    forms_list[project_index] = exportFormsOrdered(api_url_list[project_index], api_key_list[project_index])
    

    # Generate a dictionary with form_names as keys; each entry is a dict specifying in which 
    # events the form is non-repeating, indpendently repeating, or dependently repeating.
    form_repetition_map_list[project_index] = createFormRepetitionMap(project_longitudinal_list[project_index], project_repeating_list[project_index], form_event_mapping_list[project_index], repeating_forms_events_list[project_index], forms_list[project_index])
    
    
    # Gather data about each variable.
    metadata_list[project_index] = parseMetadata(def_field_list[project_index], project_info_list[project_index], project_longitudinal_list[project_index], project_repeating_list[project_index], events_list[project_index], metadata_list[project_index], form_event_mapping_list[project_index], repeating_forms_events_list[project_index], forms_list[project_index], form_repetition_map_list[project_index])
    
    
    # Load all records.
#    if (project_index == 0): # USED BEFORE REVERSING ORDER OF PROJECT DATA RETRIEVAL
    if (project_index == 1):# USED AFTER REVERSING ORDER OF PROJECT DATA RETRIEVAL
        record_ids_vips_enrolled = getIPSSIDs(db='vips2', inc_non_vips_enrolled=False)
        records_list[project_index] = exportRecords(api_url_list[project_index], api_key_list[project_index], record_id_list=record_ids_vips_enrolled)
    else: 
        # Only pull record IDs from second project that exist in first project.
#        records_list[project_index] = exportRecords(api_url_list[project_index], api_key_list[project_index], record_id_list=[record_id for record_id in record_id_map_list[0]]) # USED BEFORE REVERSING ORDER OF PROJECT DATA RETRIEVAL
        # Only pull record IDs from first project that exist in second project.
        records_list[project_index] = exportRecords(api_url_list[project_index], api_key_list[project_index], record_id_list=[record_id for record_id in record_id_map_list[1]]) # USED AFTER REVERSING ORDER OF PROJECT DATA RETRIEVAL
    
    # Check for high-level issues in project settings, metadata, records.
    project_compatible_list[project_index] = isProjectCompatible(metadata_list[project_index], records_list[project_index], def_field_list[project_index])
    if (not project_compatible_list[project_index]):
        sys.exit()
    
    
    # Generate a non redundant list of record IDs. 
    record_id_map_list[project_index] = createRecordIDMap(def_field_list[project_index], records_list[project_index])
    
    
    # Generate a list of data access groups if they exist.
    dags_used_list[project_index], dags_list[project_index] = getDAGs(records_list[project_index])
    
    
    # Generate a dictionary containing information about each dag (e.g. number of records they contain).
    dag_record_map_list[project_index] = createDAGRecordMap(def_field_list[project_index], records_list[project_index], record_id_map_list[project_index], dags_used_list[project_index], dags_list[project_index])

# Check for records that only appear in the first project.
for record_id in record_id_map_list[0]:
    if (not record_id in record_id_map_list[1]):
        print "Record: "+record_id+" found in first project but not in second project. This will probably cause errors."

# Generate list of checks to perform (defualt & user-defined). 
checklist = createChecklist(check_name_list)

# Perform checks on data and report issues.
check_results = checkDriverInterProject(checklist, out_dir, def_field_list, forms_list, project_info_list, project_longitudinal_list, project_repeating_list, events_list, metadata_list, form_event_mapping_list, repeating_forms_events_list, form_repetition_map_list, records_list, record_id_map_list, dags_used_list, dags_list, dag_record_map_list)
