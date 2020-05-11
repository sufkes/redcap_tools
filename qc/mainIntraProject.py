#!/usr/bin/env python
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
from readConfig import readConfig

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
from misc.ApiSettings import ApiSettings
import ipss
from ipss.getIPSSIDs import getIPSSIDs

from pprint import pprint

def mainIntraProject(config_path):
    config = readConfig(config_path)
    print "Performing checks with configuration:"
    pprint( config )
    print
    
    #### Read user's settings.yml file, which will be used to get API tokens and URLs.
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find file containing API keys and URLs.

    # Determine the API URL and API token based on the users input and api_keys.yml file.
    code_name = config["code_name"]
    api_url, api_key, code_name = api_settings.getApiCredentials(code_name=code_name)

    # Create output directory if it does not exist.
    out_dir = config["out_dir"]
    if (not os.path.isdir(out_dir)):
        os.mkdir(out_dir)
        print "Created directory:", out_dir

    # Define a list containing the lists of Check objects (defined in Check.py).
    check_name_list = config["checks"]

    check_paths_exist = True
    for check_name in check_name_list:
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        check_path = os.path.join(scriptdir, check_name+".py")
        if not os.path.exists(check_path):
            raise Exception("Path does not exist:", check_path)


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
        print "Review the event_ids below. These are required for generating links to problematic data in reports. If these are incorrect, or unset, you can set them in the event_ids.yml file specified in your settings.yml file. You can find the event_id associated with an event by accessing data from that event online, and looking at the value of 'event_id' in the address bar."
        for event in events:
            event_id = events[event]["event_id"]
            if (not event_id == None):
                print Color.green+event+" "+event_id+Color.end
            else:
                print Color.red+event+" "+'None'+Color.end
    print
                
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


    ## Load all records.
    if config["use_getIPSSIDs"]:
        getIPSSIDs_args = config["getIPSSIDs_args"]
        record_id_list = getIPSSIDs(**getIPSSIDs_args)
    elif config["use_custom_record_id_list"]:
        record_id_list = config["record_id_list"]
    else:
        record_id_list = None
    records = exportRecords(api_url, api_key, record_id_list)


    # Check for high-level issues in project settings, metadata, records.
    # 2020-05-11 - This script appears to check for bugged output of exportRecords.py, which has now been handled in exportRecords.py.
#    project_compatible = isProjectCompatible(metadata, records, def_field)
#    if (not project_compatible):
#        raise Exception("Error found in records or metadata. Review output above.")


    # Generate a dictionary with record IDs as keys and a list of row numbers corresponding to that record as values.
    record_id_map = createRecordIDMap(def_field, records)

    
    # Generate a list of data access groups if they exist.
    dags_used, dags = getDAGs(records)
    
    
    # Generate a dictionary containing information about each dag (e.g. number of records they contain).
    dag_record_map = createDAGRecordMap(def_field, records, record_id_map, dags_used, dags)
    
    
    # Generate list of checks to perform (default & user-defined).
    checklist = createChecklist(check_name_list)
    
    
    # Perform checks on data and report issues.
    check_results = checkDriver(checklist, out_dir, def_field, forms, project_info, project_longitudinal, project_repeating, events, metadata, form_event_mapping, repeating_forms_events, form_repetition_map, records, record_id_map, dags_used, dags, dag_record_map)
    
    
#    # Save data exported from REDCap and generated in this script. The check results are saved by checkDriver() above.
#    saveData(out_dir, project, forms, project_info, metadata, record_id_map, dags_used, dags, check_results)
    return

if (__name__ == '__main__'):    
    ## Create argument parser.
    description = """Perform data quality checks within a single REDCap project."""
    parser = argparse.ArgumentParser(description=description)

    # Add positional arguments.
    parser.add_argument("config_path", help="path to YAML configuration file.")
    
    # Parse arguments.
    args = parser.parse_args()
    
    # Run the script
    mainIntraProject(args.config_path)
