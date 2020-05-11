import os, sys

from tokenizeBranchingLogic import tokenizeBranchingLogic
from translateTokens import translateTokens
from getRecord import getEventField, getFieldInstance, getEventFieldInstance
from Color import Color

def doesFieldExist(field_name, metadata_without_branching_logic):
    try:
        metadata_without_branching_logic[field_name]
        field_exists = True
    except KeyError:
        field_exists = False
    return field_exists

def doesEventExist(event_name, events):
    if (event_name in events):
        event_exists = True
    else: 
        event_exists = False
    return event_exists

def doesEventContainField(event_name, field_name, metadata_without_branching_logic):
    if (event_name in metadata_without_branching_logic[field_name].events_containing_field):
        event_contains_field = True
    else:
        event_contains_field = False
    return event_contains_field

def isEventFieldInstanceValidBL(arg, field_name, project_longitudinal, project_repeating, form_repetition_map, events, metadata_without_branching_logic):
    """The purpose of this function is to determine if the [event][var][instance] is valid for the 
    branching logic string."""
    if (not project_longitudinal) and (not project_repeating):
        # Possible problems:
        # 1. An event or repetition is specified: handled elsewhere by counting braces.
        # 2. Variable specified does not exist: handled elsewhere while parsing argument.
#        event_field_instance_valid = True
        pass
    elif (project_longitudinal) and (not project_repeating):
        # Possible problems:
        # 1. An event and repetition are specified: handled elsewhere by counting braces.
        # 2. A repetition (no event) is specified: handled elsehwhere while parsing argument.
        # 3. Variable specified does not exist: handled elsewhere while parsing argument.
        # 4. Event specified does not exist: handled below
        # 5. Specified event does not include variable: handle below
        if (arg["event"] != None):
            if doesEventExist(arg["event"], events):
                if doesEventContainField(arg["event"], arg["field_name"], metadata_without_branching_logic):
#                    event_field_instance_valid = True
                    pass
                else: # if specified event does not contain field
#                    event_field_instance_valid = False
                    error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies the event '"+arg["event"]+"' for the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', but the event does not include the field."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
            else: # if specified event does not exist
#                event_field_instance_valid = False
                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies the event '"+arg["event"]+"', but the event does not exist."
                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
        # 6. No event specified: assume same event as row being checked. Raise error when current event does not include requested field.
        else: # if no event is specified
            # If no event is specified, the field will be searched for in the event from which
            # the field is being requested. If no event is specified, the variable should appear in 
            # every event from which it will be requested, otherwise a warning should be raised.
            for event in metadata_without_branching_logic[field_name].events_containing_field:
                if (not doesEventContainField(event, arg["field_name"], metadata_without_branching_logic)):
                    #print "BRANCHING LOGIC ERROR: The field '"+arg["field_name"]+"' is called without specifying an event from the event '"+event+"', which does not contain the field -- this field will never be filled in for this event."
                    error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which calls the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"' without specifying an event from the event '"+event+"', but the event does not include the field."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
#            event_field_instance_valid = True
    elif (not project_longitudinal) and (project_repeating):
        # Possible problems:
        # 1. An event and repetition are specified: handled elsewhere by counting braces.
        # 2. An event (no repetition) is specified: handled elsewhere while parsing argument.
        # 3. Variable specified does not exist: handled elsewhere while parsing argument.
        # 4. Instance specified for non repeating form: handle here; REDCap does not find the requested variable.
        # 5. No instance specified for repeating form: In this case, if the requested field is in the
        # same form as the variable from which it was requested, REDCap will consistently retrieve 
        # the current instance. However, if the requested field is in a different form from the variable
        # from which it was requested, REDCap will instead retrieve the first instance of the field for
        # which there is an entry. This behaviour is undesired, so a warning should be raised in such
        # cases.
        if (arg["instance"] != None): # if an instance was specified
            if form_repetition_map[arg["form_name"]]["indep_repeat"]: # if form is independently repeating
#                event_field_instance_valid = True
                pass
            else: # if form is non-repeating
#                event_field_instance_valid = False
                #error_msg = "BRANCHING LOGIC ERROR: A repeat instance of the variable '"+arg["field_name"]+"' in form '"+arg["form_name"]+"' was specified, but the form is not repeating."
                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies a repeat instance of the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', but the form is non-repeating."
                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
        else: # if no instance specified
            if form_repetition_map[arg["form_name"]]["indep_repeat"]: # if form is independently repeating
                if (arg["form_name"] == metadata_without_branching_logic[field_name].form_name): # if calling field and requested field are in same form
#                    event_field_instance_valid = True
                    pass
                else: # if calling field and requested field are in different forms
#                    event_field_instance_valid = False
                    error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which refers to an unspecified instance of the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', which is independently repeating. REDCap cannot handle branching logic which refers to an unspecified instance of an independently repeating field in a different form."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
            else: # if form is nonrepeating
#                event_field_instance_valid = True
                pass
    else: # if longitudinal and repeating
        # Things to check here:
        # 1. Event specified does not exist: HANDLE HERE; only needs to be checked for non-repeating fields.
        # 2. Specified event does not include variable: HANDLE HERE; only needs to be checked for non-repeating fields.
        # 3. Cannot have [ev][var][rep]
        # 4. If event specified, must be non-repeating form; check for repeating form with event specified.
        # 5. If IR form, must either specify instance, or must refer to variable within current form.
        # 6. For NR, IR, DR forms, if no event is specified, check that all events containing current 
        # field also contain the requested variable.
        # 7. If an instance is specified, check that the field is repeating in all forms from which it 
        # will be called. 

        # Check that an event and instance are not specified; raise warning if so.
        if (arg["event"] != None) and (arg["instance"] != None):
#            event_field_instance_valid = False
            #print "BRANCHING LOGIC ERROR: Event and instance specified in branching logic for field '"+field_name+"'. REDCap cannot properly handle branching logic with both an event and instance specified."
            error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies both an event and a repeat instance of the field '"+arg["field_name"]+"'. REDCap cannot handle branching logic which specifies both an event and an instance of a field."
            metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
        else: # If arg not of form [ev][var][rep]
            # Check if an event was specified. If so, check that the field is non-repeating in that event.
            if (arg["event"] != None):
                # Check that specified event is valid
                if doesEventExist(arg["event"], events):
                    # Check that the specified event contains the field.
                    if doesEventContainField(arg["event"], arg["field_name"], metadata_without_branching_logic):
                        # Check if the field is non-repeating in the specified event.
                        if (arg["event"] in form_repetition_map[arg["form_name"]]["events_non_repeat"]):
#                            event_field_instance_valid = True
                            pass
                        else: # if field is repeating in specified event
#                            event_field_instance_valid = False
                            error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies the event '"+arg["event"]+"' for the field '"+arg["field_name"]+"' in the form '"+arg["form_name"]+"', which is repeating in the requested event. REDCap cannot handle branching logic in which an event is specified for a form which is repeating in the specified event."
                            metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                            #print "BRANCHING LOGIC ERROR: The field '"+field_name+"' has branching logic which specifies an event for the field '"+arg["field_name"]+"' which is repeating in the requested event. REDCap cannot handle branching logic in which an event is specified for a form which is repeating in the specified event."
                    else: # if specified event does not contain field
#                        event_field_instance_valid = False
                        error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies the event '"+arg["event"]+"' for the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', but the event does not include the field."
                        metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                else: # if specified event does not exist
#                    event_field_instance_valid = False
                    error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies the event '"+arg["event"]+"', but the event does not exist."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
            else: # if no event specified
                # Loop through all events containing the field whose branching logic
                # is being parsed currently. For each of these events, check that the
                # event from which the branching logic will be called contains the 
                # requested variable.
                # if instance specified:
                #     NR: cannot be NR if instance specified
                #     IR: okay
                #     DR: okay
                # if no instance specified:
                #     NR: okay
                #     IR: required field must be in same form as calling field.
                #     DR: okay
                for event in metadata_without_branching_logic[field_name].events_containing_field:
                    # All events in these lists must be valid as they are gotten from
                    # REDCap itself.
                    # Check that the events from which the field is requested contains
                    # the requested field.
                    if doesEventContainField(event, arg["field_name"], metadata_without_branching_logic):
                        if (arg["instance"] != None): # if instance specified.
                            # determine if requested field is NR, IR, or DR in the
                            # current event.
                            arg_frm = form_repetition_map[arg["form_name"]]
                            if (event in arg_frm["events_non_repeat"]): # if field is non-repeating in calling event
#                                event_field_instance_valid = False
                                #print "BRANCHING LOGIC ERROR: The field '"+field_name+"' has branching logic which refers to a repeat instance of the field '"+arg["field_name"]+"', but the field is non-repeating in event '"+event+"'."
                                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which specifies a repeat instance of the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', but the form is non-repeating in the event '"+event+"'."
                                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                            elif (event in arg_frm["events_indep_repeat"]): # if field is independently repeating in calling event
#                                event_field_instance_valid = True # Can specify instance of IR field within events.
                                pass
                            elif (event in arg_frm["events_dep_repeat"]): # if field is dependently repeating in calling event
#                                event_field_instance_valid = True # Can specify instance of DR field within events.
                                pass
                        else: # if no instance specified
                            # determine if requested field is NR, IR, or DR in the
                            # current event.
                            arg_frm = form_repetition_map[arg["form_name"]]
                            if (event in arg_frm["events_non_repeat"]): # if field is non-repeating in calling event
#                                event_field_instance_valid = True
                                pass
                            elif (event in arg_frm["events_indep_repeat"]): # if field is independently repeating in calling event
                                if (arg["form_name"] == metadata_without_branching_logic[field_name].form_name): # if calling field and requested fields lie in same form
#                                    event_field_instance_valid = True # Can refer to same instance of IR field within event if calling and requested fields lie in same form
                                    pass
                                else: # if calling field and requested field lie in different forms
#                                    event_field_instance_valid = False
                                    #print "BRANCHING LOGIC ERROR: The field '"+field_name+"' in form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which refers to an unspecified instance of the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', which is independently repeating in the event '"+event+"'. REDCap cannot handle branching logic which refers to an unspecified instance of an independently repeating field in a different form."
                                    error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which refers to an unspecified instance of the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"', which is independently repeating in the event '"+event+"'. REDCap cannot handle branching logic which refers to an unspecified instance of an independently repeating field in a different form."
                                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                            elif (event in arg_frm["events_dep_repeat"]): # if field is dependently repeating in calling event
#                                event_field_instance_valid = True # Can refer to same instance of DR field within event by not specifying instance.
                                pass
                    else: # if field is requested from an event which does not contain the field.
#                        event_field_instance_valid = False
                        error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which calls the field '"+arg["field_name"]+"' in form '"+arg["form_name"]+"' without specifying an event from the event '"+event+"', but the event does not include the field."
                        metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
    return # event_field_instance_valid

def getFieldName(string):  
    '''Converts "field(2)" to "field___2".'''
    if ("(" in string): # if checkbox field
        field_name = string.split("(")[0]+"___"+string.split("(")[1].rstrip(")")
    else: # if not checkbox field
        field_name = string
    return field_name

def getArgType(arg_field_name, metadata_without_branching_logic):
    '''Get type of the argument (e.g. date_ymd, integer, number etc.) in the branching logic.'''
    validation_type = metadata_without_branching_logic[arg_field_name].text_validation_type.strip()
    if (validation_type == ""):
        validation_type = None
    return validation_type

def handleFieldBox(arg, metadata_without_branching_logic):
    '''Interpret field notation of the form [var]'''
    arg["event"] = None
    arg["field_name"] = getFieldName(arg["token"].lstrip("[").rstrip("]"))
    if doesFieldExist(arg["field_name"], metadata_without_branching_logic):
        arg["field_name_valid"] = True
        arg["form_name"] = metadata_without_branching_logic[arg["field_name"]].form_name
        arg["instance"] = None
    else:
        arg["field_name_valid"] = False
    return arg

def handleEventFieldBox(arg, events, metadata_without_branching_logic):
    '''Interpret field notation of the form [event_arm][var]'''
    arg["event"] = arg["token"].split("]")[0].lstrip("[")
    arg["field_name"] = getFieldName(arg["token"].split("]")[1].lstrip("["))
    if doesFieldExist(arg["field_name"], metadata_without_branching_logic):
        arg["field_name_valid"] = True
        arg["form_name"] = metadata_without_branching_logic[arg["field_name"]].form_name
        arg["instance"] = None
    else:
        arg["field_name_valid"] = False
    return arg

def handleFieldInstanceBox(arg, metadata_without_branching_logic):
    '''Interpret field notation of the form [var][instance]'''
    arg["event"] = None
    arg["field_name"] = getFieldName(arg["token"].split("]")[0].lstrip("["))
    if doesFieldExist(arg["field_name"], metadata_without_branching_logic):
        arg["field_name_valid"] = True
        arg["form_name"] = metadata_without_branching_logic[arg["field_name"]].form_name
        arg["instance"] = int(arg["token"].split("]")[1].lstrip("["))
    else:
        arg["field_name_valid"] = False
    return arg

def handleEventFieldInstanceBox(arg, events, metadata_without_branching_logic):
    '''Interpret field notation of the form [event_arm][var][instance]'''
    arg["event"] = arg["token"].split("]")[0].lstrip("[")
    arg["field_name"] = getFieldName(arg["token"].split("]")[1].lstrip("["))
    if doesFieldExist(arg["field_name"], metadata_without_branching_logic):
        arg["field_name_valid"] = True
        arg["form_name"] = metadata_without_branching_logic[arg["field_name"]].form_name
        arg["instance"] = int(arg["token"].split("]")[2].lstrip("["))
    else:
        arg["field_name_valid"] = False
    return arg

def writeBranchingLogicFunction(def_field, project_longitudinal, project_repeating, events, form_repetition_map, metadata_without_branching_logic, field_name, branching_logic_string):
    """This function converts a branching logic string (e.g. [var2] = '1') and
    converts it into a Python function."""

    if (branching_logic_string.strip() == ""): # if there is no branching logic
        branching_logic = None
    else:
        # Assume branching logic is valid until a mistake is found.
        branching_logic_valid = True

        # Tokenize the branching logic string.
        tokens = tokenizeBranchingLogic(branching_logic_string)

        # Translate the tokens into REDCap readable tokens.
        translated_tokens = translateTokens(tokens)

#        print 'translated_tokens:', translated_tokens

        # Define list of tokens which are operators: 
        # SHOULD BE DEFINED ELSEWHERE ONCE AND FOR ALL TO AVOID DISCREPANCIES.
        operators = ["==", "!=", "<", ">", "<=", ">=", " and ", " or ", ")", "(", "+", "-", "*", "/"]
        operators_disallowed = ["+", "-", "*", "/"] # Arithmetic found to not work well in branching logic. Raise warnings if these are used.
        operators_disallowed.append("!") # Can't handle logic of the type !([field1] = '1' and [field2]='2')
        
        # Identify the arguments of the branching logic function:
        args = []
        for token in translated_tokens:
            if "[" in token:
                arg = {}
                arg["token"] = token
                args.append(arg)

#        print 'args:', args

        # Check for smart variables and quit if any are found.
        for arg_index in range(len(args)):
            arg = args[arg_index]
            if ("-" in arg["token"]): # All smart variables seem to contain dashes.
                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which appears to contain a Smart Variable. This quality control script cannot currently interpret Smart Variables."
                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                branching_logic_valid = False

        # Check for arithmetic operators (and others) which are known to malfunction in branching logic.
        for token in translated_tokens:
            if token in operators_disallowed:
                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which uses arithmetic operations, or uses logic of the form ![field]='1'. These are not handled by this script."
                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                branching_logic_valid = False
                break
                
        # Interpret each argument as [event][variable(checkbox)][instance]
        if (not project_repeating) and (not project_longitudinal):
            # Handle 1 box corresponding to the field name.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                box_count = arg["token"].count("[")
                if (box_count > 1):
                    # Handle invalid count of boxes.
                    branching_logic_valid = False
                    error_msg = "ERROR IN BRANCHING LOGIC: Invalid box count for field '"+field_name+"'."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)
                args[arg_index] = handleFieldBox(arg, metadata_without_branching_logic)

        elif (project_repeating) and (not project_longitudinal):
            # Handle up to 2 boxes.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                box_count = arg["token"].count("[")
                if (box_count == 1): # if [var]
                    args[arg_index] = handleFieldBox(arg, metadata_without_branching_logic)
                elif (box_count == 2): # if [var][instance]
                    args[arg_index] = handleFieldInstanceBox(arg, metadata_without_branching_logic)
                else:
                    # Handle invalid count of boxes.
                    branching_logic_valid = False
                    #print "BRANCHING LOGIC ERROR: Invalid box count for field '"+field_name+"'."
                    error_msg = "ERROR IN BRANCHING LOGIC: Invalid box count for field '"+field_name+"'."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)

        elif (not project_repeating) and (project_longitudinal):
            # Handle up to 2 boxes.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                box_count = arg["token"].count("[")
                if (box_count == 1): # if [var]
                    args[arg_index] = handleFieldBox(arg, metadata_without_branching_logic)
                elif (box_count == 2): # if [event_arm][var]
                    args[arg_index] = handleEventFieldBox(arg, events, metadata_without_branching_logic)
                else:
                    # Handle invalid count of boxes.
                    branching_logic_valid = False
                    #print "BRANCHING LOGIC ERROR: Invalid box count for field '"+field_name+"'."
                    error_msg = "ERROR IN BRANCHING LOGIC: Invalid box count for field '"+field_name+"'."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)

        else: # If repeating and longitudinal
            # Handle up to 3 boxes.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                box_count = arg["token"].count("[")
                if (box_count == 1): # if [var]
                    args[arg_index] = handleFieldBox(arg, metadata_without_branching_logic)
                elif (box_count == 2): # if [event_arm][var] or [var][instance]
                    # Determine whether an event was specified
                    try: 
                        int(arg["token"].split("]")[1].lstrip("[")) # if [var][instance]; check by attempting to convert second box to int.
                        args[arg_index] = handleFieldInstanceBox(arg, metadata_without_branching_logic)
                    except ValueError: # if [event_arm][var]
                        args[arg_index] = handleEventFieldBox(arg, events, metadata_without_branching_logic)
                elif (box_count == 3):
                    # This case should be valid, but REDCap cannot handle it consistently, so an
                    # error is raised by isEventFieldInstanceValidBL(). This part of the code is 
                    # retained in case REDCap functionality is improved to handle this case.
                    args[arg_index] = handleEventFieldInstanceBox(arg, events, metadata_without_branching_logic)
                else:
                    # Handle invalid count of boxes (e.g. [ev][var][instance][nonsense]
                    branching_logic_valid = False
                    #print "BRANCHING LOGIC ERROR: Invalid box count for field '"+field_name+"'."
                    error_msg = "ERROR IN BRANCHING LOGIC: Invalid box count for field '"+field_name+"'."
                    metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)

        # Determine if (event, field, instance) specified in the branching logic is 
        # valid. If problems are found, error messages are added to the list of 
        # branching logic errors. Later, an empty error list indicates that the 
        # branching logic is considered valid.
        for arg in args:
            if arg["field_name_valid"]: # if the arg's field name is invalid, other checks cannot be performed
                isEventFieldInstanceValidBL(arg, field_name, project_longitudinal, project_repeating, form_repetition_map, events, metadata_without_branching_logic)
            else:
                error_msg = "ERROR IN BRANCHING LOGIC: The field '"+field_name+"' in the form '"+metadata_without_branching_logic[field_name].form_name+"' has branching logic which requests the field '"+arg["field_name"]+"', but the requested field does not exist."
                metadata_without_branching_logic[field_name].branching_logic_errors.append(error_msg)

        if (len(metadata_without_branching_logic[field_name].branching_logic_errors) == 0): # if no branching logic errors found
            branching_logic_valid = True
        else:
            branching_logic_valid = False

        if branching_logic_valid: # Only attempt to write a function for the branching logic if it is valid.
            # Determine the argument type and add to arg.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                args[arg_index]["type"] = getArgType(arg["field_name"], metadata_without_branching_logic)
    
            # Write a function for the branching logic. 
            indent = "    "
            end = "\n"
            function_string = "def branchingLogic(row, form_repetition_map, records, record_id_map):"+end
    
            # Find the required row for each argument. Invalid branching logic arguments will be 
            # prevented from entering these functions by isEventFieldInstanceValidBL() above.
            for arg_index in range(len(args)):
                arg = args[arg_index]
                if (not project_longitudinal) and (not project_repeating):
                    # Look in same row of records as record being checked.
                    function_string += indent+"arg"+str(arg_index)+" = records[row]['"+arg["field_name"]+"']"+end
                elif (project_longitudinal) and (not project_repeating):
                    if (arg["event"] == None): # if no event specified
                        # Look in same row (i.e. in same event) of records as record being checked. Warnings will have been raised already where needed.
                        function_string += indent+"arg"+str(arg_index)+" = records[row]['"+arg["field_name"]+"']"+end
                    else: # if event specified
                        function_string += indent+"arg"+str(arg_index)+" = getEventField(row, "+(str(arg["event"]) if arg["event"] == None else "'"+str(arg["event"])+"'")+", '"+str(arg["field_name"])+"', '"+str(def_field)+"', records, record_id_map)"+end
                elif (not project_longitudinal) and (project_repeating):
                    function_string += indent+"arg"+str(arg_index)+" = getFieldInstance(row, '"+str(arg["field_name"])+"', '"+str(arg["form_name"])+"', "+str(arg["instance"])+", '"+str(def_field)+"', form_repetition_map, records, record_id_map)"+end
                elif (project_longitudinal) and (project_repeating):
                    function_string += indent+"arg"+str(arg_index)+" = getEventFieldInstance(row, "+(str(arg["event"]) if arg["event"] == None else "'"+str(arg["event"])+"'")+", '"+str(arg["field_name"])+"', '"+str(arg["form_name"])+"', "+str(arg["instance"])+", '"+str(def_field)+"', form_repetition_map, records, record_id_map)"+end
                
            # Add the logical test to the function string.
            function_string += indent+"return "
            arg_number = 0 # Add the first argument first.
            for token_index in range(len(translated_tokens)):
                arg = args[arg_number]
                token = translated_tokens[token_index]
                if "[" in token:
                    if (arg["type"] == "number"):
                        function_string += "(0 if arg"+str(arg_number)+" == '' else float(arg"+str(arg_number)+"))"
                        last_var_type = arg["type"]
                    elif (arg["type"] == "integer"):
                        function_string += "(0 if arg"+str(arg_number)+" == '' else int(arg"+str(arg_number)+"))"
                        last_var_type = arg["type"]
                    else:
                        function_string += "arg"+str(arg_number)
                        last_var_type = arg["type"]
                    if arg_number < len(args) - 1:
                        arg_number += 1
                else: # Use last variable type to interpret what the number/string should be interpreted as.
                    #if token == " ": # SHOULDN'T HAPPEN IN THE FIRST PLACE. FIX TOKENIZER. SEEMS TO ONLY HAPPEN TO INTEGERS/NUMBERS.
                    #    continue
                    if token in operators: # Prevent conversion of (, ==, > etc. to float/int.
                        function_string += token
                    elif (last_var_type == "number"):
                        function_string += "float("+token+")"
                    elif (last_var_type == "integer"):
                        function_string += "int("+token+")"
                    else:
                        function_string += token
#            print "Field          :", field_name
#            print "Branching logic:", branching_logic_string
#            print function_string
#            print

            exec function_string
    
            # Assign the written function to a the variable 'branching_logic'.
            branching_logic = branchingLogic
        else: # if branching logic is not valid
            branching_logic = None

            # Print branchign logic errors. 
            # PRINT ONLY ERROR MESSAGES FOR FIRST OPTION IN CHECKBOX FIELDS; THIS COULD BE IMPROVED
            # LATER WHEN THE CREATION OF CHECKBOX FIELD INSTANCES IS IMPROVED.
            print_error_list = False
            if (metadata_without_branching_logic[field_name].field_type != "checkbox"):
                print_error_list = True
            elif (field_name == metadata_without_branching_logic[field_name].choices[0]):
                print_error_list = True
            if print_error_list:
                print "Field          :", field_name.split("___")[0]
                print "Branching logic:", branching_logic_string
                for error_msg in metadata_without_branching_logic[field_name].branching_logic_errors:
                    print error_msg
                print Color.red + "ERRORS IN BRANCHING LOGIC: The branching logic for field '"+field_name.split("___")[0]+"' is invalid, or is not handled by this script. The branching logic function for this field will always return True." + Color.end
                print                
    return branching_logic
