import sys

def doNoneEntriesExist(records, def_field):
    """This function looks for None type entries in the records, which are usually caused by use 
    of unrecognized characters."""

    # Certain fields containing exotic characters get turned into 'None' using this export method.
    # This bit of code can at least detect this problem and then user can manually fix. 
    # Ideally, the API should be able to interpret the data as well as a manually exported csv file.
    no_none_entries = True
    for record in records:
        for field in record.keys():
            if type(record[field]) == type(None):
                print record[def_field], record['redcap_event_name'],field
                no_none_entries = False
    if (not no_none_entries):
        print
        print "The records listed above have entries with bad characters. Fix these manually and retry."

    return no_none_entries

def areFieldNamesConsistent(metadata, records):
    """This function checks that the list of field names used in the metadata is exactly the same as the
    list of field names used in the records."""
    field_names_same = True

    # Identify variable names which don't appear in records, and variables names in records which don't
    # appear in the parsed metadata.
    # This section also generates a list of field_names. These names are the variables names used in the 
    # records (e.g., for checkbox fields: var2___1, var2___2 etc.) rather than those in the data dictionary
    # (e.g., for checkbox fields: var2).

    for field_name in metadata:
        if not (field_name in records[0].keys()):
            print "bad field name: '"+field_name
            field_names_same = False
    for key in records[0].keys():
        if not (key in metadata): # 'in metadata' means 'is a key (field name) in metadata'.
            if not (key in ["redcap_event_name", "redcap_repeat_instrument", "redcap_repeat_instance", "redcap_data_access_group"]):
                print "bad key:", key
                field_names_same = False
    return field_names_same

def isProjectCompatible(metadata, records, def_field):
    """This function performs high-level checks to determine whether the project settings, metadata, and 
    records are compatible with the quality control system."""

    project_compatible = True
    if (len(records) > 0):
        if (not doNoneEntriesExist(records, def_field)):
            project_compatible = False
    
        if (not areFieldNamesConsistent(metadata, records)):
            project_compatible = False
    return project_compatible
