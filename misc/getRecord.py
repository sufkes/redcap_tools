"""These functions are used in the branching logic functions. When a certain field in a certain row
is being checked, the branching logic will refer to other rows and fields. These functions identify 
and return the value stored in these other (row, column) pairs. 

When these functions are used depends on whether the project is longitudinal, whether it 
has repeating events, and whether the branching logic refers to a specific event."""

# If the row being referred to in the branching logic does not exist, REDCap treats it
# as if there is no entry there. If the required entry is being compared to a string, it 
# is treated as an empty string; if it is being compared to a number, it is treated as a 
# number.
# THE ISSUE OF HOW TO HANDLE STRINGS VERSUS NUMBERS DOES NOT REAR IT'S HEAD HEAR. THAT IS 
# A PROBLEM THAT MUST BE DEALT WITH IN writeBranchingLogic().

# In writeBranchingLogic(), a number of checks are performed to ensure that the branching
# logic is valid, and is restricted to cases which REDCap can handle consistently in the 
# expected way. Thus, in these functions, the branching logic can be assumed to be valid, 
# and obeys the following restrictions which are technically allowed according to REDCap's 
# erroneous documentation:
# - Non-longitudinal, repeating projects:
#     - If an instance is not specified and the requested field is repeating, the calling
#     field and the requested field must lie in the same form.
# - Longitudinal, repeating projects:
#     - If an event is specified, the requested field must be non-repeating. Thus, requests
#     of the form [event][field][instance] are not permitted.
#     - If an instance is not specified, the requested field must be either
#          (a) non-repeating;
#          (b) independently repeating and in the same form as the calling field; or
#          (c) dependently repeating.

def getEventField(row_number, required_event, required_field_name, def_field, records, record_id_map):
    row_id = records[row_number][def_field]
    row_event = records[row_number]["redcap_event_name"]

    value = "" # value returned if (row, field) does not exist in records

    # Branching logic (without smart variables) must refer to the same record.
    required_id = row_id

    # Find the row and field specified in the argument.
    for other_row_index in record_id_map[required_id]:
        other_row = records[other_row_index]
        if (other_row["redcap_event_name"] == required_event): # if other row corresponds to specified event
            value = other_row[required_field_name]
            break

#    for other_row in records:
#        if (other_row[def_field] == required_id): # if other row corresponds to same record
#            if (other_row["redcap_event_name"] == required_event): # if other row corresponds to specified event
#                value = other_row[required_field_name]
#                break
    return value

def getFieldInstance(row_number, required_field_name, required_form_name, required_instance, def_field, form_repetition_map, records, record_id_map):
    row_id = records[row_number][def_field]
    row_form_name = records[row_number]["redcap_repeat_instrument"]
    row_instance = records[row_number]["redcap_repeat_instance"]

    value = "" # value returned if (row, field) does not exist in records

    # Branching logic (without smart variables) must refer to the same record.
    required_id = row_id

    # Find the row and field specified in the argument.
    if (required_instance != None): # if instance specified (the requested field must be independently repeating)
        for other_row_index in record_id_map[required_id]:
            other_row = records[other_row_index]
            if (other_row["redcap_repeat_instrument"] == required_form_name): # if other row corresponds to an instance of the requested independently repeating form
                if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance
                    value = other_row[required_field_name]
                    break

#        for other_row in records:
#            if (other_row[def_field] == required_id): # if row corresponds to same record
#                if (other_row["redcap_repeat_instrument"] == required_form_name): # if other row corresponds to an instance of the requested independently repeating form
#                    if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance
#                        value = other_row[required_field_name]
#                        break
    elif form_repetition_map[required_form_name]["indep_repeat"]: # if requested field is independently repeating (in which case it must lie in the same form as the calling field)
#        required_instance = row_instance # If no instance specified for an independently repeating form, get the same instance as the calling row.
#        for other_row in records:
#            if (other_row[def_field] == required_id): # if row corresponds to same record
#                if (other_row["redcap_repeat_instrument"] == required_form_name): # if other row corresponds to an instance of the requested independently repeating form
#                    if (other_row["redcap_repeat_instrument"] == required_instance): # if other row corresponds to the same instance as the calling row
#                        value = other_row[required_field_name]
#                        break
        value = records[row_number][required_field_name] # Same form and instance as calling field, therefore must be in the same row.
    else: # if an instance was not specified and the requested field is non-repeating
        for other_row_index in record_id_map[required_id]:
            other_row = records[other_row_index]
            if (other_row["redcap_repeat_instrument"] == ""): # if row does not correspond to a repeating form
                value = other_row[required_field_name]
                break

#        for other_row in records:
#            if (other_row[def_field] == required_id): # if row corresponds to the same record
#                if (other_row["redcap_repeat_instrument"] == ""): # if row does not correspond to a repeating form
#                    value = other_row[required_field_name]
#                    break

#    elif (same_form): # if the form from which the branching logic is being called is the required form
#        value = records[row_number][required_field_name]
#    elif (form_repetition_map[required_form_name]["non_repeat"]): # if required form is non-repeating
#        for other_row in records:
#            if (other_row[def_field] == required_id):
#                if (other_row["redcap_repeat_instrument"].strip() == ""):
#                    value = other_row[required_field_name]
#                    break
#    else: # no instance is specified; the required field is in a different form; the required form is repeating
#        for other_row in records:
#            if (other_row[def_field] == required_id):
#                if (other_row["redcap_repeat_instrument"] == required_form_name):
#                    print "Checking field "+required_field_name+" in instance number:", other_row["redcap_repeat_instance"]
#                    if (other_row[required_field_name].strip() != ""):
#                        value = other_row[required_field_name]
#                        print "Found non-empty entry."
#                        break
     
#    # Find the row and field specified in the argument.
#    for other_row in records:
#        if (other_row[def_field] == required_id): # if this row is for the same record
#            if (other_row["redcap_repeat_instrument"] == required_form_name):
#                if (other_row["redcap_repeat_instance"] == required_instance): 
#                    value = other_row[required_field_name]
#                    break
    return value

def getEventFieldInstance(row_number, required_event, required_field_name, required_form_name, required_instance, def_field, form_repetition_map, records, record_id_map):
    row_id = records[row_number][def_field] # Get the record ID (e.g. the value in the 'ipssid' field).
    row_event = records[row_number]["redcap_event_name"]
    row_instance = records[row_number]["redcap_repeat_instance"] # Will be blank for nonrepeating fields.

    # Branching logic (without smart variables) must refer to the same record.
    required_id = row_id

    value = ""

    if (required_event != None): # if event specified (in which case the requested field must be non-repeating:
        for other_row_index in record_id_map[required_id]:
            other_row = records[other_row_index]
            if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the specified event
                if (other_row["redcap_repeat_instance"] == ""): # if other row is non-repeating
                    value = other_row[required_field_name]
                    break

#        for other_row in records:
#            if (other_row[def_field] == required_id): # if other row corresponds to the same record
#                if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the specified event
#                    if (other_row["redcap_repeat_instance"] == ""): # if other row is non-repeating
#                        value = other_row[required_field_name]
#                        break
    else: # if no event specified
        required_event = row_event # If no event specified, always refer to the same event.
        # Determine whether the requested field is non-repeating, independently repeating, or 
        # dependently repeating. Handle each case appropriately.

        # NR
        if (required_event in form_repetition_map[required_form_name]["events_non_repeat"]): # if the required field is nonrepeating in the required event
            for other_row_index in record_id_map[required_id]:
                other_row = records[other_row_index]
                if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
                    if (other_row["redcap_repeat_instance"] == ""): # if other row is non-repeating
                        value = other_row[required_field_name]
                        break

#            for other_row in records:
#                if (other_row[def_field] == required_id): # if other row corresponds to the same record
#                    if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
#                        if (other_row["redcap_repeat_instance"] == ""): # if other row is non-repeating
#                            value = other_row[required_field_name]
#                            break
        # IR
        elif (required_event in form_repetition_map[required_form_name]["events_indep_repeat"]): # if the required field is independently repeating in the required event
            if (required_instance != None): # if an instance was specified
                for other_row_index in record_id_map[required_id]:
                    other_row = records[other_row_index]
                    if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
                        if (other_row["redcap_repeat_instrument"] == required_form_name): # if other row corresponds to the required independently repeating form
                            if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance of the independently repeating form
                                value = other_row[required_field_name]
                                break

#                for other_row in records:
#                    if (other_row[def_field] == required_id): # if other row corresponds to the same record
#                        if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
#                            if (other_row["redcap_repeat_instrument"] == required_form_name): # if other row corresponds to the required independently repeating form
#                                if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance of the independently repeating form
#                                    value = other_row[required_field_name]
#                                    break
            else: # if an instance was not specified (in which case the requested field lies in the same form as the calling field, and the required instance is same as the calling field)
                value = records[row_number][required_field_name]
        # DR
        else: # if the required field is dependently repeating in the calling form
            if (required_instance != None): # if an instance was specified
                for other_row_index in record_id_map[required_id]:
                    other_row = records[other_row_index]
                    if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
                        if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance (it automatically correpsonds the the DR event)
                            value = other_row[required_field_name]
                            break

#                for other_row in records:
#                    if (other_row[def_field] == required_id): # if other row corresponds to the same record
#                        if (other_row["redcap_event_name"] == required_event): # if other row corresponds to the same event
#                            if (other_row["redcap_repeat_instance"] == required_instance): # if other row corresponds to the specified instance (it automatically correpsonds the the DR event)
#                                value = other_row[required_field_name]
#                                break
            else: # if an instance was not specified
                value = records[row_number][required_field_name]                                

    return value

def getEntryNLNR(record_id, field_name, records, record_id_map):
    """Get specific value in records of a non-longitudinal, non-repeating project."""
    return "PH(value)"

def getEntryLNR(record_id, event, field_name, records, record_id_map):
    """Get specific value in records of a longitudinal, non-repeating project."""
    return "PH(value)"

def getEntryNLR(record_id, event, instance, field_name, records, record_id_map, form_repetition_map):
    """Get specific value in records of a non-longitudinal, repeating project."""
    return "PH(value)"

def getEntryLR(record_id, event, instance, field_name, records, record_id_map, metadata, form_repetition_map):
    """Get specific value in records of a longitudinal, repeating project.
    Unlike the other functions in this module, this function is not used inside the branching logic.
    This function is used to retrieve a value from the records. In the branching logic, the event or
    instance may not be specified, but a particular event and instance must be selected. In this
    function, the event and instance must be specified, so the function is much simpler."""
    
    # event must be specified.
    # instance will be None for non-repeating form.

    value = "" # THINK ABOUT THIS CAREFULLY.
    hidden = None

    field = metadata[field_name]

    if event in form_repetition_map[field.form_name]["events_indep_repeat"]:
        repeat_instrument = field.form_name
    else:
        repeat_instrument = "" # set blank if form is non-repeating or dependently repeating in event.

    for row_index in record_id_map[record_id]: # loop over rows corresponding to requested record ID.
        if (records[row_index]["redcap_event_name"] == event):
            if (records[row_index]["redcap_repeat_instrument"] == repeat_instrument): # in correct row for fields form.
                if ((records[row_index]["redcap_repeat_instance"] == "") and (instance == None)) or (records[row_index]["redcap_repeat_instance"] == instance):
                    value = records[row_index][field_name]
                    
                    # Determine if field is hidden by branching logic.
                    hidden = True
                    if (field.branching_logic == None):
                        hidden = False
                    elif field.branching_logic(row_index, form_repetition_map, records, record_id_map): # Show if branching logic returns True
                        hidden = False
    return value, hidden
