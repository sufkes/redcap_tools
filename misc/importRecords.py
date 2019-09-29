# Standard modules
import os, sys
import math
import csv
import StringIO
import copy
from collections import OrderedDict

# Non-standard modules
import redcap
#import pandas

# My modules in current directory
from exportProjectInfo import exportProjectInfo
from exportRecords import exportRecords

# My modules in other directories
sufkes_git_repo_dir = "/Users/steven ufkes/scripts" # change this to the path to which the sufkes Git repository was cloned.
sys.path.append(os.path.join(sufkes_git_repo_dir, "misc"))
from Color import Color
from Timer import Timer

def recordsToDict(records, primary_key):
    """
    Parameters:
        records is a list of dicts, where each dict has the same set of keys.
        primary_key is a list or tuple of keys used in each dict in records. 
    Returns:
        records_dict: a collections.OrderedDict object. Each row in records is mapped to an entry in records_dict; the key for each entry is tuple of values taken from each row for the keys specified in primary key. The value is a dict of all fields except those in the primary key and the redcap_data_access_group field.
    """
    records_dict = OrderedDict()
    for row in records:
        key = tuple(unicode(row[field]) for field in primary_key) # value of primary key (e.g. (id, event, repeat instrument, repeat instance)) for current row.
#        for field_name in primary_key+['redcap_data_access_group']:
#            del row[field_name] # this mutates the real records_src. (bad)
#        records_dict[key] = row
        records_dict[key] = {k:v for k,v in row.iteritems() if (not k in primary_key+['redcap_data_access_group'])}
    return records_dict

def verifyChanges(api_url, api_key, records_src, def_field, project_info, overwrite):
    """
    Parameters:
        api_url: API URL of project to be modified
        api_key: API token of project to be modified
        records_src: data to be imported
        def_field: string; the name of the record ID field in the project to be modified.
        project_info: project_info of project to be modified.
        overwrite: Boolean; whether to overwrite existing data with blanks present in records_src.
    Prints summary of the changes that will be made to the destination project.
    Returns True if user confirms changes, False if not.
    """
    
    print "Comparing source data with destination database. Please review the changes below and confirm."
    print "DEBUG WARNING: Comparing strings after stripping whitespace from the start and end of the string."

    t_export = Timer('Export data from destination project for comparison')
    records_dst = exportRecords(api_url, api_key) # Export all data from destination project.
    # records_dst has type: list(dict(unicode:unicode))
    t_export.stop()

    ## Convert records to dict of dicts (from list of dicts).
    # Determine what the primary key is, depending on the project settings.
    primary_key = [def_field]
    if (project_info['is_longitudinal']):
        primary_key.append('redcap_event_name')
    if (project_info['has_repeating_instruments_or_events']):
        primary_key.extend(['redcap_repeat_instrument', 'redcap_repeat_instance'])

    # Convert records from list of (Ordered) dicts to OrderedDict of (Ordered) dicts. The keys in the outermost OrderedDict are built from the values of the fields in primary_key.
    t_dictize = Timer('Convert records to type OrderedDict')
    records_dict_src = recordsToDict(records_src, primary_key)
    records_dict_dst = recordsToDict(records_dst, primary_key)
    t_dictize.stop()

    ## Compare the source data with the destination data.
    t_compare = Timer('Compare source and destination data')
    changes_dict = OrderedDict() # Stores (old_val, new_val)
    for key, row_src in records_dict_src.iteritems():
        if key in records_dict_dst:
            row_dst = records_dict_dst[key]
        else:
            row_dst = None
        for field_name in row_src:
            val_src = row_src[field_name]
#            val_src = val_src.decode('utf-8') # convert str to unicode for comparison with records_dst (which is converted to unicode on export since format='json').
            if (row_dst != None):
                val_dst = row_dst[field_name]
            else:
                val_dst = None
            if (strip(val_src) != strip(val_dst)):
                changes_dict[key] = OrderedDict() # Each row is an OrderedDict()
                changes_dict[key]['src'] = val_src
                changes_dict[key]['dst'] = val_dst
                if (val_src != ''):
                    print key, field_name
                    if (val_dst != None): # if change is existent -> nonblank
                        print "'"+val_dst+"'"
                    else: # if change is nonexistent -> nonblank
                        print "None"
                    print ">"
                    print "'"+val_src+"'"
                elif (overwrite == 'overwrite') and (val_dst != None): # if change is non-blank -> blank, and overwrite option is selected
                    print key, field_name
                    print "'"+val_dst+"'"
                    print ">"
                    print "''"
#                print type(val_src), ">", type(val_dst)
                print

    # SAVE changes_dict
#    print "DEBUG: Saving changes_dict to changes.pkl pickle file."
#    import pickle
#    with open('changes.pkl','wb') as ff:
#        pickle.dump(changes_dict, ff)
    t_compare.stop()

    cont = bool(raw_input("These changes will be made to the database. Continue y/[n]? ") == 'y')
    return cont

def importRecords(api_url, api_key, records_src, overwrite='normal', format='json', quick=False, return_content='ids', size_thres=40000): # size_thres = 300000 has not caused error [2019-05-08 ACTUALLY, MAYBE IT HAS]
    # Load project.
    project = redcap.Project(api_url, api_key)
    project_info = exportProjectInfo(api_url, api_key)
    
    # Ask for user confirmation before proceeding.
    print "Data will be imported to the following project:"
    print "-------------------------------------------------------------------------------------------------"
    print "Project Title: "+Color.blue+project_info["project_title"]+Color.end
    print "Project ID   : "+Color.blue+str(project_info["project_id"])+Color.end
    print "-------------------------------------------------------------------------------------------------"
    cont = bool(raw_input("Please verify that this is project you wish to modify. Continue y/[n]? ") == 'y')
    if (not cont):
        print "Quitting"
        sys.exit()
    if (overwrite == "overwrite"):
        cont = bool(raw_input("You have selected to overwrite fields with blanks. Continue y/[n]? ") == 'y')
        if (not cont):
            print "Quitting"
            sys.exit()
    
    # If records_src is a CSV string, convert it to a list of dicts. Then proceed using the same method as for format='json'.
    if (format == 'csv'):
        reader = csv.DictReader(StringIO.StringIO(records_src))
        records_src = []
#        print 'WARNING: Not converting import data to unicode before PyCap import_records() call'
        for line in reader: # each line is a dict (csv version < 3.6) or OrderedDict (csv version >= 3.6). Convert each line to dict for consistency.
            line_dict = {key.decode('utf-8'):value.decode('utf-8') for key, value in line.iteritems()} # doesn't seem necessary to convert the keys and values to unicode; seems to work the same either way.
#            line_dict = dict(line)
            records_src.append(line_dict)

    # Compare source and destination data. Continue if user confirms changes.
    if (not quick):
        print "DEBUG: Comparing records_src before and after verification."
        records_src_copy = copy.deepcopy(records_src)
        if (not verifyChanges(api_url, api_key, records_src, project.def_field, project_info, overwrite)):
            print "Quitting"
            sys.exit()
        print "DEBUG: records_src unchanged by verifyChanges():", records_src == records_src_copy

    # Determine size of imported data. I DON'T KNOW THE APPROPRIATE WAY TO DETERMINE THE "SIZE", NOR THE SIZE LIMIT. IF IT DOESN'T WORK WITH THE CURRENT SETTING, REDUCE THE SIZE LIMIT.
    num_row = len(records_src)
    num_col = len(records_src[0])
    num_cells = num_row*num_col
    
    failure_msg = "Import appears to have failed, likely because the input data is too large. Review the logging information in REDCap online to verify import failure, and change data chunk size by adjusting 'size_thres'."

    # Import data
    if (num_cells < size_thres):
        print "Importing data in one piece"
#        return_info = project.import_records(records_src, overwrite=overwrite, format=format, return_content=return_content)

#        print "importing records as type:", type(records_src), "(", type(records_src[0]), "(", type(records_src[0][records_src[0].keys()[0]]), " ) )"

        return_info = project.import_records(records_src, overwrite=overwrite, format='json', return_content=return_content) # If format was 'csv', records_src has been converted to 'json' by this point.

        # Print information returned from REDCap.
        if (return_content == 'count'):
            try:
                num_modified = return_info["count"]
                print "Number of records imported: "+str(num_modified)
            except KeyError:
                print failure_msg
                sys.exit()
        elif (return_content == 'ids'):
            if (return_info != {}):
                print "Number of records imported: "+str(len(return_info))
                print "IDs of records imported:"
                id_string = ""
                for id in return_info:
                    id_string += id+" "
                id_string = id_string.rstrip()
                print id_string
            else:
                print failure_msg
                sys.exit()
    else:
        row_chunk_size = size_thres/num_col # Python 2 rounds down integers after division (desired)
        print "Importing data in chunks of "+str(row_chunk_size)+" rows"
        
        if (return_content == 'count'):
            num_modified = 0
        elif (return_content == 'ids'):
            ids_imported = []

        # Slice the data into chunks of size <= size_thres
        num_chunks = int(math.ceil(float(num_row)/float(row_chunk_size)))
        for chunk_index in range(num_chunks): 
            # Replace following if else block with one line -- now records_src is always a list of dicts.
            chunk = records_src[chunk_index*row_chunk_size:(chunk_index+1)*row_chunk_size]

#            print "importing records as type:", type(records_src), "(", type(records_src[0]), "(", type(records_src[0][records_src[0].keys()[0]]), " ) )"

            # Import chunk.
#            return_info = project.import_records(chunk, overwrite=overwrite, format=format, return_content=return_content)
            return_info = project.import_records(chunk, overwrite=overwrite, format='json', return_content=return_content) # if format was CSV, the CSV string has already been converted to 'json' format.

            # Combine import results for each chunk.
            if (return_content == 'count'):
                try:
                    num_modified += return_info["count"]
                except KeyError:
                    print failure_msg
                    sys.exit()
            elif (return_content == 'ids'):
                if (return_info != {}):
                    ids_imported.extend(return_info)
                else:
                    print chunk
                    print return_info
                    print failure_msg
                    sys.exit()

            completion_percentage = float(chunk_index+1)/float(num_chunks)*100.
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% complete' % (completion_percentage,))
            sys.stdout.flush()
        sys.stdout.write('\n\r')
#        sys.stdout.write('%.2f%% complete' % (float(100),))
        sys.stdout.flush()
                
        # Report import results.
        if (return_content == 'count'):
            print "Number of records imported: "+str(num_modified)
        elif (return_content == 'ids'):
            id_string = ""
            for id in ids_imported:
                id_string += id+" "
            id_string = id_string.rstrip()
            print "Number of records imported: "+str(len(ids_imported))
            print "IDs of records imported:"            
            print id_string
    return
