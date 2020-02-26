#!/usr/bin/env python

# Standard modules
import os, sys, argparse
import csv
import xlsxwriter
from copy import deepcopy
from more_itertools import unique_everseen
from StringIO import StringIO
from collections import OrderedDict

# Non-standard modules
import redcap
import pandas

# My scripts in current directory
from getIPSSIDs import getIPSSIDs

# My scripts in other directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.Color import Color
from misc.Timer import Timer
from misc.exportRecords import exportRecords
from misc.exportProjectInfo import exportProjectInfo
from misc.getEvents import getEvents
from misc.exportFormEventMapping import exportFormEventMapping
from misc.exportRepeatingFormsEvents import exportRepeatingFormsEvents
from misc.exportFormsOrdered import exportFormsOrdered
from misc.createFormRepetitionMap import createFormRepetitionMap
from misc.parseMetadata import parseMetadata
from misc.getRecordIDList import getRecordIDList

# Time the whole script.
t_script = Timer('Generate data package')

# Create argument parser.
description = """Generate data package for SIPS II EEG V6"""

# Create argument parser.
parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

# Define optional arguments.
parser.add_argument('-d', '--debug', action='store_true', help='Skip important processing steps for debugging purposes.')

# Parse arguments.
args = parser.parse_args()

# Set directory to save report to.
dir_data_packages = "/Users/steven ufkes/Documents/stroke/data_packages" # directory containing IPSS data
api_url_key_list_path = os.path.join(dir_data_packages, "api_url_key_list_sips_eeg.txt") # list of api keys, urls 
dir_report = os.path.join(dir_data_packages, '2020-01_SIPS_II_EEG')
with open(api_url_key_list_path, 'r') as fh:
    try:
        api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
    except IndexError:
        print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
        sys.exit()
url_eeg = api_pairs[0][0]
key_eeg = api_pairs[0][1]

def convertFieldNames(api_url, api_key, def_field, field_list):
    """When exporting fields, REDCap API requires that the field name be entered as defined online. For checkbox fields, e.g. 'cb',  each option is mapped to a separate field in the exported data
    (e.g. 'cb___1', 'cb___2', etc.). This function converts a list of fields as specified in an API export call to a list of fields as they are returned in the exported data (and as they are subsequently 
    defined in the metadata object by parseMetadata.py"""
    if (field_list == None):
        new_field_list = None
    else:
        sample_id = exportRecords(api_url, api_key, fields=[def_field], quiet=True)[0][def_field] # Record ID for first record in database.
        sample_row = exportRecords(api_url, api_key, fields=field_list, record_id_list=[sample_id], quiet=True)[0]
        new_field_list = [key for key in sample_row if (not key in [def_field, 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group'])]
    return new_field_list

def getEmptyRows(df, metadata, def_field, col_list=None, form_list=None, ids=None):
    """
    Return rows in a REDCap records dataframe that contain no data within a specified list of fields. A field is considered empty if its value is '' for noncheckbox fields and '0' for checkbox fields.

    df: DataFrame to query
    col_list: list of field_names which should be checked for data. Default: all field names in project. def_field will automatically be removed if included
    metadata: metadata for REDCap project
    def_field: the ID field for the REDCap project.
    """

    t_getEmptyRows = Timer('getEmptyRows('+str(form_list)+')')
    if (col_list == None) and (form_list == None):
        col_list = [field_name for field_name in metadata] # check all fields, other than ID field, for completion by default.
    elif (form_list != None):
        if (col_list == None):
            col_list = set()
        for field_name, field_obj in metadata.iteritems():
            if (field_obj.form_name in form_list):
                col_list.add(field_name)

    non_id_fields_checkbox = set()
    non_id_fields_noncheckbox = set()
    for field_name in col_list:
        if (not field_name in df.columns):
            continue
        field_obj = metadata[field_name]
        if (field_obj.field_type == 'checkbox'):
            non_id_fields_checkbox.add(field_name)
        else:
            non_id_fields_noncheckbox.add(field_name)

    # Remove ID fields from selection:
    if (def_field in non_id_fields_noncheckbox): 
        non_id_fields_noncheckbox.remove(def_field) # filled in for every row; does not indicate presence of data.

    ## Remove empty rows.
    # Partition query into a number of sub-queries. 
    qry_list = ['(({} == "0") or ({} == ""))'.format(field_name, field_name) for field_name in non_id_fields_checkbox] # Checkboxes could be blank after new fields added in merge step.
    qry_list.extend(['({} == "")'.format(field_name) for field_name in non_id_fields_noncheckbox])

    partition_size = 10
    qry_empty_partitioned = []
    partition_complete = False
    ii = 0
    while (not partition_complete):
        start = ii*partition_size
        stop = (ii+1)*partition_size
        sub_query = ' and '.join(qry_list[start:stop])
        qry_empty_partitioned.append(sub_query)
        if (stop >= len(qry_list)):
            partition_complete = True
        ii += 1
    
    empty_selection = df
    for sub_qry in qry_empty_partitioned:
        empty_selection = empty_selection.query(sub_qry)

    # If a record ID list was specified, restrict selection to the list of IDs.
    if (ids != None):
        empty_selection = empty_selection.loc[empty_selection[def_field].isin(ids),:]

    # Restrict selection to the columns which were checked and are empty (do not include ID column).
    fields_in_selection = [field_name for field_name in metadata if (field_name in col_list) and (field_name in df.columns)]
    empty_selection = empty_selection[fields_in_selection]

    t_getEmptyRows.stop()
    return empty_selection
    
def makeSheet(api_url, api_key, record_id_list, project, project_info, project_longitudinal, project_repeating, events, form_event_mapping, repeating_forms_events, forms, form_repetition_map, metadata, forms_to_add=None, fields_to_add=None, events_to_add=None, remove_repeating_info=True):
    """Returns a Pandas dataframe containing specified data exported from REDCap.
    Removes 'form_complete' variables.
    
    Use events_to_add=None to include all events; events_to_add=[] to exclude all events (function 
    will return None in this case)."""

    ## Fetch project title and ID
    project_title = project_info['project_title']
    project_id = project_info['project_id']
    t_makeSheet = Timer('makeSheet() for '+project_title)
    
    ## Return if no data requested.
    if (events_to_add == set()) or ((fields_to_add == set()) and (forms_to_add == set())): # If no events or no fields from this project are requested for the data package.
        print Color.red+"ERROR: Nothing to add from this project for this datasheet."+Color.end
        t_makeSheet.stop()
        return pandas.DataFrame()

    ## Export data
    t_export = Timer('Export data to DataFrame for '+project_title)
    csv_string = exportRecords(api_url, api_key, record_id_list, forms=forms_to_add, fields=fields_to_add, events=events_to_add, quiet=False, format='csv') # type(export result) = unicode. Convert to type(str) encoded in utf-8. Modified exportRecords such that output is type(str) encoded in utf-8.
    csv_file = StringIO(csv_string)
    df = pandas.read_csv(csv_file, dtype=unicode, encoding='utf-8').fillna('')
    t_export.stop()

    t_remove_completion = Timer('Remove form-completion fields for '+project_title)

    ## Determine which columns to include
    columns = df.columns
    
    # Get names of 'form_complete' variables.
    completion_field_list = []
    for form_name in [form_info['instrument_name'] for form_info in forms]: # include all forms, even those not requested.
        completion_field = form_name+'_complete'
        if (not completion_field in columns): # verify that the completion field name is correct.
#            print Color.red+'ERROR: Supposed completion variable '+str(completion_field)+' is not a real variable.'+Color.end # Seems to be working properly
            pass
        else:
            completion_field_list.append(completion_field)
    exclude_columns = completion_field_list

    include_columns = [column for column in columns if (not column in exclude_columns)]
    t_remove_completion.stop()

    # Exclude rows containing no data (SHOULDN'T BE NECESSARY FOR IPSS IF inc_placeholders=False in getIPSSIDs.py)
    t_exclude_rows = Timer('Remove empty rows for '+project_title)
    if args.debug:
        print Color.red+'WARNING: SKIPPING EMPTY ROW CHECK.'+Color.end
        empty_indices = pandas.DataFrame()
    else:
        empty_indices = getEmptyRows(df, metadata, project.def_field).index # Do now for the entire dataset exported. Do again later after dividing data into pieces.

    # Remove the empty rows and excluded columns
    df = df.loc[~df.index.isin(empty_indices), include_columns]
    t_exclude_rows.stop()

    t_makeSheet.stop()
    return df

def change_dtype(value):
    """Use to convert cells back to numbers if possible. Apply to columns using df[column].apply(change_dtype)"""
    try:
        new_value = int(value)
    except ValueError:
        try:
            new_value = float(value)
        except ValueError:
            new_value = value
    return new_value

def addSheet(writer, df, sheet_name):
    """Add worksheet to workbook"""

    t_addSheet = Timer('addSheet()')
    # Define name for worksheet
    if (len(sheet_name) > 31): # Truncate worksheet title. xlsx files appear to have a character limit of 31 for worksheet titles.
#        print "WARNING: Sheet name too long; truncating to 31 characters."
        sheet_name = sheet_name[:31]

    # I JUST MOVED THIS HERE; MAKE SURE IT WON'T CAUSE ANY PROBLEMS.
    # Convert from unicode to int or float where possible.
    if (not args.debug):
        t_change_dtype = Timer('Converting dtypes')
        for column in df.columns:
#            if (not column in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_data_access_group']): # CONVERT INSTANCE NUMBER AND IPSSID -- WHY NOT?
            if (not column in ['redcap_event_name', 'redcap_repeat_instrument', 'redcap_data_access_group']): # CONVERT INSTANCE NUMBER AND IPSSID -- WHY NOT?
                df.loc[:, column] = df.loc[:, column].apply(change_dtype)
        t_change_dtype.stop()
    else:
        print Color.red+'WARNING: Skipping dtype conversion for debug.'

    # Write Pandas dataframe to xlsx worksheet
    df.to_excel(writer, sheet_name=sheet_name, encoding='utf-8', index=False)

    # Set column widths to roughly the length of the column header.
    worksheet = writer.sheets[sheet_name]  # pull worksheet object
    for idx, col in enumerate(df):  # loop through all columns
        max_len = len(col)
        worksheet.set_column(idx, idx, max_len)  # set column width
    t_addSheet.stop()
    return

## Get project data for each project.
#project_psom2 = redcap.Project(url_psom2, key_psom2)
#project_info_psom2 = exportProjectInfo(url_psom2, key_psom2)
#project_longitudinal_psom2 = bool(project_info_psom2["is_longitudinal"])
#project_repeating_psom2 = bool(project_info_psom2["has_repeating_instruments_or_events"])
#events_psom2 = getEvents(project_psom2, project_info_psom2, project_longitudinal_psom2)
#metadata_raw_psom2 = project_psom2.export_metadata()
#form_event_mapping_psom2 = exportFormEventMapping(project_psom2, project_longitudinal_psom2)
#repeating_forms_events_psom2 = exportRepeatingFormsEvents(url_psom2, key_psom2, project_repeating_psom2)
#forms_psom2 = exportFormsOrdered(url_psom2, key_psom2)
#form_repetition_map_psom2 = createFormRepetitionMap(project_longitudinal_psom2, project_repeating_psom2, form_event_mapping_psom2, repeating_forms_events_psom2, forms_psom2)
#metadata_psom2 = parseMetadata(project_psom2.def_field, project_info_psom2, project_longitudinal_psom2, project_repeating_psom2, events_psom2, metadata_raw_psom2, form_event_mapping_psom2, repeating_forms_events_psom2, forms_psom2, form_repetition_map_psom2, write_branching_logic_function=False)

#### Export data for each project. Only obtain list of record IDs and forms to export; process projects further in makeSheet()

if (args.package_name in ['sips', 'sipsf']):
    t_decode_med = Timer('Changing medication fields to common names.')
    for field_name in ['ac_1', 'anticonvulsant_2', 'anticonvulsant_3', 'anticonvulsant_4', 'anticonvulsant_5', 'anticonvulsant_6', 'anticonvulsant_7', 'anticonvulsant_8', 'anticonvulsant_9', 'anticonvulsant_10', 'name_of_medication', 'name_of_medication_2', 'name_of_medication_3', 'name_of_medication_4', 'name_of_medication_5', 'name_of_medication_6']:
#        field_obj = metadata_sips2[field_name]
        choices_dictionary = metadata_sips2[field_name].choices_dictionary
        choices_dictionary[''] = '' # add option for no answer.
        def decodeMedication(s, choices_dictionary):
            return choices_dictionary[s]
        project_df_sips2.loc[:, field_name] = project_df_sips2.loc[:, field_name].apply(decodeMedication, args=(choices_dictionary,))
    t_decode_med.stop()

# If record has radiographic features data in IPSS, remove this data from the Archive fields.
#def modifyRadioData(project_df_arch, project_df_ipss, metadata_arch, metadata_ipss, project_arch, project_ipss, except_ids=None):
#    """Don't modify IDs in except_ids"""
#    t_radio = Timer('Modify radiographic data')
#    radio_fields_arch = set()
#    radio_fields_ipss = set()
#    for field_name, field_obj in metadata_arch.iteritems():
#        if (field_obj.form_name == 'radiographic_stroke_features'):
#            radio_fields_arch.add(field_name)
#    for field_name, field_obj in metadata_ipss.iteritems():
#        if (field_obj.form_name == 'radiographic_features_at_presentation'):
#            radio_fields_ipss.add(field_name)
#    
#    record_ids_with_ipss_radio_data = set()
#    for row_index in project_df_ipss.index:
#        id = project_df_ipss.loc[row_index, project_ipss.def_field]
#        data_in_row = False
#        if id in record_ids_with_ipss_radio_data: # if ID was already found
#            continue
#        for field in radio_fields_ipss:
#            if ('___' in field):
#                if (project_df_ipss.loc[row_index, field] == '1'):
#                    data_in_row = True
#            elif (project_df_ipss.loc[row_index, field] != ''):
#                data_in_row = True
#            if data_in_row:
#                record_ids_with_ipss_radio_data.add(id)
#                break
#
#    # Remove excepted IDs from list of IDs to be modified.
#    ids_to_mod = [id for id in record_ids_with_ipss_radio_data if (not id in except_ids)]
#    
#    project_df_arch.loc[project_df_arch[project_arch.def_field].isin(ids_to_mod), radio_fields_arch] = 'NA' #'NA (refer to fields in IPSS form Radiographic Features at Presentation)'
#    t_radio.stop()
#    return project_df_arch, record_ids_with_ipss_radio_data
#
#project_df_arch, record_ids_with_ipss_radio_data = modifyRadioData(project_df_arch, project_df_ipss, metadata_arch, metadata_ipss, project_arch, project_ipss, except_ids=ids_custom_mod_arch_only+ids_custom_mod_arch_radio_only)


## If record has Treatment data in IPSS, remove this data from the Archive fields.
#def modifyTreatmentData(project_df_arch, project_df_ipss, metadata_arch, metadata_ipss, project_arch, project_ipss, except_ids=None):
#    t_treatment = Timer('Modify treatment data')
#    treat_fields_arch = set()
#    treat_fields_ipss = set()
#    for field_name, field_obj in metadata_arch.iteritems():
#        if (field_obj.form_name in ['treatment_table', 'medical_treatment']):
#            treat_fields_arch.add(field_name)
#    for field_name, field_obj in metadata_ipss.iteritems():
#        if (field_obj.form_name == 'treatment'):
#            treat_fields_ipss.add(field_name)
#
#    record_ids_with_ipss_treat_data = set()
#    for row_index in project_df_ipss.index:
#        id = project_df_ipss.loc[row_index, project_ipss.def_field]
#        data_in_row = False
#        if id in record_ids_with_ipss_treat_data: # if ID was already found
#            continue
#        for field in treat_fields_ipss:
#            if ('___' in field):
#                if (project_df_ipss.loc[row_index, field] == '1'):
#                    data_in_row = True
#            elif (project_df_ipss.loc[row_index, field] != ''):
#                data_in_row = True
#            if data_in_row:
#                record_ids_with_ipss_treat_data.add(id)
#                break
#
#    # Remove excepted IDs from list of IDs to be modified.
#    ids_to_mod = [id for id in record_ids_with_ipss_treat_data if (not id in except_ids)]
#
#    project_df_arch.loc[project_df_arch[project_arch.def_field].isin(ids_to_mod), treat_fields_arch] = 'NA' #'NA (refer to fields in IPSS form Treatment)' # overwrite data if it already exists in IPSS.
#    t_treatment.stop()
#    return project_df_arch, record_ids_with_ipss_treat_data
#
#project_df_arch, record_ids_with_ipss_treat_data = modifyTreatmentData(project_df_arch, project_df_ipss, metadata_arch, metadata_ipss, project_arch, project_ipss, except_ids=ids_custom_mod_arch_only+ids_custom_mod_arch_treat_only)

## Transfer 'Summary of Impressions' data from PSOM fields to IPSS fields. Handle this differently for the final SIPS package.
if (args.package_name in ['malig', 'subhem', 'meet2019']):
    def modifySummaryOfImpressionsData(project_df_ipss, project_df_psom, metadata_psom, project_psom):
        t_soi = Timer('Modify Summary of Impressions data')
        psom_to_ipss_map = {'fuionset_soi':'fuionset', "fpsomr": 'fpsomr', "fpsoml": 'fpsoml', "fpsomlae": 'fpsomlae', "fpsomlar": 'fpsomlar', "fpsomcb": 'fpsomcb', "psomsen___1": 'psomsen___3', "psomsen___2": 'psomsen___4', "psomsen___3": 'psomsen___5', "psomsen___4": 'psomsen___6', "psomsen___5": 'psomsen___7', "psomsen___6": 'psomsen___8', "psomsen___7": 'psomsen___9', "psomsen___8": 'psomsen___10', "psomsen___9": 'psomsen___11', "psomsen___10": 'psomsen___12', "psomsen___11": 'psomsen___13', "psomsen___12": 'psomsen___14', "fpsomco___1": 'fpsomco___1', "fpsomco___2": 'fpsomco___2', "othsens": 'othsens', 'totpsom':'totpsom', "fucomm": 'fucomm'}
        ipss_to_psom_map = {}
        for key, val in psom_to_ipss_map.iteritems():
            ipss_to_psom_map[val] = key
    
        # (-1) If taking from PSOM V2, need to remove the 'acute_hospitalizat_arm_1' event.
        print "Rows in PSOM dataframe prior to removing 'acute_hospitalizat_arm_1' event:", len(project_df_psom)
        project_df_psom = project_df_psom.loc[~(project_df_psom['redcap_event_name']=='acute_hospitalizat_arm_1'),:]
        print "Rows in PSOM dataframe prior to removing 'acute_hospitalizat_arm_1' event:", len(project_df_psom)

        # (0) Delete all summary of impressions data for SickKids patients.
        #t_soi_del = Timer('(0) Delete HSC Summary of Impressions data from IPSS')
        # WAS DOING THIS SOI DELETION STEP FOR TESTING. WHEN I DO THIS, ONLY PATIENTS WHO DO NOT EXIST IN PSOM RETAIN THE NA TAG, AND NONE OF THESE APPEAR TO HAVE A SOI. SIMPLY LEAVE THEIR IPSS SOI DATA THIER INSTEAD OF DELETING IT.
    #    project_df_ipss.loc[(project_df_ipss['redcap_data_access_group']=='hsc'), ipss_to_psom_map] = 'NA (Overwritten by fields in PSOM database)' 
        #t_soi_del.stop()

        # (1) Change the event name and instance to match those used in IPSS
        #t_soi_rep = Timer('(1) Change event names and instances in PSOM to match IPSS')    
        for row_index in project_df_psom.index:
            event_name_psom = project_df_psom.loc[row_index, 'redcap_event_name']
            repeat_instrument_psom = project_df_psom.loc[row_index, 'redcap_repeat_instrument'] # Will always be blank.
            instance_psom = project_df_psom.loc[row_index, 'redcap_repeat_instance']
        
            project_df_psom.loc[row_index, 'redcap_event_name'] = 'followup_arm_1'
            project_df_psom.loc[row_index, 'redcap_repeat_instrument'] = 'outcome'
    
            if (event_name_psom == 'initial_psom_arm_1'):
                project_df_psom.loc[row_index, 'redcap_repeat_instance'] = '1'
            elif (event_name_psom == 'follow_up_psom_arm_1'):
                project_df_psom.loc[row_index, 'redcap_repeat_instance'] = str(int(float(instance_psom)) + 1)
        #t_soi_rep.stop()
        
        # (2) Append '_psom' to each variable name in the PSOM dataframe, so that the sets of IPSS and PSOM variable names are disjoint.
        #t_soi_ren = Timer('(2) Add "_psom" to each PSOM variable')
        new_columns = {column:column+'_psom' for column in metadata_psom if (not column == project_psom.def_field)}
        project_df_psom = project_df_psom.rename(columns=new_columns)
        #t_soi_ren.stop()
    
        # (3) Join the PSOM database with the IPSS database.
        #t_soi_join = Timer('(3) Join IPSS and PSOM dataframes')
        project_df_ipss = project_df_ipss.merge(project_df_psom, on=['ipssid','redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], how='outer').fillna('')
        #t_soi_join.stop()
    
        # (4) Copy the '_psom' fields to their IPSS counterpart fields, only for PSOM patients.
        #t_soi_over = Timer('Overwrite IPSS fields with PSOM fields')
        columns_to_remove = [] # Build for step (5) below.
        for key, val in ipss_to_psom_map.iteritems():
            real_val = val+'_psom'
            project_df_ipss.loc[(project_df_ipss['ipssid'].isin(project_df_psom['ipssid'])), key] = project_df_ipss.loc[(project_df_ipss['ipssid'].isin(project_df_psom['ipssid'])), real_val]
            columns_to_remove.append(real_val)
        #t_soi_over.stop()
    
        # (5) Delete the '_psom' fields from the IPSS dataframe.
        #t_soi_delpsom = Timer('Delete PSOM fields from IPSS dataframe')
        project_df_ipss = project_df_ipss[[column for column in project_df_ipss.columns if (not column in columns_to_remove)]]
        #t_soi_delpsom.stop()
    
        # (6) Add DAG for all PSOM patients, because newly added rows will not have a DAG.
        project_df_ipss.loc[project_df_ipss['ipssid'].isin(project_df_psom['ipssid']), 'redcap_data_access_group'] = 'hsc'
        
        t_soi.stop()
        return project_df_ipss
    
    skip_soi_mod = False
    if args.debug:
        skip_soi_mod = True
    if skip_soi_mod:
        print Color.red+'WARNING: SKIPPING MODIFICATION OF SUMMARY OF IMPRESSIONS DATA.'+Color.end
    else:
        if (args.package_name in ['malig', 'subhem']):
            project_df_ipss = modifySummaryOfImpressionsData(project_df_ipss, project_df_psom, metadata_psom, project_psom)
        if (args.package_name in ['meet2019']):
            project_df_ipss = modifySummaryOfImpressionsData(project_df_ipss, project_df_psom2, metadata_psom2, project_psom2) # need to remove all rows for event acute_hospitalizat_arm_1.

# For single-row format: Create a mapping event_name:{list of fields} that determines the event from which each field will be selected.
if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
    t_event_field_map = Timer('Creating map between events and fields')
    event_field_mapping_arch = {} # keys are tuples (event_name, repeat_instrument_name) ; values are sets of field names
    for field_name, field_obj in metadata_arch.iteritems():
        if ('acute_arm_1' in field_obj.events_containing_field): # if field is in this event
            desired_event = 'acute_arm_1'
        else: # all fields are in acute or followup, no need to handle treatment_with_rec_arm_1 event
            desired_event = 'follow_up_arm_1'
    
        # If field is non-repeating in the desired event, set repeating form name to '', if independently repeating in this event, set to form name.
        if desired_event in form_repetition_map_arch[field_obj.form_name]['events_non_repeat']:
            desired_repeat_form = '' # row contains non-repeating fields in desired event.
        elif desired_event in form_repetition_map_arch[field_obj.form_name]['events_indep_repeat']:
            desired_repeat_form = field_obj.form_name
        elif desired_event in form_repetition_map_arch[field_obj.form_name]['events_dep_repeat']:
            print 'ERROR: Unhandled repetition type.'
            pass # Project doesn't contain any dependently repeating forms; don't bother to handle.
    
        # Add field to mapping.
        key = (desired_event, desired_repeat_form)
        if (not key in event_field_mapping_arch):
            event_field_mapping_arch[key] = set([field_name])
        else:
            event_field_mapping_arch[key].add(field_name)
    # Add DAG to list manually since it doesn't have a form/event.
    dag_key = ('acute_arm_1', '')
    if dag_key in event_field_mapping_arch:
        event_field_mapping_arch[dag_key].add('redcap_data_access_group')
    else:
        event_field_mapping_arch[dag_key] = set(['redcap_data_access_group'])
    
    event_field_mapping_ipss = {}
    for field_name, field_obj in metadata_ipss.iteritems():
        if ('acute_arm_1' in field_obj.events_containing_field): # if field is in this event
            desired_event = 'acute_arm_1'
        else:
            desired_event = 'followup_arm_1'
    
        # If field is non-repeating in the desired event, set repeating form name to '', if independently repeating in this event, set to form name.
        if desired_event in form_repetition_map_ipss[field_obj.form_name]['events_non_repeat']:
            desired_repeat_form = '' # row contains non-repeating fields in desired event.
        elif desired_event in form_repetition_map_ipss[field_obj.form_name]['events_indep_repeat']:
            desired_repeat_form = field_obj.form_name
        elif desired_event in form_repetition_map_ipss[field_obj.form_name]['events_dep_repeat']:
            print 'ERROR: Unhandled repetition type.'
            pass # Project doesn't contain any dependently repeating forms; don't bother to handle.
    
        # Add field to mapping.
        key = (desired_event, desired_repeat_form)
        if (not key in event_field_mapping_ipss):
            event_field_mapping_ipss[key] = set([field_name])
        else:
            event_field_mapping_ipss[key].add(field_name)
    # Add DAG to list manually since it doesn't have a form/event.
    dag_key = ('acute_arm_1', '')
    if dag_key in event_field_mapping_ipss:
        event_field_mapping_ipss[dag_key].add('redcap_data_access_group')
    else:
        event_field_mapping_ipss[dag_key] = set(['redcap_data_access_group'])
    t_event_field_map.stop()

def combineFieldsForms(metadata, field_list, form_list):
    """Take a list of field names and a list of form names for a given project. Add all the fields in the list of form names to the list of field names. If both lists are 
    None, return a list of all fields in the project."""
    if (form_list == None) and (field_list == None): 
        field_list = set([field_name for field_name in metadata]) # Generate list of all fields in project
    elif (form_list != None):
        if (field_list == None):
            field_list = set() # Initialize empty list of fields and populate it with fields in form_list; else start from existing list of fields and add fields from form_list
        for field_name, field_obj in metadata.iteritems(): # Add fields contained in form_list to field_list
            if (field_obj.form_name in form_list):
                field_list.add(field_name)

    # Ensure that list of field names is the same as they appear in the data dictionary
    field_list = [field_name for field_name in metadata if (field_name in field_list)]
    return field_list

def listIncludedFields(field_list, form_list, event_list, metadata, def_field, restrict_events):
    '''Input project dataframe, metadata, lists of fields and forms to include, list of events to include, the current record ID variable name, and whether certain events should be excluded.
    Returns a set containing the names of the fields which should be included from the current project.'''

    field_list = combineFieldsForms(metadata, field_list, form_list) # convert list of fields and forms to a list of fields.

    ## Exclude fields that are not in the requested event.
    if (restrict_events):
        field_set = set()
        for field_name in field_list:
            field_obj = metadata[field_name]
            if (len(event_list.intersection(field_obj.events_containing_field)) != 0): # if the field is in one of the requested events.
                field_set.add(field_name)
    else:
        field_set = set(field_list)
    return field_set


#def removeExcludedFields(project_df_current, field_list, form_list, event_list, metadata, def_field, restrict_events):
#    ### Generate list of variables to include from each project.
#
#    print "THIS FUNCTION IMPROPERLY DELETES FIELDS WHOSE NAME APPEARS IN MULTIPLE DATABASES."
#
#    field_list = combineFieldsForms(metadata, field_list, form_list) # convert list of fields and forms to a list of fields.
#
#    ## Exclude fields that are not in the requested event.
#    if (restrict_events):
#        field_set = set()
#        for field_name in field_list:
#            field_obj = metadata[field_name]
#            if (len(event_list.intersection(field_obj.events_containing_field)) != 0): # if the field is in one of the requested events.
#                field_set.add(field_name)
#    else:
#        field_set = set(field_list)
#
#    # Generate list of field names to remove from the dataframe.
#    fields_to_remove = set([field_name for field_name in metadata])
#    fields_to_remove -= field_set
#    try:
#        fields_to_remove.remove(def_field) # do not attempt to remove the ID field.
#    except KeyError:
#        #print Color.red+"WARNING: (2) Failed to remove '"+def_field+"' from 'fields_to_remove' for unknown reason. * HANDLE THIS CASE!"+Color.end
#        pass
#
#    project_df_current = project_df_current[[col for col in project_df_current.columns if (not col in fields_to_remove)]]
#    return project_df_current

if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
    def flattenData(project_df_current, event_field_mapping, def_field, record_ids):
        # Remove fields from event_field_mapping if they are not in the current dataframe.
        t_flatten = Timer('flattenData()')
        event_field_mapping_current = {}
        for key, field_set in event_field_mapping.iteritems():
            event_field_mapping_current[key] = field_set.intersection(project_df_current.columns)
    
        # Remove all but the first instance of each repeating form. * Lisa Sun data package only
        project_df_current = project_df_current.loc[project_df_current['redcap_repeat_instance'].isin(['', '1'])]
        
        ## Flatten data to one row per record
        # Verify that indices are not duplicated 
        index_duplication = any(project_df_current.index.duplicated())
        if index_duplication:
            print Color.red+"WARNING: duplicated indices in project_df_all. Reassigning indices."
            project_df_current.reset_index(inplace=True)
            
        ## Flatten rows.
        ids = list(unique_everseen(list(project_df_current[def_field])))
        df_new = pandas.DataFrame({def_field:ids}, dtype=unicode)
        for key, field_set in event_field_mapping_current.iteritems():
            selection_field_list = [def_field] + [field_name for field_name in field_set if (not field_name == def_field)]
            selection = project_df_current.loc[(project_df_current['redcap_event_name'] == key[0]) & (project_df_current['redcap_repeat_instrument'] == key[1]), selection_field_list].astype(unicode)
            df_new = df_new.merge(selection, on=[def_field], how='outer').fillna('')
    
        # Re-order rows to match original dataframe.
        df_new = df_new[[column for column in project_df_current.columns if (column in df_new)]]
        project_df_current = deepcopy(df_new)
        t_flatten.stop()
        return project_df_current

if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
    def archAppendSuffix(df, metadata_arch):
        """Append '_from_old' to columns which are fields in the IPSS Archive."""
    
        suffix = '_from_old'
    
        # Add _from_old to all fields taken from the IPSS Archive
        print "Warning: Appending '_from_old' to all Archive fields."
        for field_name, field_obj in metadata_arch.iteritems():
            if (field_name in df.columns):
                # Checked if suffixed name is already taken.
                field_name_new = field_name + suffix
                if (field_name_new in df.columns):
                    print "Error: Renamed field (from instrument '"+field_obj.form_name+"') already in dataframe:", field_name_new
                else:
                    df.rename({field_name: field_name_new}, axis=1, inplace=True)
        return df

## Create subsets of the data per specifications of requestor.
t_create_wss = Timer('Create worksheets')

for format_type in format_type_list:
    # Copy dataframes and modify a separate instance of project_df_current_format for each format_type
    if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
        project_df_arch_current_format = deepcopy(project_df_arch)
    project_df_ipss_current_format = deepcopy(project_df_ipss) 
    if (args.package_name in ['sips', 'sipsf']):
        project_df_sips2_current_format = deepcopy(project_df_sips2)
    if (args.package_name in ['sipsf']):
        project_df_psom2_current_format = deepcopy(project_df_psom2)

    # Flattens acute and followup data to a single row (repeated fields get deleted).
    if (format_type == 'singlerow'): 
        project_df_arch_current_format = flattenData(project_df_arch_current_format, event_field_mapping_arch, project_arch.def_field, record_ids_arch)
        project_df_ipss_current_format = flattenData(project_df_ipss_current_format, event_field_mapping_ipss, project_ipss.def_field, record_ids_ipss)
        if (args.package_name in ['sips']):
            project_df_sips2_current_format = flattenData(project_df_sips2_current_format, event_field_mapping_sips2, project_sips2.def_field, record_ids_sips2)

    ## Create a single DataFrame by joining the DataFrames of each project.
    t_merge = Timer("Merge IPSS and Archive for format: "+format_type)
    if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
        project_df_arch_current_format = modify_arch(project_df_arch_current_format) # convert 'pk_patient_id' to 'ipssid', 'follow_up_arm_1' to 'followup_arm_1'.
    
        ## Remove fields and rename instruments that are duplicated in Archive and IPSS. Change or delete only the Archive duplicate. 
        print 'Warning: Lazily deleting height and weight from Archive Dataframe, and modifying repeat_instrument name of recovery_and_recurrence, instead of handling genearal case of duplicate variable/form names between databases. weight and height from Archive are not requested. Forms from archive recovery and recurrence are not requested.'
        #del project_df_arch_current_format['height']
        #del project_df_arch_current_format['weight']
        project_df_arch_current_format.drop('height', axis=1, inplace=True)
        project_df_arch_current_format.drop('weight', axis=1, inplace=True)
        del metadata_arch['height']
        del metadata_arch['weight']
    
        # Rename Archive recovery_and_recurrence form. This is necessary because it has the same name as an IPSS form, and repeats independently in both databases.
        if (format_type == 'multirow'):
            indices_to_modify = (project_df_arch_current_format['redcap_repeat_instrument'] == 'recovery_and_recurrence') # recovery_and_recurrence is the only repeating Archive form whose name is used in IPSS
            project_df_arch_current_format.loc[indices_to_modify, 'redcap_repeat_instrument'] = 'recovery_and_recurrence_from_arch'

    # For SIPS data package 'other_specify' is required from both Archive and SIPS II, it NEEDS TO BE HANDLED. MUST CHANGE df.columns AND metadata KEY, RENDERING THINGS INCOMPATIBLE POSSIBLY.
    if (args.package_name in ['sips']):
#        print 'Warning: Lazily deleting gender from SIPS Dataframe. It is not requested.'
#        del project_df_sips2_current_format['gender']
#        project_df_sips2_current_format.drop('gender', axis=1, inplace=True)
        print "WARNING: CHANGING NAME OF 'other_specify' and 'gender' IN SIPS II DATAFRAME AND METADATA, BECAUSE IT CONFLICTS WITH AN ARCHIVE VARIABLE."
        new_names = {'other_specify':'other_specify_from_sips2', 'gender':'gender_from_sips2'}
        project_df_sips2_current_format.rename(columns=new_names, inplace=True)
        metadata_sips2 = OrderedDict([(key, val) if (not key in new_names) else (new_names[key], val) for (key, val) in metadata_sips2.iteritems()])

    # For SIPS final data package 'gender' is required from both IPSS V3 and SIPS II, it NEEDS TO BE HANDLED. MUST CHANGE df.columns AND metadata KEY, RENDERING THINGS INCOMPATIBLE POSSIBLY.
    if (args.package_name in ['sipsf']):
        print "Warning: Renaming all fields which are used in multiple projects in all projects. UNDO THIS LATER!!! THIS HAS NOT BEEN TESTED!!!"
        print "Warning: This renaming method will break if you request specific fields as opposed to specific forms."
        # Rename duplicated IPSS V3 fields
        rename_fields_ipss = {}
        for field_name in project_df_ipss_current_format.columns:
            if (not field_name in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']):
                if (field_name in project_df_sips2.columns) or (field_name in project_df_psom2.columns):
                    rename_fields_ipss[field_name] = field_name + '_renamed_ipss'
                    project_df_ipss_current_format.rename(columns=rename_fields_ipss, inplace=True)
                    metadata_ipss = OrderedDict([(key, val) if (not key in rename_fields_ipss) else (rename_fields_ipss[key], val) for (key, val) in metadata_ipss.iteritems()])
        # Rename duplicated SIPS II fields
        rename_fields_sips2 = {}
        for field_name in project_df_sips2_current_format.columns:
            if (not field_name in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']):
                if (field_name in project_df_ipss.columns) or (field_name in project_df_psom2.columns):
                    rename_fields_sips2[field_name] = field_name + '_renamed_sips2'
                    project_df_sips2_current_format.rename(columns=rename_fields_sips2, inplace=True)
                    metadata_sips2 = OrderedDict([(key, val) if (not key in rename_fields_sips2) else (rename_fields_sips2[key], val) for (key, val) in metadata_sips2.iteritems()])
        # Rename duplicated PSOM V2 fields
        rename_fields_psom2 = {}
        for field_name in project_df_psom2_current_format.columns:
            if (not field_name in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']):
                if (field_name in project_df_sips2.columns) or (field_name in project_df_ipss.columns):
                    rename_fields_psom2[field_name] = field_name + '_renamed_psom2'
                    project_df_psom2_current_format.rename(columns=rename_fields_psom2, inplace=True)
                    metadata_psom2 = OrderedDict([(key, val) if (not key in rename_fields_psom2) else (rename_fields_psom2[key], val) for (key, val) in metadata_psom2.iteritems()])

    if (args.package_name in ['sips']):
        for col in project_df_sips2_current_format:
            if col in project_df_arch_current_format.columns:
                print 'Warning:', col, 'is a field in SIPS II and Archive.'
            if col in project_df_ipss_current_format.columns:
                print 'Warning:', col, 'is a field in SIPS II and IPSS.'

    if (args.package_name in ['sipsf']):
        for col in project_df_sips2_current_format:
            if col in project_df_ipss_current_format.columns:
                print 'Warning:', col, 'is a field in SIPS II and IPSS.'
            if col in project_df_psom2_current_format.columns:
                print 'Warning:', col, 'is a field in SIPS II and PSOM V2.'


    # Merge IPSS and Archive data.
    if (format_type == 'singlerow'):
        on_list = ['ipssid']
    else:
        on_list = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance']
    project_df_all_current_format = project_df_ipss_current_format
    if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
        for col in project_df_all_current_format.columns:
            if (col in project_df_arch_current_format.columns) and (not col in on_list):
                print "Warning: Merging dataframes (IPSS V3 with Archive) with duplicate column:", col
        project_df_all_current_format = project_df_all_current_format.merge(project_df_arch_current_format, on=on_list, how='outer', suffixes=('','_from_arch')).fillna('')
    if (args.package_name in ['sips', 'sipsf']):
        for col in project_df_all_current_format.columns:
            if (col in project_df_sips2_current_format.columns) and (not col in on_list):
                print "Warning: Merging dataframes (IPSS V3 with SIPS II) with duplicate column:", col
        project_df_all_current_format = project_df_all_current_format.merge(project_df_sips2_current_format, on=on_list, how='outer', suffixes=('','_from_sips2')).fillna('')
    if (args.package_name in ['sipsf']):
        for col in project_df_all_current_format.columns:
            if (col in project_df_psom2_current_format.columns) and (not col in on_list):
                print "Warning: Merging dataframes (IPSS V3 + SIPS II merge with PSOM V2) with duplicate column:", col
        project_df_all_current_format = project_df_all_current_format.merge(project_df_psom2_current_format, on=on_list, how='outer', suffixes=('','_from_psom2')).fillna('')

    # Sort the dataframe by ipssid, redcap_repeat_instance.
    if (format_type == 'multirow'):
        t_sort = Timer('Sort data based on primary key')

        # Add version of IPSSID to convert to a number for sorting purposes; remove it immediately after sorting is complete.
#        project_df_all_current_format['ipssid_as_float'] = project_df_all_current_format['ipssid']
#        def ipssid_to_float(id):
#            return float(id.replace('-','.'))
#        project_df_all_current_format.loc[:, 'ipssid_as_float'] = project_df_all_current_format.loc[:, 'ipssid_as_float'].apply(ipssid_to_float)
#        project_df_all_current_format.loc[:, 'redcap_repeat_instance'] = project_df_all_current_format.loc[:, 'redcap_repeat_instance'].apply(change_dtype)
#        project_df_all_current_format.loc[:, 'ipssid_as_float'] = project_df_all_current_format.loc[:, 'ipssid_as_float'].apply(change_dtype)
#        print project_df_all_current_format[['ipssid', 'ipssid_as_float']]
#        project_df_all_current_format.sort_values(['ipssid_as_float', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], inplace=True) 
#        # Remove the float-IPSSID column which was used for sorting
#        project_df_all_current_format.drop('ipssid_as_float', axis=1, inplace=True)

        # Retry sorting above:
        project_df_all_current_format['ipssid_as_int_1'] = project_df_all_current_format['ipssid']
        project_df_all_current_format['ipssid_as_int_2'] = project_df_all_current_format['ipssid']
        def ipssid_to_int_1(ipssid):
            return int(ipssid.split('-')[0])
        def ipssid_to_int_2(ipssid):
            try:
                if ('-' in ipssid):
                    return int(ipssid.split('-')[1])
                else:
                    return 0
            except ValueError:
                return 0 # Required for the ID '9203-'

        project_df_all_current_format.loc[:, 'ipssid_as_int_1'] = project_df_all_current_format.loc[:, 'ipssid_as_int_1'].apply(ipssid_to_int_1)
        project_df_all_current_format.loc[:, 'ipssid_as_int_2'] = project_df_all_current_format.loc[:, 'ipssid_as_int_2'].apply(ipssid_to_int_2)
        project_df_all_current_format.loc[:, 'redcap_repeat_instance'] = project_df_all_current_format.loc[:, 'redcap_repeat_instance'].apply(change_dtype)
#        project_df_all_current_format.loc[:, 'ipssid_as_float'] = project_df_all_current_format.loc[:, 'ipssid_as_float'].apply(change_dtype)
        print project_df_all_current_format[['ipssid', 'ipssid_as_int_1', 'ipssid_as_int_2']]
        project_df_all_current_format.sort_values(['ipssid_as_int_1', 'ipssid_as_int_2', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], inplace=True) 
        # Remove the integer-IPSSID columns which were used for sorting
        project_df_all_current_format.drop(['ipssid_as_int_1', 'ipssid_as_int_2'], axis=1, inplace=True)        

        t_sort.stop()

    if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
        # Remove the Archive DAG column after transferring over the Archive DAGs to the IPSS DAGs for rows that correspond to repeating forms in the Archive.
        missing_dag_indices = (project_df_all_current_format['redcap_data_access_group'] == '') # Series of bools associated with each index in dataframe
        project_df_all_current_format.loc[missing_dag_indices, 'redcap_data_access_group'] = project_df_all_current_format.loc[missing_dag_indices, 'redcap_data_access_group_from_arch']
    #    del project_df_all_current_format['redcap_data_access_group_from_arch']
        project_df_all_current_format.drop('redcap_data_access_group_from_arch', axis=1, inplace=True)

    # Remove the SIPS II DAG colum
    if (args.package_name in ['sips', 'sipsf']):
        project_df_all_current_format.drop('redcap_data_access_group_from_sips2', axis=1, inplace=True)

    # Remove the PSOM V2 DAG colum # There isn't such a DAG column in PSOM.
#    if (args.package_name in ['sipsf']):
#        project_df_all_current_format.drop('redcap_data_access_group_from_psom2', axis=1, inplace=True)
    t_merge.stop()

    if (not args.debug):
        ## Overwrite fields if they are only valid for either the 1992-2014 patients or the 2014-present patients.
        t_na = Timer("Overwrite fields with NA if they didn't exist at time of entry for format: "+format_type)

#        ###### MANUAL OVERWRITE SPECIFIC FORMS FOR HAND-PICKED LIST OF RECORDS. I DON'T KNOW HOW THESE ID LISTS WERE GENERATED, AND IT IS NOT SAFE TO ASSUME THAT THESE LISTS SHOULD NOT BE DIFFERENT NOW
        if (args.package_name in ['malig', 'subhem', 'meet2019']):
            # "Reabstracted V3 Data N=77"
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_mod_ipss_only)), [col for col in project_df_all_current_format.columns if ((col in metadata_arch) and ((metadata_arch[col].form_name in ['medical_treatment', 'treatment_table', 'radiographic_stroke_features']) or (col in stroke_presentation_select_fields)))]] = 'NA' # 'NA (reabstracted V3 data N=76)'
    
            # "Archive Data N=4210"
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_mod_arch_only)), [col for col in project_df_all_current_format.columns if ((col in metadata_ipss) and (metadata_ipss[col].form_name in ['arteriopathy_diagnosis_classification', 'prothrombotichypercoaguability_state', 'radiographic_features_at_presentation', 'treatment', 'tpa_specific_questions', 'additional_thromboembolic_events_during_initial_ho']))]] = 'NA' # 'NA (patient was enrolled between 2003-2014)'
            
            # "Data to be taken from V3 with the exception of "Radiographic Features" data (which should come from Archive)"
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_mod_ipss_only_except_radio)), [col for col in project_df_all_current_format.columns if (((col in metadata_arch) and ((metadata_arch[col].form_name in ['medical_treatment', 'treatment_table']) or (col in stroke_presentation_select_fields))) or ((col in metadata_ipss) and (metadata_ipss[col].form_name == 'radiographic_features_at_presentation')))]] = 'NA' # 'NA (Partial reabstracted V3 except radiographic data)'
    
            # "Data to be taken from V3 with the exception of "treatment" data (which should come from the archive)"
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_mod_ipss_only_except_treat)), [col for col in project_df_all_current_format.columns if (((col in metadata_arch) and ((metadata_arch[col].form_name in ['radiographic_stroke_features']) or (col in stroke_presentation_select_fields))) or ((col in metadata_ipss) and (metadata_ipss[col].form_name == 'treatment')))]] = 'NA' # 'NA (Partial reabstracted V3 except treatment data)'
    
    #        # Forms not completed for 1992-2014 patients:
    #        # Use the indices and columns returned by getEmptyRows() to overwrite fields in forms which are completely empty in a given row.
    #        forms_post_2014 = ['arteriopathy_diagnosis_classification', 'prothrombotichypercoaguability_state', 'radiographic_features_at_presentation', 'treatment', 'tpa_specific_questions', 'additional_thromboembolic_events_during_initial_ho']
    #        empty_selection = getEmptyRows(project_df_all_current_format, metadata_ipss, 'ipssid', col_list=None, form_list=forms_post_2014, ids=record_ids_arch) # Overwrite all excluded forms with NA
    #        project_df_all_current_format.loc[empty_selection.index, empty_selection.columns] = unicode('NA (patient was enrolled between 2003-2014)')
    
    #        # "Data to be taken from Archive ONLY" = SKU: Overwrite IPSS fields in forms_post_2014.
    #        col_list = [field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name in forms_post_2014)]
    #        project_df_all_current_format.loc[project_df_all_current_format['ipssid'].isin(ids_custom_mod_arch_only), col_list] = unicode('NA (patient was enrolled between 2003-2014)')
    
    #        # "Data to be taken from V3 with the exception of "radiographic features" data (which should come from archive)" = SKU: Overwrite IPSS fields in radiographic form.
    #        # ALSO NEED TO MAKE SURE THAT ARCHIVE RADIOGRAPHIC DATA DID NOT GET OVERWRITTEN.
    #        col_list = [field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name == 'radiographic_features_at_presentation')]
    #        project_df_all_current_format.loc[project_df_all_current_format['ipssid'].isin(ids_custom_mod_arch_radio_only), col_list] = unicode('NA (patient was enrolled between 2003-2014)')
    
    #        # "Data to be taken from V3 with the exception of "treatment" data (which should come from archive)"
    #        # ALSO NEED TO ENSURE THAT ARCHIVE TREATMENT DATA DID NOT GET OVERWRITTEN.
    #        col_list = [field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name == 'treatment')]
    #        project_df_all_current_format.loc[project_df_all_current_format['ipssid'].isin(ids_custom_mod_arch_treat_only), col_list] = unicode('NA (patient was enrolled between 2003-2014)')
            ###### SKETCHY SECTION END
    
            # Forms not completed for 2014-present patients:
            record_ids_ipss_only = [id for id in record_ids_ipss if (not id in record_ids_arch)]
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(record_ids_ipss_only)), [col for col in project_df_all_current_format.columns if ((col in metadata_arch) and (not col in metadata_ipss))]] = 'NA' # 'NA (patient was enrolled into REDCap)'
            # I DON'T KNOW WHY I WOULD HAVE USED THE METHOD BELOW, AND IT SEEMS TO HAVE CAUSED ERRORS. REPLACE WITH ABOVE METHOD.
    #        empty_selection = getEmptyRows(project_df_all_current_format, metadata_arch, 'ipssid', col_list=None, form_list=None, ids=record_ids_ipss_only) # Get all Archive variables for IPSS-only patients
    #        project_df_all_current_format.loc[empty_selection.index, empty_selection.columns] = unicode('NA (patient was enrolled into REDCap)') # Overwrite all excluded forms with NA
        elif (args.package_name in ['sips']):
            ## SIPS package manual overwrites.
            # For SIPS II cohort II, overwrite all Archive and old 1-row-per-patient data with NA.
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_sips2_cohort_2)), [col for col in project_df_all_current_format.columns if (col in metadata_arch)]] = 'NA'
            project_df_1row_rad.loc[(project_df_1row_rad['ipssid'].isin(ids_sips2_cohort_2)), [col for col in project_df_1row_rad.columns]] = 'NA'            
            project_df_1row_tre.loc[(project_df_1row_tre['ipssid'].isin(ids_sips2_cohort_2)), [col for col in project_df_1row_tre.columns]] = 'NA'            

            # For non SIPS II cohort II, overwrite all Archive data with NA.
            project_df_all_current_format.loc[(project_df_all_current_format['ipssid'].isin(ids_not_sips2_cohort_2)), [col for col in project_df_all_current_format.columns if (col in metadata_ipss) and (metadata_ipss[col].form_name in ['radiographic_features_at_presentation', 'treatment'])]] = 'NA'

        elif (args.package_name in ['sipsf']):
            ## SIPS final package manual overwrites 
            # For SIPS I and SIPS II cohort I patients, overwrite fields in IPSS V3 instruments 'radiographic_features_at_presentation' and 'treatment'.
            ids_to_modify_sipsf = project_df_all_current_format.loc[project_df_all_current_format['substud___6']=='1','ipssid'] # SIPS I and SIPS II cohort I
            project_df_all_current_format.loc[project_df_all_current_format['ipssid'].isin(ids_to_modify_sipsf), [col for col in project_df_all_current_format.columns if ((col in metadata_ipss) and (metadata_ipss[col].form_name in ['radiographic_features_at_presentation','treatment']))]] = 'NA'
        t_na.stop()
    else:
        print Color.red+'WARNING: Skipping NA overwrite for debug.'+Color.end

    for field_list in field_list_list:
        field_list_name = field_list['name']

        if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
            field_list_arch = field_list['arch']['fields'] # * GIVES, E.G. 'CHECKBOX_NAME' INSTEAD OF 'CHECKBOX_NAME___1'
            if (field_list_arch != None):
                field_list_arch = set(convertFieldNames(url_arch, key_arch, project_arch.def_field, field_list_arch))
            form_list_arch = field_list['arch']['forms']
        
        field_list_ipss = field_list['ipss']['fields']
        if (field_list_ipss != None):
            field_list_ipss = set(convertFieldNames(url_ipss, key_ipss, project_ipss.def_field, field_list_ipss))
        form_list_ipss = field_list['ipss']['forms']

        if (args.package_name in ['sips', 'sipsf']):
            field_list_sips2 = field_list['sips2']['fields']
            if (field_list_sips2 != None):
                field_list_sips2 = set(convertFieldNames(url_sips2, key_sips2, project_sips2.def_field, field_list_sips2))
            form_list_sips2 = field_list['sips2']['forms']

        if (args.package_name in ['sipsf']):
            field_list_psom2 = field_list['psom2']['fields']
            if (field_list_psom2 != None):
                field_list_psom2 = set(convertFieldNames(url_psom2, key_psom2, project_psom2.def_field, field_list_psom2))
            form_list_psom2 = field_list['psom2']['forms']
    
        for event_list in event_list_list:
            restrict_events = event_list['restrict_events']
    
            event_list_name = event_list['name']
            
            if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
                event_list_arch = event_list['arch']
            event_list_ipss = event_list['ipss']
            if (args.package_name in ['sips', 'sipsf']):
                event_list_sips2 = event_list['sips2']
            if (args.package_name in ['sipsf']):
                event_list_psom2 = event_list['psom2']

            if (restrict_events):
                event_list_all = event_list_arch.union(event_list_ipss)
                if (args.package_name in ['sips']):
                    event_list_all = event_list_all.union(event_list_sips2)

            # Create deep copies of the dataframes to modify for each sub-package. Retain the original dataframes.
    #        t_dc = Timer('Deep copy dataframes')
            project_df_all_current_format_fields_events = deepcopy(project_df_all_current_format)
    #        t_dc.stop()
    
            print "DataFrame dimensions prior to field removal:", len(project_df_all_current_format_fields_events), 'X', len(project_df_all_current_format_fields_events.columns)
            t_rm_fields = Timer('Remove fields from current worksheet: '+field_list_name+", events: "+event_list_name)
            # REDO FIELD EXCLUSION BELOW. INSTEAD OF PERFORMING SEPARATE FIELD EXCLUSIONS FOR EACH DATABASE, GENERATE A LIST OF FIELDS TO INCLUDE, THEN DO ONE EXCLUSION OPERATION BASED ON THAT LIST.
            
            # Generate list of fields to include from each project
            # THIS SHOULD WORK PROPERLY FOR CORRECTLY RENAMED FIELDS (if they were renamed in the metadata and the dataframe)
            include_set = set(['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group']) # primary key variables
            if (args.package_name in ['malig', 'subhem', 'meet2019', 'sips']):
                include_set.update(listIncludedFields(field_list_arch, form_list_arch, event_list_arch, metadata_arch, 'ipssid', restrict_events)) # IPSS Archive variables
            include_set.update(listIncludedFields(field_list_ipss, form_list_ipss, event_list_ipss, metadata_ipss, 'ipssid', restrict_events)) # IPSS V3 variables
            # Do not list 1-row-per-patient variables, since they are added later.
                               
#            project_df_all_current_format_fields_events = removeExcludedFields(project_df_all_current_format_fields_events, field_list_arch, form_list_arch, event_list_arch, metadata_arch, 'ipssid', restrict_events) # Remove unrequested Archive fields 
#            project_df_all_current_format_fields_events = removeExcludedFields(project_df_all_current_format_fields_events, field_list_ipss, form_list_ipss, event_list_ipss, metadata_ipss, 'ipssid', restrict_events) # Remove unrequested Archive fields 
            if (args.package_name in ['sips', 'sipsf']):
#                project_df_all_current_format_fields_events = removeExcludedFields(project_df_all_current_format_fields_events, field_list_sips2, form_list_sips2, event_list_sips2, metadata_sips2, 'ipssid', restrict_events) # Remove unrequested SIPS II fields 
                include_set.update(listIncludedFields(field_list_sips2, form_list_sips2, event_list_sips2, metadata_sips2, 'ipssid', restrict_events)) # SIPS II variables.

            if (args.package_name in ['sipsf']):
                include_set.update(listIncludedFields(field_list_psom2, form_list_psom2, event_list_psom2, metadata_psom2, 'ipssid', restrict_events)) # PSOM V2 variables.
                
            # Remove all fields which are not in the list of included variables.
            project_df_all_current_format_fields_events = project_df_all_current_format_fields_events[[col for col in project_df_all_current_format_fields_events.columns if col in include_set]]
            t_rm_fields.stop()
            print "DataFrame dimensions after field removal:", len(project_df_all_current_format_fields_events), 'X', len(project_df_all_current_format_fields_events.columns)

            # Remove rows that don't correspond to any of the events requested from IPSS or Archive
            if (restrict_events):
                t_rm_events = Timer('Removing events from current worksheet: '+field_list_name+", events: "+event_list_name)
                project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['redcap_event_name'].isin(event_list_all), :]
                t_rm_events.stop()

            # Convert from unicode to int or float where possible. MOVED TO addSheet()
#            if (not args.debug):
#                t_change_dtype = Timer('Converting dtypes')
#                for column in project_df_all_current_format_fields_events.columns:
#                    if (not column in ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_data_access_group']): # CONVERT INSTANCE NUMBER
#                        project_df_all_current_format_fields_events.loc[:, column] = project_df_all_current_format_fields_events[column].apply(change_dtype)
#                t_change_dtype.stop()
#            else:
#                print Color.red+'WARNING: Skipping dtype conversion for debug.'

            t_write_ws = Timer("Write worksheet for sheet: "+field_list_name+", events: "+event_list_name+", format: "+format_type)
        
            ## Write DataFrame to worksheet.
            if (args.package_name == 'malig'):
                # Create workbook.
                path_report = os.path.join(dir_report, "data_package_"+args.package_name+"_"+field_list_name+"_"+event_list_name+'_'+format_type+".xlsx")
                writer = pandas.ExcelWriter(path_report, engine='xlsxwriter')

                # Remove treatment fields from acute dataframe.
                project_df_all_current_format_fields_events = project_df_all_current_format_fields_events[[col for col in project_df_all_current_format_fields_events.columns if (not col in metadata_arch) or (not metadata_arch[col].form_name == 'treatment_table')]]

                ## Add data from old one-row-per-patient data package.
                for col in project_df_1row_rad.columns:
                    if (col in project_df_all_current_format_fields_events.columns):
                        print "Column in acute treatment data already present in DataFrame:", col
                for col in project_df_1row_tre.columns:
                    if (col in project_df_all_current_format_fields_events.columns):
                        print "Column in acute treatment data already present in DataFrame:", col
                for col in project_df_1row_tre.columns:
                    if (col in project_df_1row_rad.columns):
                        print "Warning: Same variable named used in 1-row-per-patient radiology and acute_treatment tabs: "+str(col)

                # Merge old and current data.
                project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.merge(project_df_1row_rad, on=['ipssid'], suffixes=('_from_ipss','_from_old'), how='left').fillna('')
                project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.merge(project_df_1row_tre, on=['ipssid'], suffixes=('_from_ipss','_from_old'), how='left').fillna('')

                # OVERWRITE THE ACUTE FIELDS FROM THE OLD 1-ROW-PER-PATIENT DATA PACKAGE WITH NA IF THE RECORD CONTAINS ANY DATA IN THE IPSS TREATMENT FORM.
                project_df_all_current_format_fields_events.loc[(project_df_all_current_format_fields_events['ipssid'].isin(ids_mod_ipss_only+ids_mod_ipss_only_except_radio)), [col for col in project_df_all_current_format_fields_events.columns if (('_from_old' in col) and (col in project_df_1row_tre.columns))]] = 'NA' # 'NA (reabstracted V3 data or reabstracted V3 data except radiographic data)'

                # Fill in treatment table and radiographic investigations fields with NA for patients that were not included in the old one-row-per-patient data package.
                #project_df_all_current_format_fields_events.loc[~project_df_all_current_format_fields_events['ipssid'].isin(project_df_1row_tre['ipssid']), [col for col in project_df_1row_tre.columns if (not col == 'ipssid')]] = 'NA (patient was enrolled into REDCap)'
                record_ids_ipss_only = [id for id in record_ids_ipss if (not id in record_ids_arch)]
                project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(record_ids_ipss_only), [col for col in project_df_1row_rad.columns if (not col == 'ipssid')]] = 'NA' # 'NA (patient was enrolled into REDCap)'
                project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(record_ids_ipss_only), [col for col in project_df_1row_tre.columns if (not col == 'ipssid')]] = 'NA' # 'NA (patient was enrolled into REDCap)'


                # Append '_from_old' to IPSS Archive fields.
#                project_df_all_current_format_fields_events = archAppendSuffix(project_df_all_current_format_fields_events, metadata_arch)

                addSheet(writer, project_df_all_current_format_fields_events, 'all_forms')
            elif (args.package_name in ['subhem', 'meet2019']):
                # Create workbook.
                path_report = os.path.join(dir_report, "data_package_"+args.package_name+"_"+field_list_name+"_"+event_list_name+'_'+format_type+".xlsx")
                writer = pandas.ExcelWriter(path_report, engine='xlsxwriter')

                if (event_list_name == 'acute'):
                    # Remove treatment fields from acute dataframe.
                    project_df_all_current_format_fields_events = project_df_all_current_format_fields_events[[col for col in project_df_all_current_format_fields_events.columns if (not col in metadata_arch) or (not metadata_arch[col].form_name == 'treatment_table')]]
    
                    ## Add data from old one-row-per-patient data package.
                    for col in project_df_1row_rad.columns:
                        if (col in project_df_all_current_format_fields_events.columns):
                            print "Column in acute treatment data already present in DataFrame:", col
                    for col in project_df_1row_tre.columns:
                        if (col in project_df_all_current_format_fields_events.columns):
                            print "Column in acute treatment data already present in DataFrame:", col
                    for col in project_df_1row_tre.columns:
                        if (col in project_df_1row_rad.columns):
                            print "Warning: Same variable named used in 1-row-per-patient radiology and acute_treatment tabs: "+str(col)
                    
                    # Merge old and current data.
                    project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.merge(project_df_1row_rad, on=['ipssid'], suffixes=('_from_ipss','_from_old'), how='left').fillna('')
                    project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.merge(project_df_1row_tre, on=['ipssid'], suffixes=('_from_ipss','_from_old'), how='left').fillna('')

                    # Remove repeat instrument rows, and repeat instrument columns.
                    project_df_all_current_format_fields_events = project_df_all_current_format_fields_events.loc[(project_df_all_current_format_fields_events['redcap_repeat_instrument'] == ''), [col for col in project_df_all_current_format_fields_events.columns if (not col in ['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'])]]
    
                    # Overwrite the acute fields from the old 1-row-per-patient data package with NA if the record contains any data in the IPSS Treatment form.
                    project_df_all_current_format_fields_events.loc[(project_df_all_current_format_fields_events['ipssid'].isin(ids_mod_ipss_only+ids_mod_ipss_only_except_radio)), [col for col in project_df_all_current_format_fields_events.columns if (('_from_old' in col) and (col in project_df_1row_tre.columns))]] = 'NA' # 'NA (reabstracted V3 data or reabstracted V3 data except radiographic data)'

#                    ids_to_mod = [id for id in record_ids_with_ipss_treat_data if (not id in ids_custom_mod_arch_treat_only)]
#                    project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(ids_to_mod), [col for col in project_df_all_current_format_fields_events.columns if ('_from_old' in col) and (col in project_df_1row_tre.columns)]] = 'NA' # overwrite with the same text as the Archive Treatment Table/Medical Treatment fields.

                    # Fill in treatment table & radiographic investigations fields with NA for patients that were not included in the old one-row-per-patient data package.
                    record_ids_ipss_only = [id for id in record_ids_ipss if (not id in record_ids_arch)]
                    # SHOULD DO BASED ON PRESENCE IN ARCHIVE RATHER THAN BASED ON PRESENCE IN 1-ROW-PER-PATIENT DATA PACKAGE.
#                    project_df_all_current_format_fields_events.loc[~project_df_all_current_format_fields_events['ipssid'].isin(project_df_1row_tre['ipssid']), [col for col in project_df_1row_tre.columns if (not col == 'ipssid')]] = 'NA (patient was enrolled into REDCap)'
                    project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(record_ids_ipss_only), [col for col in project_df_1row_rad.columns if (not col == 'ipssid')]] = 'NA' # 'NA (patient was enrolled into REDCap)'
                    project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(record_ids_ipss_only), [col for col in project_df_1row_tre.columns if (not col == 'ipssid')]] = 'NA' # 'NA (patient was enrolled into REDCap)'

                    # Append '_from_old' to IPSS Archive fields.
#                    project_df_all_current_format_fields_events = archAppendSuffix(project_df_all_current_format_fields_events, metadata_arch)
    
                    addSheet(writer, project_df_all_current_format_fields_events, 'all_forms')
                elif (event_list_name == 'followup'):
                    ## Split data from each form onto a separate worksheet in the workbook.
                    # Archive data (only medical_treatment and treatment_table)
                    for form_name in ['medical_treatment', 'treatment_table']:
                        fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group']
                        fields_to_include.extend([field_name for field_name in metadata_arch if metadata_arch[field_name].form_name == form_name])
                        selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['redcap_repeat_instrument'] == form_name, fields_to_include]
                        
                        # Remove NA rows from selection. Look at first data column and check whether it says NA; if so, the whole column will be blank.
                        print "WARNING: DOING SKETCHY CHECK FOR NA ROWS BASED ON COLUMN NUMBERS."
                        column_to_query = selection.columns[5] # Should be first data column.
                        selection = selection.loc[~(selection[column_to_query] == 'NA'), :]

                        # Append '_from_old' to IPSS Archive fields.
#                        selection = archAppendSuffix(selection, metadata_arch)

                        addSheet(writer, selection, form_name)

                    # IPSS data (all forms in the follow up event).
                    for form_info in forms_ipss:
                        form_name = form_info['instrument_name']
                        if (not form_repetition_map_ipss[form_name]['indep_repeat']): # if form is non-repeating
#                            print 'Warning: Excluding form', form_name, 'from follow up workbook.'
                            continue
                        fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group']
                        fields_to_include.extend([field_name for field_name in metadata_ipss if metadata_ipss[field_name].form_name == form_name])
                        selection = project_df_all_current_format_fields_events.loc[(project_df_all_current_format_fields_events['redcap_repeat_instrument'] == form_name), fields_to_include]
                        # Remove NA rows from selection. Look at first data column and check whether it says NA; if so, the whole column will be blank.
                        column_to_query = selection.columns[5] # Should be first data column.
                        selection = selection.loc[~(selection[column_to_query] == 'NA'), :]

                        addSheet(writer, selection, form_name)
            elif (args.package_name == 'sips'):
                def removeEmpty(df, columns_to_check):
                    '''
                    Input Pandas.DataFrame
                    Return dataframe with "empty" rows removed: rows are considered empty if they contain only "NA" or "" (or "0" if checkbox); 'columns_to_check' are the rows which are check for completion.
                    '''
                    df_empty = deepcopy(df)
                    for col in columns_to_check:
                        if (col in ['ipssid', 'pk_patient_id']):
                            continue
                        if ('___' in col): # if checkbox
                            df_empty = df_empty.loc[(df_empty[col].isin(['NA', '', '0', 0])), :]
                        else:
                            df_empty = df_empty.loc[(df_empty[col].isin(['NA', ''])), :]

                    return df.loc[~df.index.isin(df_empty.index), :]

                dag_strage_columns = project_df_ipss.loc[(project_df_ipss['redcap_event_name']=='acute_arm_1'), ['ipssid', 'redcap_data_access_group', 'strage']]

                # Divide the records into two groups:
                # (1) SIPS I (including SIPS II cohort I)
                #     - exclude "screened, not enrolled"
                # (2) SIPS II
                #     - exclude "screened, not enrolled"
                #     - exclude SIPS II cohort II + "
                for cohort_name, cohort in OrderedDict([('SIPS1',ids_sips_group_1), ('SIPS2',ids_sips_group_2), ('SIPS1and2', ids_sips_group_1 + ids_sips_group_2)]).iteritems():
                    # Create workbook.
                    path_report = os.path.join(dir_report, "data_package_"+args.package_name+"_"+field_list_name+"_"+event_list_name+'_'+format_type+'_'+cohort_name+".xlsx")
                    writer = pandas.ExcelWriter(path_report, engine='xlsxwriter')

                    ## Split data from each form onto a separate worksheet in the workbook.
                    # Archive data
                    for form_info in forms_arch: # loop over forms this way to preserve order
                        form_name = form_info['instrument_name']
                        if (form_name in form_list_arch): 
#                            fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group']
#                            fields_to_include.extend([field_name for field_name in metadata_arch if (metadata_arch[field_name].form_name == form_name) and (not field_name in fields_to_include)]) # Be careful not to ask for any field twice.
#                            selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(cohort), fields_to_include]
#                            selection = removeEmpty(selection) # remove NA or empty rows.

                            ## Retry with (DAG + strage) merge. Don't include event_name since only using acute data. Don't include repeat instrument/instance for nonrepeating events.
                            fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
#                            if (form_repetition_map_arch[form_name]['indep_repeat'] or form_repetition_map_arch[form_name]['dep_repeat']):
#                                fields_to_include.extend(['redcap_repeat_instrument','redcap_repeat_instance'])
                            fields_in_form = [field_name for field_name in metadata_arch if (metadata_arch[field_name].form_name == form_name)]
                            fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)])
                            
                            selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(cohort), fields_to_include]
                            selection = removeEmpty(selection, fields_in_form) # remove columns for which the fields in the requested forms are empty or NA.

                            selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                            columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                            columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                            columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                            selection = selection[columns_reordered]

                            if (not len(selection) == 0):
                                addSheet(writer, selection, form_name)
    
                    ## 1-row-per-patient data.
                    # from radiology tab (radiographic investigations)
                    selection = project_df_1row_rad.loc[project_df_1row_rad['ipssid'].isin(cohort), :]
                    selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                    columns_reordered = ['ipssid', 'redcap_data_access_group', 'strage']
                    columns_reordered.extend([col for col in project_df_1row_rad.columns if (not col in columns_reordered)]) # don't double-add any columns
                    columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                    selection = selection[columns_reordered]
                    if (not len(selection) == 0):
                        addSheet(writer, selection, '1_row_radiographic_investigations')

                    # from acute_treatment tab:
                    selection = project_df_1row_tre.loc[project_df_1row_tre['ipssid'].isin(cohort), :]
                    selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                    columns_reordered = ['ipssid', 'redcap_data_access_group', 'strage']
                    columns_reordered.extend([col for col in project_df_1row_tre.columns if (not col in columns_reordered)]) # don't double-add any columns
                    columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                    selection = selection[columns_reordered]
                    if (not len(selection) == 0):
                        addSheet(writer, selection, '1_row_acute_treatment')

                    # IPSS data.
                    for form_info in forms_ipss: # loop over forms this way to preserve order
                        form_name = form_info['instrument_name']
                        if (cohort_name == "SIPS1") and (form_name == 'tpa_specific_questions'):
                            continue # Don't include IPSS V3 TPA form for SIPS I cohort per Chloe's request.
                        if (form_name in form_list_ipss): 
                            print 'WARNING: THIS LOOP WILL BREAK IF YOU SUDDENLY REQUEST FIELDS NOT PRESENT IN form_list_ipss'
#                            fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group']
#                            fields_to_include.extend([field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name == form_name) and (not field_name in fields_to_include)]) # Be careful not to ask for any field twice.
        #                    selection = project_df_all_current_format_fields_events.loc[(project_df_all_current_format_fields_events['redcap_repeat_instrument'] == form_name), fields_to_include]
#                            selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(cohort), fields_to_include]
#                            selection = removeEmpty(selection)
                            
                            # Retry above section.
                            fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
                            fields_in_form = [field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name == form_name)]
                            fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)]) # don't double-add a field_name
                            
                            selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(cohort), fields_to_include]
                            selection = removeEmpty(selection, fields_in_form) # remove columns for which the fields in the requested forms are empty or NA.

                            selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                            columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                            columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                            columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                            selection = selection[columns_reordered]

                            if (not len(selection) == 0):
                                addSheet(writer, selection, form_name)
    
                    # SIPS II data
                    for tab_label, form_name_list in OrderedDict([('screening_form',['screening_form']), ('confirmation_form',['confirmation_form_reviewer_1', 'confirmation_form_reviewer_2']), ('neuroimaging_crf',['neuroimaging_crf']), ('acute_crf',['acute_crf'])]).iteritems():

                        ## Retry with (DAG + strage) merge. Don't include event_name since only using acute data. Don't include repeat instrument/instance for nonrepeating events.
                        fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
                        for form_name in form_name_list:
                            if (form_repetition_map_sips2[form_name]['indep_repeat'] or form_repetition_map_sips2[form_name]['dep_repeat']):
                                fields_to_include.extend(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'])
                                break
                        fields_in_form = [field_name for field_name in metadata_sips2 if (metadata_sips2[field_name].form_name in form_name_list)]
                        fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)])
                            
                        selection = project_df_all_current_format_fields_events.loc[project_df_all_current_format_fields_events['ipssid'].isin(cohort), fields_to_include]
                        ########### DEBUG
                        if (cohort_name == 'SIPS1and2'):
                            print "Rows for form "+tab_label+": "+str(len(selection))
                        selection = removeEmpty(selection, fields_in_form) # remove NA or empty rows.
                        if (cohort_name == 'SIPS1and2'):
                            print "Rows for form "+tab_label+": "+str(len(selection))                        

                        selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                        columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                        columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                        columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                        selection = selection[columns_reordered]

                        # Special: remove anticonvulsant 5-10 data since it is empty for all patients.
                        if (tab_label == 'acute_crf'):
                            prob_empty_anticonv_fields = ['anticonvulsant_'+str(num) for num in range(5,11)] + ['ac_5_dose', 'aloneconcur5']
                            print prob_empty_anticonv_fields
                            empty_anticonv_fields = []
                            for field_name in prob_empty_anticonv_fields:
                                if (len(selection.loc[~(selection[field_name] == ''),:]) == 0):
                                    empty_anticonv_fields.append(field_name)
                                    print "Warning: Removing field", field_name, "from data package, because it seems to be empty."
                            print empty_anticonv_fields
                            selection = selection[[col for col in selection if not (col in empty_anticonv_fields)]]
    
                        if (not len(selection) == 0):
                            addSheet(writer, selection, tab_label)

            elif (args.package_name == 'sipsf'):
                def removeEmpty(df, columns_to_check):
                    '''
                    Input Pandas.DataFrame
                    Return dataframe with "empty" rows removed: rows are considered empty if they contain only "NA" or "" (or "0" if checkbox); 'columns_to_check' are the rows which are check for completion.
                    '''
                    df_empty = deepcopy(df)
                    for col in columns_to_check:
                        if (col in ['ipssid', 'pk_patient_id']):
                            continue
                        if ('___' in col): # if checkbox
                            df_empty = df_empty.loc[(df_empty[col].isin(['NA', '', '0', 0])), :]
                        else:
                            df_empty = df_empty.loc[(df_empty[col].isin(['NA', ''])), :]

                    return df.loc[~df.index.isin(df_empty.index), :]

                dag_strage_columns = project_df_ipss.loc[(project_df_ipss['redcap_event_name']=='acute_arm_1'), ['ipssid', 'redcap_data_access_group', 'strage']]
                print dag_strage_columns

                # Create workbook.
                path_report = os.path.join(dir_report, "data_package_"+args.package_name+"_"+field_list_name+"_"+event_list_name+'_'+format_type+".xlsx")
                writer = pandas.ExcelWriter(path_report, engine='xlsxwriter')

                ## Split data from each form onto a separate worksheet in the workbook.
                # IPSS data.
                for form_info in forms_ipss: # loop over forms this way to preserve order
                    form_name = form_info['instrument_name']
                    if (form_name in form_list_ipss): 
                        print 'WARNING: THIS LOOP WILL BREAK IF YOU SUDDENLY REQUEST FIELDS NOT PRESENT IN form_list_ipss'

#                        fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
                        fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'strage'] # *DO* include event & repeat form information for sanity
                        fields_in_form = [field_name for field_name in metadata_ipss if (metadata_ipss[field_name].form_name == form_name)]
                        fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)]) # don't double-add a field_name
                        print '1) strage:', 'strage' in fields_to_include
                        
                        selection = project_df_all_current_format_fields_events.loc[:, fields_to_include]
                        print '2) strage:', 'strage' in selection.columns
                        selection = removeEmpty(selection, fields_in_form) # remove rows for which the fields in the requested forms are empty or NA.
                        print '3) strage:', 'strage' in selection.columns
                        
                        print '4) strage:', 'strage' in dag_strage_columns
                        selection.drop(['strage'], inplace=True, axis=1) # Remove it from the selection (I DON'T REALLT KNOW WHY)
                        selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                        print '5) strage:', 'strage' in selection.columns
                        columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                        columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                        columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                        print '6) strage:', 'strage' in columns_reordered
                        selection = selection[columns_reordered]
                        print '7) strage:', 'strage' in selection.columns
                        # Un-rename the fields with inter-project name conflicts.
                        unrename_fields_ipss = {v:k for k,v in rename_fields_ipss.iteritems()}
                        selection.rename(columns=unrename_fields_ipss,inplace=True)
                        print '8) strage:', 'strage' in selection.columns
                        if (not len(selection) == 0):
                            addSheet(writer, selection, form_name)
    
                # SIPS II data
                for tab_label, form_name_list in OrderedDict([('screening_form',['screening_form']), ('confirmation_form',['confirmation_form_reviewer_1', 'confirmation_form_reviewer_2']), ('neuroimaging_crf',['neuroimaging_crf']), ('acute_crf',['acute_crf']), ('follow_up_crf',['follow_up_crf'])]).iteritems():

                    ## Retry with (DAG + strage) merge. Don't include event_name since only using acute data. Don't include repeat instrument/instance for nonrepeating events.
#                    fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
#                    for form_name in form_name_list:
#                        if (form_repetition_map_sips2[form_name]['indep_repeat'] or form_repetition_map_sips2[form_name]['dep_repeat']):
#                            fields_to_include.extend(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'])
#                            break

                    # In the final data package, only some forms are in each data package "format", so restrict worksheet additions accordingly.
                    tab_in_current_format = False
                    for form_name in form_name_list:
                        if form_name in form_list_sips2:
                            tab_in_current_format = True
                            break
                    if (not tab_in_current_format):
                        continue
                    print "form_list_sips2:", form_list_sips2
                    print "form_name_list", form_name_list

                    fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'] # *DO* include event & repeat form information for sanity
                    fields_in_form = [field_name for field_name in metadata_sips2 if (metadata_sips2[field_name].form_name in form_name_list)]
                    fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)])
                            
                    selection = project_df_all_current_format_fields_events.loc[:, fields_to_include]
                    selection = removeEmpty(selection, fields_in_form) # remove NA or empty rows.

                    selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                    columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                    columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                    columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                    selection = selection[columns_reordered]

                    # Special: remove anticonvulsant 5-10 data since it is empty for all patients.
                    if (tab_label == 'acute_crf'):
                        prob_empty_anticonv_fields = ['anticonvulsant_'+str(num) for num in range(5,11)] + ['ac_5_dose', 'aloneconcur5']
                        print prob_empty_anticonv_fields
                        empty_anticonv_fields = []
                        for field_name in prob_empty_anticonv_fields:
                            if (len(selection.loc[~(selection[field_name].astype(str) == ''),:]) == 0):
                                empty_anticonv_fields.append(field_name)
                                print "Warning: Removing field", field_name, "from data package, because it seems to be empty."
                        print empty_anticonv_fields
                        selection = selection[[col for col in selection if not (col in empty_anticonv_fields)]]

                    # Un-rename the fields with inter-project name conflicts.
                    unrename_fields_sips2 = {v:k for k,v in rename_fields_sips2.iteritems()}
                    selection.rename(columns=unrename_fields_sips2,inplace=True)
    
                    if (not len(selection) == 0):
                        addSheet(writer, selection, tab_label)

                # PSOM V2 data
                for form_info in forms_psom2: # loop over forms this way to preserve order
                    form_name = form_info['instrument_name']
                    if (form_name in form_list_psom2): 
                        print 'WARNING: THIS LOOP WILL BREAK IF YOU SUDDENLY REQUEST FIELDS NOT PRESENT IN form_list_psom2'

#                        fields_to_include = ['ipssid'] # don't include any repeating form information since this is only acute data.
                        fields_to_include = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'] # *DO* include event & repeat form information for sanity
                        fields_in_form = [field_name for field_name in metadata_psom2 if (metadata_psom2[field_name].form_name == form_name)]
                        fields_to_include.extend([field_name for field_name in fields_in_form if (not field_name in fields_to_include)]) # don't double-add a field_name
                        
                        selection = project_df_all_current_format_fields_events.loc[:, fields_to_include]
                        selection = removeEmpty(selection, fields_in_form) # remove columns for which the fields in the requested forms are empty or NA.

                        selection = selection.merge(dag_strage_columns, how='left', on='ipssid')
                        columns_reordered = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
                        columns_reordered.extend([col for col in fields_to_include if (not col in columns_reordered)]) # don't double-add any columns
                        columns_reordered = [col for col in columns_reordered if (col in selection.columns)] # remove columns not present in selection
                        selection = selection[columns_reordered]

                        # Un-rename the fields with inter-project name conflicts.
                        unrename_fields_psom2 = {v:k for k,v in rename_fields_psom2.iteritems()}
                        selection.rename(columns=unrename_fields_psom2, inplace=True)

                        if (not len(selection) == 0):
                            addSheet(writer, selection, form_name)

            ## Close and save workbook.
            writer.close()
            t_write_ws.stop()

t_create_wss.stop()
t_script.stop()
