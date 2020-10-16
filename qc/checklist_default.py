from Check import Check # Class used to define what a check does and when it is performed

# Create list of checks (must be called 'checklist').
checklist = []

 
# Define check by specifying each of the parameters in the 'Check' class.

# For project-wide checks, include all rows in records, even those which should not exist based on 
# the events and repeating forms settings.
# Checks performed once per project include:
# - Check for (near) duplicate records.
# - Check for entries lying in fields hidden by branching logic.


#### Check: Find required fields which have no entry
name = "required_empty"
description = "Required fields with no entry"
report_forms = True # Whether to generate report on the number of issues broken down by instrument.
inter_project = False # Whether check compares data between multiple projects.
whole_row_check = False # Whether check involves all data in a row of data.
check_invalid_entries = False # Whether check should look at fields hidden by branching logic or fields which cannot be completed for the current row.
inter_record = False # Whether check compares data from multiple records.
inter_row = False # Whether check compares data between rows.
specify_fields = False # Whether the fields to check will be specified explicitly. 
target_fields = None # None if specify_fields is False, else set to the list of fields to be checked.

# Define function which determines whether a row should be checked (regardless of event, instance, branching logic)
def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    check_row = True # Don't exclude any rows considering row information alone.
    return check_row

# Define function which determines whether a field should be checked (regardless of branching logic).
def fieldConditions(field_name, metadata):
    field = metadata[field_name]
    if field.required_field: # Include only required fields.
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
    if (field.field_type == "checkbox"):
        if (field_name == field.choices[0]): # Perform check when the first checkbox option is found.
            all_boxes_blank = True # Assume all blank until nonblank option found.
            for choice_field_name in field.choices: # Loop over the other checkbox options.
                if (row[choice_field_name] == '1'):
                    all_boxes_blank = False
                    break

            # WON'T WORK IF FIELD NAME IS 'foo___var_name___1'.
            if all_boxes_blank:
                element_bad = True

    elif row[field_name].strip() == "":
        element_bad = True
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Find any fields which have no entry (required or not)
name = "any_empty"
description = "Fields with no entry (required or not)"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
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
    check_field = True
    return check_field

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False # Assume good until flaw found.
    field = metadata[field_name]
    row = records[row_index]
    if (field.field_type == "checkbox"):
        if (field_name == field.choices[0]): # Perform check when the first checkbox option is found.
            all_boxes_blank = True # Assume all blank until nonblank option found.
            for choice_field_name in field.choices: # Loop over the other checkbox options.
                if (row[choice_field_name] == '1'):
                    all_boxes_blank = False
                    break

            # WON'T WORK IF FIELD NAME IS 'foo___var_name___1'.
            if all_boxes_blank:
                element_bad = True

    elif row[field_name].strip() == "":
        element_bad = True
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
