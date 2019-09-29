from Check import Check # Class used to define what a check does and when it is performed
from getRecord import getEntryLR

# THIS SHOULD BE PUT IN THE DEFAULT CHECKLIST; I DIDN'T DO IT THE FIRST TIME BECAUSE I NEED TO HANDLE ALL CASES (LONGITUDINAL, REPEATING) IN getRecords() FUNCTIONS.

# Create list of checks (must be called 'checklist').
checklist = []

 
# Define check by specifying each of the parameters in the 'Check' class.


# For project-wide checks, include all rows in records, even those which should not exist based on 
# the events and repeating forms settings.
# Checks performed once per project include:
# - Check for (near) duplicate records.
# - Check for entries lying in fields hidden by branching logic.

#### Check: Fields that are hidden by branching logic but contain data
name = "hidden_with_data"
description = "Fields that are hidden by branching logic but contain data"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = True
inter_record = False
inter_row = False
specify_fields = False
target_fields = None

# Define function which determines whether a row should be checked (regardless of event, instance, branching logic)
def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    check_row = True # Don't exclude any rows considering row information alone.
    return check_row

# Define function which determines whether a field should be checked (regardless of branching logic).
def fieldConditions(field_name, metadata):
    if (metadata[field_name].branching_logic != None):
        check_field = True
    else:
        check_field = False
    return check_field

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False # Assume good until flaw found.

    field = metadata[field_name]
    row = records[row_index]
    record_id = row[def_field]
    event_name = row['redcap_event_name']
    instance = row['redcap_repeat_instance']
    if (instance == ''):
        instance = None

    value, hidden = getEntryLR(record_id, event_name, instance, field_name, records, record_id_map, metadata, form_repetition_map)

    if (hidden):
        if (field.field_type == "checkbox"):
            if (field_name == field.choices[0]): # Perform check when the first checkbox option is found.
                all_boxes_blank = True # Assume all blank until nonblank option found.
                for choice_field_name in field.choices: # Loop over the other checkbox options.
                    if (row[choice_field_name] == '1'):
                        all_boxes_blank = False
                        break
    
                # WON'T WORK IF FIELD NAME IS 'foo___var_name___1'.
                if (not all_boxes_blank):
                    element_bad = True
    
        elif (value != ""):
            element_bad = True
    return element_bad

# Add check instance to list of checks
print "WARNING: SKIPPING CHECK FOR DATA STORED IN FIELDS HIDDEN BY BRANCHING LOGIC, BECAUSE IT IS CRASHING IN VIPS FOR AN UNKNOWN REASON."
#checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
#del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction

