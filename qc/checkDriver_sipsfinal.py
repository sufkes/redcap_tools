"""This is the driver which performs the data quality checks. For each check in the 
input checklist, it (1) determines which variables, projects, events etc. to perform the
checks on; (2) performs the check; and (3) displays the output and writes a report to 
file."""

# Standard modules
import os, sys
import glob
import time
import csv

# My modules from current directory
from reportCheckResults_sipsfinal import reportCheckResults, combineCheckReports
from formatStrings import formatDAGName

# My modules from other directories
sufkes_git_repo_dir = '/Users/steven ufkes/scripts'
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_misc")) 
from isEventFieldInstanceValid import isEventFieldInstanceValid

def getElementsToCheck(check, def_field, project_longitudinal, project_repeating, repeating_forms_events, form_repetition_map, metadata, records, record_id_map):
    # Checks which look at full rows by themselves.
    if (check.whole_row_check) and (check.check_invalid_entries) and (not check.inter_row):
        elements_to_check = []
        rows_to_check = range(len(records)) # Check all rows in records
        for row_index in rows_to_check:
            elements_to_check.append((row_index,))

    # Checks which compare two full rows in records, which could correspond to different records. 
    elif (check.whole_row_check) and (check.check_invalid_entries) and (check.inter_row):
        elements_to_check = []
        rows_to_check = range(len(records)) # Check all rows in records
        for row_index in rows_to_check:
            elements_to_check.append((row_index,)) # store as element as tuple to match form of other checks.

    elif (not check.check_invalid_entries) and (check.specify_fields):
        # For checks performed only once per record (i.e. checks which refer to
        # specific fields), do not generate a list of fields to check.
        elements_to_check = [] # will contain only a list of row numbers
        rows_to_check = [] 

        # Generate list of rows to check.
        for row_index in range(len(records)):
            if check.rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                rows_to_check.append(row_index)

        # Exclude rows which should not contain the fields targeted by the check.
        for row_index in rows_to_check:
            row = records[row_index]
            for field_name in check.target_fields:
                field = metadata[field_name]
                # Determine if current (row, field) should be displayed.
                if isEventFieldInstanceValid(project_longitudinal, project_repeating, form_repetition_map, field, row):
                    if (field.branching_logic == None): # Show if there is no branching logic.
                        elements_to_check.append((row_index, check.target_fields[0])) # include a field so that the report can specify affected form and event
                        break # if one of the target field should be filled, stop looking
                    elif field.branching_logic(row_index, form_repetition_map, records, record_id_map): # Show if branching logic returns True
                        elements_to_check.append((row_index, check.target_fields[0]))
                        break # if one of the target field should be filled, stop looking
    
    elif (not check.check_invalid_entries) and (not check.specify_fields):
        elements_to_check = []
        rows_to_check = []
        fields_to_check = []
        
        # Generate list of rows to check.
        for row_index in range(len(records)):
            if check.rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                rows_to_check.append(row_index)

        # Generate list of fields to check.
        for field_name in metadata:
            if check.fieldConditions(field_name, metadata):
                fields_to_check.append(field_name)
        
        # Generate list of (row, field) tuples to check. Exclude tuples with invalid event, instance, field combinations.
        for row_index in rows_to_check:
            row = records[row_index]
            for field_name in fields_to_check:
                field = metadata[field_name]
                # Determine if current (row, field) should be displayed.
                if isEventFieldInstanceValid(project_longitudinal, project_repeating, form_repetition_map, field, row):
                    if (field.branching_logic == None): # Show if there is no branching logic.
                        elements_to_check.append((row_index, field_name))
                    elif field.branching_logic(row_index, form_repetition_map, records, record_id_map): # Show if branching logic returns True
                        elements_to_check.append((row_index, field_name))

    elif (check.check_invalid_entries) and (not check.specify_fields):
        elements_to_check = []
        rows_to_check = []
        fields_to_check = []
        
        # Generate list of rows to check.
        for row_index in range(len(records)):
            if check.rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                rows_to_check.append(row_index)

        # Generate list of fields to check.
        for field_name in metadata:
            if check.fieldConditions(field_name, metadata):
                fields_to_check.append(field_name)
        
        # Generate list of (row, field) tuples to check. Exclude tuples with invalid event, instance, field combinations.
        for row_index in rows_to_check:
            row = records[row_index]
            for field_name in fields_to_check:
                field = metadata[field_name]
                # Determine if current (row, field) should be displayed.
                elements_to_check.append((row_index, field_name))
    return elements_to_check

def getCheckResults(check, elements_to_check, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
#    row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map

    if (check.whole_row_check) and (check.check_invalid_entries) and (not check.inter_row):
        bad_elements = []
        for element in elements_to_check:
            row_index = element[0]
            field_name = None
#            if check.checkFunction(row_index, def_field, metadata, records, repeating_forms_events, form_repetition_map):
            if check.checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                bad_elements.append(element)

    elif (check.whole_row_check) and (check.check_invalid_entries) and (check.inter_row):
        bad_elements = []
        for element in elements_to_check:
            row_index = element[0]
            field_name = None
#            element_bad, other_row_indices = check.checkFunction(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map)
            element_bad, other_row_indices = check.checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map)
            if (element_bad):
                bad_elements.append((row_index, other_row_indices))

    elif (not check.check_invalid_entries) and (check.specify_fields):
        bad_elements = [] # list of row numbers with problem sought by check.
        for element in elements_to_check:
            row_index = element[0]
            field_name = None
#            if check.checkFunction(row_index, def_field, metadata, records, form_repetition_map):
            if check.checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                bad_elements.append(element)

    elif (not check.check_invalid_entries) and (not check.specify_fields):
        bad_elements = [] # list of (row_number, field_name) tuples with problem sought by current check
        for element in elements_to_check:
            row_index = element[0]
            field_name = element[1]

#            if check.checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map): # if (row, field) has problem sought by current check
            if check.checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                bad_elements.append(element)

    elif (check.check_invalid_entries) and (not check.specify_fields):
        bad_elements = [] # list of (row_number, field_name) tuples with problem sought by current check
        for element in elements_to_check:
            row_index = element[0]
            field_name = element[1]

            if check.checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
                bad_elements.append(element)
    return bad_elements

def checkDriver(checklist, out_dir, def_field, forms, project_info, project_longitudinal, project_repeating, events, metadata, form_event_mapping, repeating_forms_events, form_repetition_map, records, record_id_map, dags_used, dags, dag_record_map):

    check_results = [] # List of (check, bad_elements) tuples to be saved to file.

    for check in checklist:
        # Determine which (tuples of) entries in the records to check.
        print "getElementsToCheck()"
        s = time.time()
        elements_to_check = getElementsToCheck(check, def_field, project_longitudinal, project_repeating, repeating_forms_events, form_repetition_map, metadata, records, record_id_map)
        e = time.time()
        print "getElementToCheck(): "+"{:.3g}".format(e-s)+"s"

        # Identify which (tuples of) entries in the records (row_index, field_name) have issues.
        print "getCheckResults()"
        s = time.time()
        bad_elements = getCheckResults(check, elements_to_check, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map)
        e = time.time()
        print "getCheckResults(): "+"{:.3g}".format(e-s)+"s"

        # Report which (tuples of) entries in the records have issues.
        print "reportCheckResults()"
        s = time.time()
        reportCheckResults(elements_to_check, bad_elements, check, out_dir, def_field, project_info, project_longitudinal, project_repeating, events, forms, form_repetition_map, metadata, records, record_id_map, dags_used, dags, dag_record_map)
        e = time.time()
        "reportCheckResults(): "+"{:.3g}".format(e-s)+"s"

        # Add check results to list for saving.
        check_results.append((check, bad_elements))

    # Combine site-specific check spreadsheets into single spreadsheets containing all checks for the site.
    combineCheckReports(checklist, out_dir, dags, dags_used)

    return check_results
