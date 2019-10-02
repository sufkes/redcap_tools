# Standard modules
import os, sys

# My modules from current directory
from reportCheckResults import reportCheckResults, combineCheckReports

# My modules from other directies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.isEventFieldInstanceValid import isEventFieldInstanceValid

def getElementsToCheck(check, def_field, project_longitudinal, project_repeating, repeating_forms_events, form_repetition_map, metadata, records, record_id_map):
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
    return elements_to_check

def getCheckResults(check, elements_to_check, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    bad_elements = [] # list of row numbers with problem sought by check.
    for element in elements_to_check:
        row_index = element[0]
        field_name = None
        if check.checkFunction(row_index, field_name, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
            bad_elements.append(element)
    return bad_elements

def checkDriverInterProject(checklist, out_dir, def_field_list, forms_list, project_info_list, project_longitudinal_list, project_repeating_list, events_list, metadata_list, form_event_mapping_list, repeating_forms_events_list, form_repetition_map_list, records_list, record_id_map_list, dags_used_list, dags_list, dag_record_map_list):
    check_results = []

    # THIS CHECK DRIVER ASSUMES THAT THE INTER-PROJECT CHECK IS OF THE FOLLOWING FORM:
    # CONSIDER THE RECORDS IN THE FIRST PROJECT ONLY (project_list[0]).
    # PERFORM A CHECK ON A SUBSET OF ENTRIES IN THE FIRST PROJECT.
    # FOR EACH OF THESE ENTRIES, COMPARE WITH ENTRIES IN THE OTHER PROJECT THAT CAN BE RETRIEVED AT 
    # THE TIME THE CHECK IS PERFORMED.

    for check in checklist: 
        # Determine which entries to check in records of first project. 
        elements_to_check = getElementsToCheck(check, def_field_list[0], project_longitudinal_list[0], project_repeating_list[0], repeating_forms_events_list[0], form_repetition_map_list[0], metadata_list[0], records_list[0], record_id_map_list[0])

        bad_elements = getCheckResults(check, elements_to_check, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list)

        reportCheckResults(elements_to_check, bad_elements, check, out_dir, def_field_list[0], project_info_list[0], project_longitudinal_list[0], project_repeating_list[0], events_list[0], forms_list[0], form_repetition_map_list[0], metadata_list[0], records_list[0], record_id_map_list[0], dags_used_list[0], dags_list[0], dag_record_map_list[0])
        
    # Combine site-specific check spreadsheets into single spreadsheets containing all checks for the site.
    combineCheckReports(checklist, out_dir, dags_list[0], dags_used_list[0])

    return
