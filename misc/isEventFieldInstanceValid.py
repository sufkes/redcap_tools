def isEventFieldInstanceValid(project_longitudinal, project_repeating, form_repetition_map, field, row):
    # Determine if the field should be filled out for the currect row's event, instance.

    # THERE ARE 6 CASES:
    # 1. NON-LONGITUDINAL, NON-REPEATING: CHECK FIELD FOR EVERY ROW
    # 2. LONGITUDINAL, NON-REPEATING    : CHECK FIELD IN ROW IF ROW'S EVENT INCLUDES FIELD.
    # 3. NON-LONGITUDINAL, REPEATING
    #   (a) CHECK FIELD IN ROW IF ROW'S REPEATED INSTRUMENT INCLUDES FIELD.
    #   (b) CHECK FIELD IN ROW IF NO REPEAT INSTRUMENT IS SPECIFIED AND FIELD IS NON-REPEATING.

    # 4. LONGITUDINAL, REPEATING: 
    #   (a) FIELD IS NON REPEATING FOR EVENT
    #   (b) FIELD IS INDEPENDENTLY REPEATING FOR EVENT
    #   (c) ALL INSTRUMENTS IN EVENT REPEAT DEPENDENTLY

    # Some of these could be combined, but they have been left distinct for clarity and to avoid the 
    # need to handle key errors.

    if (not project_longitudinal) and (not project_repeating): # Case 1
        element_valid = True
    elif (project_longitudinal) and (not project_repeating): # Case 2
        if (row["redcap_event_name"] in field.events_containing_field): # if field is part of row's event.
            element_valid = True
        else:
            element_valid = False
    elif (not project_longitudinal) and (project_repeating): # Case 3
        if (row["redcap_repeat_instrument"] == field.form_name): # if field is in repeating instrument and current row corresponds to that instrument
            element_valid = True
        elif (row["redcap_repeat_instrument"] == ""): # if row does not correspond to a repeating form
            if (form_repetition_map[field.form_name]["indep_repeat"]): # if field's form repeats independently
                element_valid = False
            else: # if field's form does not repeat
                element_valid = True 
        else: # if row corresponds to a different repeating form
            element_valid = False
    else: # Case 4
        if (row["redcap_event_name"] in field.events_containing_field): # if row corresponds to event which includes field's form.
            # Handle 3 cases 
            if (row["redcap_repeat_instance"] != ""): # if row corresponds to a repeat instance (dependent or independent).
                if (row["redcap_repeat_instrument"] == field.form_name): # if row corresponds to the independently repeating instrument containing the field
                    element_valid = True
                elif (row["redcap_repeat_instrument"] == ""): # if row corresponds to a dependently repeating event
                    element_valid = True # valid because the field is already known to be part of the current, dependently repeating event
                else: # if row corresponds to an independently repeating form which does not contain the field.
                    element_valid = False
            else: # if row does not correspond to repeating forms or events
                # if form is non-repeating in the event corresponding to this row
                if (row["redcap_event_name"] in form_repetition_map[field.form_name]["events_non_repeat"]):
                    element_valid = True
                else:
                    element_valid = False                
        else: # if row corresponds to an event which does not include field's form.
            element_valid = False
    return element_valid
