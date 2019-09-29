"""The purpose of parse_metadata() is to take the raw data dictionary and extract from it the
information about each variable in a form that is useful in Python. For example, Boolean values
stored as 'y' or '' in a REDCap data dictionary are converted to Python bool's True or False."""

import sys
from copy import deepcopy
from collections import OrderedDict

from Field import Field
from writeBranchingLogicFunction import writeBranchingLogicFunction

def parseBool(str):
    if ('y' in str):
        return True
    else:
        return False

def parseMinMax(string, text_validation_type):
    """This function takes a string in the min/max field of the data dictionary and converts it into a 
    numeric value. If the field is empty or otherwise cannot be converted into a number, None is
    returned."""
    if (string == None) or (string.strip() == ""): # IMPROVE ERROR HANDLING FOR BAD OR WHITESPACE FIELDS.
        minmax = None
    else:
        if (text_validation_type.strip() == "time"):
            if (string.count(":") != 1) or (len(string.strip()) != 5):
                print "Invalid format of text validation of type 'time':", string
                sys.exit()
            minmax = int(string.replace(":","")) # It seems impossible to input a time in the wrong format.
        else:
            minmax = float(string)
    return minmax

def parseFormEventMapping(form_name, form_event_mapping): # SHOULD FIND EVENTS FOR EACH FORM FIRST FOR 'BETTER' PERFORMANCE.
    events_containing_field = []
    for event in form_event_mapping:
        if (event["form"] == form_name): # If the form is completed for this event.
            events_containing_field.append(event["unique_event_name"])
    return events_containing_field

def parseBranchingLogic(def_field, project_longitudinal, project_repeating, events, metadata_without_branching_logic, form_event_mapping, repeating_forms_events, form_repetition_map):
    """This function is used to write a branching logic function for each field. This
    must be done after information about all the fields is known."""

    # * IDEALLY, THE BRANCHING LOGIC FUNCTION CREATED IN THIS SCRIPT COULD BE BASED ON THE SOURCE CODE FOR THE REDCAP SERVER, ELIMIATING ANY QUESTION
    # OF WHETHER THE FUNCTION DEFINED HERE DOES THE SAME THING AS REDCAP, AND INCORPORATING THE BUGS IN THE REDCAP BRANCHING LOGIC INTO THIS SCRIPT.

#    metadata = {}
    metadata = OrderedDict()  # Same as dict but order items are added is retained.

    # ADD FEATURE TO ONLY PARSE ONCE FOR CHECKBOX FIELDS AND ADD LATER.
    for field_name, field in metadata_without_branching_logic.iteritems():
        branching_logic_string = field.branching_logic
        field.branching_logic = writeBranchingLogicFunction(def_field, project_longitudinal, project_repeating, events, form_repetition_map, metadata_without_branching_logic, field_name, branching_logic_string)
        metadata[field_name] = field
    return metadata

def parseMetadata(def_field, project_info, project_longitudinal, project_repeating, events, metadata, form_event_mapping, repeating_forms_events, forms, form_repetition_map, write_branching_logic_function=True):
    """Main driver for parsing the information stored in the metadata. This routine parses all of the 
    information in the data dictionary except for the branching logic, because parsing the branching
    logic currently requires that other information in the data dictionary already be parsed.

    The metadata return by PyCap is a list of fields. Since the fields are uniquely determined by
    their field names, it makes sense to convert this list to a dictioary of fields with the field names
    as keys. This will save many loops over all fields to, e.g., find a specific field name."""

#    metadata_without_branching_logic = {} # list of 'Field' objects. 
    metadata_without_branching_logic = OrderedDict() # Same as dict but order items are added is retained.

    # Loop through unparsed metadata, creating and instance of the 'Field' object for each field.
    for field_index in range(len(metadata)):

        # Load row from raw data dictionary to be parsed.
        field_raw = metadata[field_index] 

        # If field type is "descriptive", exclude if from metadata_without_branching_logic.
        if (field_raw["field_type"] == "descriptive"):
            continue

        # Interpret information in data dictionary.
        field_name           = field_raw["field_name"] # Will be dict key (not Field attribute)

        form_name            = field_raw["form_name"]
        field_type           = field_raw["field_type"]
        field_label          = field_raw["field_label"]
        choices              = field_raw["select_choices_or_calculations"]
        text_validation_type = field_raw["text_validation_type_or_show_slider_number"]
        text_validation_min  = parseMinMax(field_raw["text_validation_min"],text_validation_type)
        text_validation_max  = parseMinMax(field_raw["text_validation_max"],text_validation_type)
        identifier           = parseBool(field_raw["identifier"])
        branching_logic      = field_raw["branching_logic"]
        required_field       = parseBool(field_raw["required_field"])
        matrix_group_name    = field_raw["matrix_group_name"]
        matrix_ranking       = parseBool(field_raw["matrix_ranking"])
        field_annotation     = field_raw["field_annotation"]

        # Add empty list to store branching logic errors:
        branching_logic_errors = []
        
        # Interpret information in instrument-event mapping.
        if (project_longitudinal):
            events_containing_field = parseFormEventMapping(form_name, form_event_mapping) # For which events is this variable filled.
        else:
            events_containing_field = None

        # Interpret information in repeating instruments events.

        # Choices string to a list of choices for radio buttons (do for checkboxes separately elsewhere).
        # * PUT THIS IN A SEPARATE FUNCTION
        if (field_type in ['radio', 'dropdown', 'checkbox']): 
            num_options = choices.count('|') + 1
            choices_dictionary = {} # dict mapping the choice index to the choice text for each option.
            for index in range(num_options):
                choice_number = choices.split('|')[index].split(",")[0].strip()
                choice_text_split_by_commas = choices.split('|')[index].split(",")[1:]
                choice_text = ','.join(choice_text_split_by_commas).strip()
                choices_dictionary[choice_number] = choice_text
        elif (field_type == 'yesno'):
            choices_dictionary = {u'0':u'No', u'1':u'Yes'}
        elif (field_type == 'truefalse'):
            choices_dictionary = {u'0':u'False', u'1':u'True'}            
        else:
            choices_dictionary = None
            
        # If field is multiple choice (checkbox), add a variable for each option.
        #
        # This step is necessary because if a checkbox is defined with variable name
        # "foo" and choices "1, cat | 2, dog | 3, mouse", REDCap will convert this to 
        # three variables named "foo___1", "foo___2", and "foo___3", each of which 
        # store a 0 or 1. 
        #
        # To get the correct name, the following bit of code parses the choices specified in the 
        # data dictionary. This parse method should work provided that none of the choices include
        # the pipe '|' character, and the choice labels are only single characters (IMPROVE)
        #
        if (field_type == "checkbox"): # choices attribute is a list of variable names for the other checkbox option variable names
            num_options = choices.count('|') + 1
            choice_list = []
            for index in range(num_options):
                checkbox_number = choices.split('|')[index].split(",")[0].strip() # split by '|'; get text before first comma; strip edge whitespace.
                checkbox_field_name = field_name+u"___"+unicode(checkbox_number)
                choice_list.append(checkbox_field_name)

            for index in range(num_options):
                checkbox_field_name = choice_list[index]
                
                # Instead of keeping the full list of choices, keep only a list of the checkbox numbers.
                choices = choice_list
                
                # Add each individual checkbox as a field in metadata_without_branching_logic.
                # THE PROBLEM HERE IS THAT WHILE EACH CHECKBOX GETS IT'S OWN MEMORY ADDRESS FOR ITS
                # FIELD INSTANCE, THE CONTENTS OF THESE DIFFERENT FIELD INSTANCES REFER TO THE SAME 
                # MEMORY ADDRESSES. E.g. 'var___1' AND 'var___2' HAVE DIFFERENT MEMORY ADDRESSES,
                # BUT IF YOU CHANGE var___1.branching_logic_errors, YOU ARE ALSO CHANGING 
                # var___2.branching_logic_errors. THIS PROBLEM IS FIXED FOR NOW BY DEEPCOPYING 
                # ALL OF THE ATTRIBUTES IN THE CLASS BEFORE DEFINING EACH CHECKBOX'S Field INSTANCE.
                
                form_name = deepcopy(form_name)
                field_type = deepcopy(field_type)
                field_label = deepcopy(field_label)
                choices = deepcopy(choices)
                text_validation_type = deepcopy(text_validation_type)
                text_validation_min = deepcopy(text_validation_min)
                text_validation_max = deepcopy(text_validation_max)
                identifier = deepcopy(identifier)
                branching_logic = deepcopy(branching_logic)
                required_field = deepcopy(required_field)
                matrix_group_name = deepcopy(matrix_group_name)
                matrix_ranking = deepcopy(matrix_ranking)
                field_annotation = deepcopy(field_annotation)
                branching_logic_errors = deepcopy(branching_logic_errors)
                events_containing_field = deepcopy(events_containing_field)

                metadata_without_branching_logic[checkbox_field_name] = Field(form_name, field_type, field_label, choices, text_validation_type, text_validation_min, text_validation_max, identifier, branching_logic, required_field, matrix_group_name, matrix_ranking, field_annotation, branching_logic_errors, events_containing_field, choices_dictionary)
                
        else:
            # Add field to metadata_without_branching_logic.            
            metadata_without_branching_logic[field_name] = Field(form_name, field_type, field_label, choices, text_validation_type, text_validation_min, text_validation_max, identifier, branching_logic, required_field, matrix_group_name, matrix_ranking, field_annotation, branching_logic_errors, events_containing_field, choices_dictionary)

    # Write a branching logic function for each field.
    if write_branching_logic_function:
        metadata = parseBranchingLogic(def_field, project_longitudinal, project_repeating, events, metadata_without_branching_logic, form_event_mapping, repeating_forms_events, form_repetition_map)
    else:
        metadata = metadata_without_branching_logic

    return metadata
