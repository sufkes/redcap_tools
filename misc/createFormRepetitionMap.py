def createFormRepetitionMap(project_longitudinal, project_repeating, form_event_mapping, repeating_forms_events, forms):
    """In longitudinal projects with repeating forms and events, a single instrument may be
    non-repeating, independtly repeating (repeats independently of other froms in the same instrument), 
    dependently repeating, or any combination of these. This complicates the determination of whether a 
    (row, field) pair in the records should be filled in or not. 

    The purpose of this function is to create a dict with form_name's as keys, and elements which
    specify the events in which the form is non-repeating, independently repeating, or dependently
    repeating. The dict also contains booleans which specify whether the form is ever non-repeating, 
    independently repeating, or dependently repeating

    Returns:
        None (if project is not repeating)
        dict: (if project is repeating)
            keys: instrument name
            values: dict:
                "non_repeat": bool, whether this instrument is non-repeating in any event
                "indep_repeat": bool, whether this is a repeating instrument in any event
                "dep_repeat": bool, whether this instrument is in a repeating event. (not present if project is not longitudinal)
                "events_non_repeat": list of events in which this instrument is non-repeating (not present if project is not longitudinal)
                "events_indep_repeat": list of events in which this is a repeating-instrument (not present if project is not longitudinal)
                "events_dep_repeat": list of repeating events containing this instrument (not present if project is not longitudinal)
    
"""

    if (not project_repeating):
        form_repetition_map = None
    elif (not project_longitudinal): # if non-longitudinal, repeating
        form_repetition_map = {}
        for form in forms: # create dict for each form
            form_repetition_map[form["instrument_name"]] = {}
        for form_name in form_repetition_map:
            form_repetition_map[form_name]["non_repeat"] = True # Assume non-repeating, check in next loop.
            form_repetition_map[form_name]["indep_repeat"] = False # Assume non-repeating, check in next loop.
            for repeater in repeating_forms_events:
                if (repeater["form_name"] == form_name): # if form is repeating
                    form_repetition_map[form_name]["non_repeat"] = False
                    form_repetition_map[form_name]["indep_repeat"] = True
                    break
    else: # if longitudinal, repeating
        form_repetition_map = {}
        for form in forms: # create dict for each form
            form_repetition_map[form["instrument_name"]] = {}
        for form_name in form_repetition_map:
            # Initialize lists of events of each repetition type.
            form_repetition_map[form_name]["events_non_repeat"] = []
            form_repetition_map[form_name]["events_indep_repeat"] = []
            form_repetition_map[form_name]["events_dep_repeat"] = []
            
            for fem_entry in form_event_mapping:
                fem_entry_event_name = fem_entry["unique_event_name"]
                fem_entry_form_name = fem_entry["form"]
                if (form_name == fem_entry_form_name):
                    # An event containing the current form has been found.
                    # Now, determine if the form is non-repeating, independently repeating, or dependently repeating.
                    found_form_event_in_rfe = False
                    for rfe_entry in repeating_forms_events:
                        if (rfe_entry["event_name"] == fem_entry_event_name):
                            if (rfe_entry["form_name"] == form_name):
                                # found an event for which this form is independently repeating
                                form_repetition_map[form_name]["events_indep_repeat"].append(fem_entry_event_name)
                                found_form_event_in_rfe = True
                                break
                            elif (rfe_entry["form_name"] == ""):
                                # found an event for which this form is dependently repeating
                                form_repetition_map[form_name]["events_dep_repeat"].append(fem_entry_event_name)
                                found_form_event_in_rfe = True
                                break
                    if (not found_form_event_in_rfe):
                        # found an event for which this form is non-repeating
                        form_repetition_map[form_name]["events_non_repeat"].append(fem_entry_event_name)
                form_repetition_map[form_name]["events"] = []# list of all events 
                form_repetition_map[form_name]["events"].extend(form_repetition_map[form_name]["events_non_repeat"])
                form_repetition_map[form_name]["events"].extend(form_repetition_map[form_name]["events_indep_repeat"])
                form_repetition_map[form_name]["events"].extend(form_repetition_map[form_name]["events_dep_repeat"])
            # Check whether current form is ever non-repeating, independently repeating, or
            # dependently repeating
            if (len(form_repetition_map[form_name]["events_non_repeat"]) > 0):
                form_repetition_map[form_name]["non_repeat"] = True
            else:
                form_repetition_map[form_name]["non_repeat"] = False
            if (len(form_repetition_map[form_name]["events_indep_repeat"]) > 0):
                form_repetition_map[form_name]["indep_repeat"] = True
            else:
                form_repetition_map[form_name]["indep_repeat"] = False
            if (len(form_repetition_map[form_name]["events_dep_repeat"]) > 0):
                form_repetition_map[form_name]["dep_repeat"] = True
            else:
                form_repetition_map[form_name]["dep_repeat"] = False
    return form_repetition_map
