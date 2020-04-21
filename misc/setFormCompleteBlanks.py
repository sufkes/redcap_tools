#!/usr/bin/env python

# Standard modules
import os, sys
import argparse

# Non-standard modules
import pandas
import redcap # PyCap

# My modules in current directory
from ApiSettings import ApiSettings
from exportRecords import exportRecords
from importRecords import importRecords
from exportProjectInfo import exportProjectInfo
from getEvents import getEvents
from exportFormEventMapping import exportFormEventMapping
from exportRepeatingFormsEvents import exportRepeatingFormsEvents
from exportFormsOrdered import exportFormsOrdered
from createFormRepetitionMap import createFormRepetitionMap
from parseMetadata import parseMetadata

def setFormCompleteBlanks(api_url, api_key, out_dir=None, quick_import=False, instruments=None, statuses=["0"]):
    """Find all empty forms in a project, and set their form_complete variables to blanks.
Parameters
----------
    api_url : str
        API URL for REDCap project to be modified
    api_key : str
        API token for REDCap project to be modified
"""
    ## Export all records for project
    records = exportRecords(api_url, api_key, export_form_completion=True, forms=instruments)

    # Convert records to a Pandas DataFrame
    records_df = pandas.DataFrame(records).astype(unicode)
    
    ## Find blank forms form by form
    # Get parsed metadata.
    project = redcap.Project(api_url, api_key)
    def_field = project.def_field
    project_info = exportProjectInfo(api_url, api_key)
    project_longitudinal = bool(project_info["is_longitudinal"])
    project_repeating = bool(project_info["has_repeating_instruments_or_events"])
    events = getEvents(api_url, api_key)#project, project_info, project_longitudinal)
    metadata_raw = project.export_metadata()
    form_event_mapping = exportFormEventMapping(project, project_longitudinal)
    repeating_forms_events = exportRepeatingFormsEvents(api_url, api_key, project_repeating)
    forms = exportFormsOrdered(api_url, api_key)
    form_repetition_map = createFormRepetitionMap(project_longitudinal, project_repeating, form_event_mapping, repeating_forms_events, forms)
    metadata = parseMetadata(def_field, project_info, project_longitudinal, project_repeating, events, metadata_raw, form_event_mapping, repeating_forms_events, forms, form_repetition_map)

    ## Set which fields form the primary key
    primary_key = [def_field]
    if project_longitudinal:
        primary_key.append('redcap_event_name')
    if project_repeating:
        primary_key.extend(['redcap_repeat_instrument', 'redcap_repeat_instance'])

    # If quick_import=True, still require a single import confirmation to verify that the correct REDCap project was selected (in this case, the following variable will be set to True after the first import.). If quick_import=False, all imports will be made with quiet=False.
    quiet_import = False

        
    # Loop through forms and determine if they are empty
    for form in forms:
        form_name = form['instrument_name']
        # If a set of instuments was specified, check that current instrument is in the list.
        if ((not instruments is None) and (not form_name in instruments)):
            continue
        
        form_complete_field = form_name + "_complete"

        # Generate list of fields in the form.
        fields_in_form_checkbox = []
        fields_in_form_noncheckbox = []
        for field_name, field_obj in metadata.iteritems():
            if (field_obj.form_name == form_name): # if field is in current form.
                if (field_obj.field_type == 'checkbox'):
                    fields_in_form_checkbox.append(field_name)
                else:
                    fields_in_form_noncheckbox.append(field_name)

        # For current form, find all rows in which the form is completely empty, and the form_complete field is '0'. 
        empty_form_rows = records_df.loc[((records_df[fields_in_form_checkbox].isin(['', '0']).all(axis=1)) & (records_df[fields_in_form_noncheckbox].isin(['']).all(axis=1)) & (records_df[form_complete_field].isin(statuses))), primary_key + [form_complete_field]]

        ## Either save a report of the form_complete fields which should be set to blank, or import them directly.
        if (len(empty_form_rows) > 0):
            if (not out_dir is None):
                # Save reports to files if an output directory was specified.
                file_name = form_name + '.csv'
                out_path = os.path.join(out_dir, file_name)
                empty_form_rows.to_csv(out_path, index=False, encoding='utf-8')
            else:
                ## If an output directory was not specified, overwrite the form_complete '0's directly.
                # Set the '0's to blanks
                empty_form_rows.loc[:, form_complete_field] = ''

                # Convert the import data to CSV.
                empty_form_rows_csv = empty_form_rows.to_csv(index=False, encoding='utf-8')

                # Import the data.
                importRecords(api_url, api_key, empty_form_rows_csv, quick=quick_import, quiet=quiet_import, format='csv', overwrite='overwrite', return_content='count')
                if (quick_import and (not quiet_import)):
                    quiet_import = True
                    print "The remaining import steps will not require user confirmation, since quick_import=True."
    return

    
if (__name__ == '__main__'):
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.

    # Create argument parser
    description = """Find all empty forms in a project, and set their form_complete variables to blanks"""
    epilog = '' # """Text to follow argument explantion """
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    
    # Define keyword arguments.
    # Add arguments for API URL, API key, and code name of project used to retreive these.
    parser = api_settings.addApiArgs(parser) # Adds args "-n", "--code_name", "-k", "--api_key", "-u", "--api_url" to the argument parser.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", "--out_dir", help="directory to save form_complete fields that would be set to blanks by this function. If an output directory is specified, the form_complete fields are not overwritten with blanks, only saved for review. If an output directory is not specified, the form_complete fields are overwritten with blanks directly.")
    group.add_argument("-q", "--quick_import", help="do not summarize the changes that will be made to the database before confirming import, and do not ask for confirmation before importing each field. The user must still confirm import of the first form_complete field to ensure that the correct project was selected.", action="store_true")
    parser.add_argument("-i", "--instruments", help="list of instruments whose form_complete fields will be modified. Default: Modify all instruments.", nargs="+", metavar="INSTRUMENT")
    parser.add_argument("-s", "--statuses", help="list of form complete statuses to set to blank if the form is otherwise empty.", nargs="+", type=str, choices=["0","1","2"], default=["0"])
    
    # Print help if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()

    # Parse arguments.
    args = parser.parse_args()

    # Determine the API URL and API token based on the users input and api_keys.json file.
    api_url, api_key, code_name = api_settings.getApiCredentials(api_url=args.api_url, api_key=args.api_key, code_name=args.code_name)
    
    # Do stuff.
    setFormCompleteBlanks(api_url, api_key, out_dir=args.out_dir, quick_import=args.quick_import, instruments=args.instruments, statuses=args.statuses)
