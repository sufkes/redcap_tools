#!/usr/bin/env python

## NEED TO CHANGE TO ALLOW FOR THE CASE WHEN ONLY CERTAIN FIELDS ARE REQUESTED.

# Standard modules
import os, sys
import warnings

# Non-standard modules
import redcap
import pandas

# My modules from current directory
from exportProjectInfo import exportProjectInfo
from getEvents import getEvents
from exportFormEventMapping import exportFormEventMapping
from exportRepeatingFormsEvents import exportRepeatingFormsEvents
from exportFormsOrdered import exportFormsOrdered
from createFormRepetitionMap import createFormRepetitionMap
from parseMetadata import parseMetadata
from createRecordIDMap import createRecordIDMap
from getDAGs import getDAGs
from createDAGRecordMap import createDAGRecordMap
from isEventFieldInstanceValid import isEventFieldInstanceValid
from Color import Color
from ProgressBar import ProgressBar

def labelRecords(api_url, api_key, records_all, records_requested, all_requested, project, requested_format, label_overwrite=False, quiet=False):
    """This function takes records exported from exportRecords.py and replaces entries with the value
    'rr_hidden' if the (row number, field name) is hidden by branching logic, 'rr_invalid' if the 
    (row number, field name) is not supposed to be filled in for the row's (record ID, event, repeat 
    form, repeat instance) combination, and 'rr_error' if there is an error in the branching logic for
    the field. 

    If label_overwrite=True, fields containing values can be overwritten by 'rr_hidden' or 'rr_error'.
    """

    # Get the field name of the unique identifying field (e.g. "ipssid").
    if (not quiet):
        p_info = ProgressBar("(1/4) Getting project information")
        pass
    def_field = project.def_field
    
#    records = records_all

    # Load high-level projct information.
    project_info = exportProjectInfo(api_url, api_key)
    project_longitudinal = bool(project_info["is_longitudinal"])
    project_repeating = bool(project_info["has_repeating_instruments_or_events"])
        
    # Load list of events
    #events = getEvents(project, project_info, project_longitudinal)
    events = getEvents(api_url, api_key)
    
    # Load raw data dictionary.
    metadata_raw = project.export_metadata()
    
    # Load instrument-event mapping
    form_event_mapping = exportFormEventMapping(project, project_longitudinal)
    
    # Load information specifying which forms are repeating.
    repeating_forms_events = exportRepeatingFormsEvents(api_url, api_key, project_repeating)
   
    # Generate list of forms - list of dicts with two keys: 'instrument_label' and 'instrument_name'
    forms = exportFormsOrdered(api_url, api_key)
    forms_list = project.forms
    form_complete_names = []
    for form_name in forms_list:
        form_complete_name = form_name + '_complete'
        form_complete_names.append(form_complete_name)
    
    # Generate a dictionary with form_names as keys; each entry is a dict specifying in which 
    # events the form is non-repeating, indpendently repeating, or dependently repeating.
    form_repetition_map = createFormRepetitionMap(project_longitudinal, project_repeating, form_event_mapping, repeating_forms_events, forms)
    
    # Gather data about each variable.
    metadata = parseMetadata(def_field, project_info, project_longitudinal, project_repeating, events, metadata_raw, form_event_mapping, repeating_forms_events, forms, form_repetition_map)

    # Generate non-redundant list of record IDs.
    record_id_map = createRecordIDMap(def_field, records_all)

    # Build list of primary keys -- (ID, event, repeat form, repeat instance) tuples -- in the requested records.
    if (not all_requested):
        if (not project_longitudinal) and (not project_repeating):
            prim_key = (def_field,)
        elif (not project_longitudinal) and (project_repeating):
            prim_key = (def_field, 'redcap_repeat_instrument', 'redcap_repeat_instance')
        elif (project_longitudinal) and (not project_repeating):
            prim_key = (def_field, 'redcap_event_name')
        elif (project_longitudinal) and (project_repeating):
            prim_key = (def_field, 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance')
        
        # Populate list of primary keys:
        prim_key_vals = []
        for row_index in range(len(records_requested)):
            row = records_requested[row_index]
            prim_key_val = tuple(row[key] for key in prim_key)
            prim_key_vals.append(prim_key_val)
#        print prim_key_vals

    # Build list of fields in the requested records.
    fields_requested = tuple(field_name for field_name in records_requested[0].keys() if (field_name in metadata) or (field_name in form_complete_names))
#    print fields_requested

    # Label records.
    if (not quiet):
        p_info.stop()
        p_check = ProgressBar("(2/4) Checking whether fields are hidden and applicable to the current row")
        milestone = max(len(records_all)/2000, 1)
        pass
    list_invalid = []
    list_branching_logic_error = []
    list_hidden = []
    list_row_indices = [] # list of row indices in requested records.
    for row_index in range(len(records_all)):
        row = records_all[row_index]
#        print row['ipssid'], row['redcap_event_name'], row['redcap_repeat_instrument'], row['redcap_repeat_instance']
        if (not all_requested): # if certain rows are being excluded
            prim_key_val = tuple(row[key] for key in prim_key) 
#            print prim_key_val
            if (not prim_key_val in prim_key_vals): # if row is not in records_requested.
                continue
            else:
                list_row_indices.append(row_index)
#        for field_name, field in metadata.iteritems():
        for field_name in fields_requested:
            # The record ID field is always valid; do not perform checks on it.
            if (field_name == def_field):
                continue

            # DEBUG: Skip the form_complete fields for now.
            if (field_name in form_complete_names):
                continue
            
            field = metadata[field_name]
            
            # Check if (row index, field name) can possibly contain data.
            cell_valid = isEventFieldInstanceValid(project_longitudinal, project_repeating, form_repetition_map, field, row)
            if (not cell_valid):
#                records_all[row_index][field_name] = "r_invalid"
                list_invalid.append((row_index, field_name))

            # Check if branching logic function is bugged for current field. Replace all values with "r_error" if so.
            if cell_valid:
                if (field.branching_logic_errors != []):
                    bl_valid = False
                    list_branching_logic_error.append((row_index, field_name))
                    warnings.warn('Malformed branching logic found for field: '+field_name)
                else:
                    bl_valid = True

            # Check if (row index, field name) is hidden by branching logic.
            try:
                if cell_valid and bl_valid:
                    if (field.branching_logic == None):
                        visible = True
                    elif field.branching_logic(row_index, form_repetition_map, records_all, record_id_map):
                        visible = True
                    else:
                        visible = False
                    if (not visible):
                        list_hidden.append((row_index, field_name))
            except:
                print field_name
        if (not quiet):
            if (row_index % milestone == 0):
                p_check.update(float(row_index+1)/float(len(records_all)))
                pass
    if (not quiet):
        p_check.stop()
        p_label = ProgressBar("(3/4) Applying labels to cells that are hidden or inavlid for the current row")
        num_cells_to_label = len(list_hidden) + len(list_branching_logic_error) + len(list_invalid)
        num_labelled = 0
        milestone = max(num_cells_to_label/2000, 1)
        pass
        
    # Markup records with types after finding all of them
    for cell in list_hidden:
        row_index, field_name = cell
        field_is_checkbox = (metadata[field_name].field_type == 'checkbox')
        if label_overwrite:
            records_all[row_index][field_name] = "rr_hidden"
        elif field_is_checkbox: # THIS SECTION IS REDUNDANT.
            cb_blank = True
            for option in metadata[field_name].choices:
                if (records_all[row_index][option] == '1'): # if an option is found to be selected.
                    cb_blank = False
            if cb_blank:
                records_all[row_index][field_name] = 'rr_hidden'
        else:
            if (records_all[row_index][field_name] == ''):
                records_all[row_index][field_name] = 'rr_hidden'
        if (not quiet):
            num_labelled += 1
            if (num_labelled % milestone == 0):
                p_label.update(float(num_labelled)/float(num_cells_to_label))
    for cell in list_branching_logic_error:
        row_index, field_name = cell
        field_is_checkbox = (metadata[field_name].field_type == 'checkbox')
        if label_overwrite:
            records_all[row_index][field_name] = "rr_blerror"
        elif field_is_checkbox: # THIS SECTION IS REDUNDANT.
            cb_blank = True
            for option in metadata[field_name].choices:
                if (records_all[row_index][option] == '1'): # if an option is found to be selected.
                    cb_blank = False
            if cb_blank:
                records_all[row_index][field_name] = 'rr_blerror'
        else:
            if (records_all[row_index][field_name] == ''):
                records_all[row_index][field_name] = 'rr_blerror'
        if (not quiet):
            num_labelled += 1
            if (num_labelled % milestone == 0):
                p_label.update(float(num_labelled)/float(num_cells_to_label))
    for cell in list_invalid: # checkbox fields will be blank in this case. 
        row_index, field_name = cell
        if (label_overwrite) or (records_all[row_index][field_name] == ''):
            records_all[row_index][field_name] = "rr_invalid"
        if (not quiet):
            num_labelled += 1
            if (num_labelled % milestone == 0):
                p_label.update(float(num_labelled)/float(num_cells_to_label))
                pass
    if (not quiet):
        p_label.stop()
        p_check = ProgressBar("(4/4) Formatting and checking for errors")
        pass
        
    # Select only the requested records from records_all
    if all_requested:
        records = records_all
    else:
        records = []
        for row_index in list_row_indices:
            records.append({key:records_all[row_index][key] for key in prim_key})
            records[-1]['redcap_data_access_group'] =  records_all[row_index]['redcap_data_access_group']
            for field_name in fields_requested:
                records[-1][field_name] = records_all[row_index][field_name]

    # Convert to CSV if requested.
    if (requested_format == "csv"):        
        records_df = pandas.DataFrame(records)
        ## Rearrange the columns to their standard CSV order.
        # Get column list from DataFrame.
        columns = records_df.columns.tolist()
        columns_ordered = []

        # To generate a list of all fields in order, including those that were not requested, build a list of all real data fields, and all form complete fields. Request all of these for the first row in CSV format, then split the CSV header at each comma to get the ordered list of headers.
        first_id = records_all[0][def_field]
        first_record = project.export_records(records=[first_id], fields=list(set([field.split('___')[0] for field in records_requested[0].keys() if (not field in ['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group'])])), export_data_access_groups=True, format='csv')
        columns_ordered = [col.strip() for col in first_record.split('\n')[0].split(',')]
                
        # THE FOLLOWING REORDERING METHOD DOES NOT WORK IF FORM_COMPLETE FIELDS ARE INCLUDED.
        # Add the "standard" columns to the list.
        #for heading in [def_field, "redcap_event_name", "redcap_repeat_instrument", "redcap_repeat_instance", "redcap_data_access_group"]:
            #if (heading in columns) and (not heading in columns_ordered): # if heading was exported.
                #columns_ordered.append(heading)

        # Add the fields in the list they appear in metadata, excluding unexported fields.
        #for form_name in forms_list:
            #for field_name in metadata:
                #if (metadata[field_name].form_name == form_name) and (field_name in columns) and (not field_name in columns_ordered):
                    #columns_ordered.append(field_name)

            # Add the form_complete field for the current form if it was requested.
            #form_complete_name = form_name + '_complete'
            #if (form_complete_name in columns) and (not form_complete_name in columns_ordered):
                #columns_ordered.append(form_complete_name)

        # Do sanity check that size of ordered headings is same as size of unordered headings.
        if (len(columns) != len(columns_ordered)):
            print "Number of ordered headings differs from size of unordered headings"
        if (len(set(columns_ordered)) != len(columns_ordered)):
            print "ERROR: Duplicate headings in ordered column headings."
            for heading in columns_ordered:
                if (columns_ordered.count(heading) > 1):
                    print "Duplicated heading:", heading
        for heading in list(set(columns) - set(columns_ordered)):
            print "Heading missing from ordered heading list:", heading
        for heading in list(set(columns_ordered) - set(columns)):
            print "Heading missing from unorderd heading list:", heading

            
        records_df = records_df[columns_ordered] # Reorder the columns.
        records = records_df.to_csv(index=False, encoding='utf-8') # Convert DataFrame to CSV string

    if (not quiet):
        p_check.stop()
        pass
    return records
                
