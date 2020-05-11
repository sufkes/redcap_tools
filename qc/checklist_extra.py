from Check import Check # Class used to define what a check does and when it is performed

# Create list of checks (must be called 'checklist').
checklist = []

 
# Define check by specifying each of the parameters in the 'Check' class.

# For project-wide checks, include all rows in records, even those which should not exist based on 
# the events and repeating forms settings.
# Checks performed once per project include:
# - Check for (near) duplicate records.
# - Check for entries lying in fields hidden by branching logic.

#### Check: Find other rows in records which have identical values for all fields which are non-empty in the current row
name = "duplicate_rows"
description = "Find other rows in records which have identical values for all fields which are non-empty in the current row"
report_forms = False
inter_project = False
whole_row_check = True
check_invalid_entries = True # SHOULD BE FALSE BECAUSE OTHER CHECKS WILL FIND INVALID ROWS.
inter_record = True
inter_row = True
specify_fields = False

target_fields = None
rowConditions = None
fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    threshold = 1.0 # threshold which determines how similar two records must be in order to be considered duplicates

    # Look for another row which has the same entries as the current row's nonempty entries up to a
    # certain threshold.
    row = records[row_index]

    nonempty_fields = [] # fields which are nonempty in current row
    for field_name in metadata:
        if (row[field_name] != ""): # PERHAPS CHANGE TO CONSIDER CHECKBOX FIELDS WITH 0 AS EMPTY. EXCLUDE def_field, event, instance, form
            nonempty_fields.append(field_name)
    num_nonempty = len(nonempty_fields) # number of non-empty fields in current row

    duplicate_rows = [] # list of duplicate rows    

    if (num_nonempty > 0): # Only look for duplicates if row has at least one entry.
        for other_row_index in range(len(records)):
            if (other_row_index == row_index):
                continue # don't flag current row as duplicate of itself
            num_matches = 0
            other_row = records[other_row_index]
            for field_name in nonempty_fields:
                if (row[field_name] != ""):
                    if (row[field_name] == other_row[field_name]):
                        num_matches += 1
            similarity = float(num_matches)/float(num_nonempty)
            if (similarity >= threshold):
                duplicate_rows.append(other_row_index)
        if (len(duplicate_rows) > 0): # if a duplicate was found
            element_bad = True
    return element_bad, duplicate_rows

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Find values lying outside a specified minimum or maximum.
# CURRENTLY DOES NOT WORK FOR DATES.
name = "minmax"
description = "Fields with value lying outside of the allowed range specified in REDCap. (does not work for dates)"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = False
target_fields = None

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

def fieldConditions(field_name, metadata):
    field = metadata[field_name]
    if (type(field.text_validation_min) == type(float()) ) or (type(field.text_validation_max) == type(float())): # HANDLE ERRORS AT PARSE DATA DICTIONARY STEP.
        check_field = True
    else:
        check_field = False
    return check_field

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    field = metadata[field_name]
    row = records[row_index]
    try:
        if str(row[field_name]).strip() != "": # if there is an entry
            if (field.text_validation_max != None):
                if (float(row[field_name]) > field.text_validation_max):
                    element_bad = True
            if (field.text_validation_min != None):
                if (float(row[field_name]) < field.text_validation_min):
                    element_bad = True
    except ValueError:
        print "Couldn't convert:", row_index, type(records[row_index][field_name]), "entry:",records[row_index][field_name]    
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction

