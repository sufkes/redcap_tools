# Standard modules
import sys
from more_itertools import unique_everseen

# Non-standard modules
import redcap

# My modules
#from labelRecords import labelRecords

def exportRecordsChunked(project, record_ids=None, events=None, fields=None, forms=None, format='json', quiet=False, chunk_size=400):
    """Function to export records for large projects. So far, this function is known to be 
    required for only for the IPSS database."""

    def chunks(l, n):
        """Yield successive n-sized chunks from list l"""
        for ii in xrange(0, len(l), n):
            if (not quiet):
                sys.stdout.write('\r')
                sys.stdout.write('%.2f%% complete' % (float(ii)/float(len(l))*1e2,))
                sys.stdout.flush()
            yield l[ii:ii+n]
        if (not quiet):
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% complete' % (float(100),))
            sys.stdout.write('\n')
            sys.stdout.flush()

    record_list = project.export_records(records=record_ids, fields=[project.def_field]) # List of [def_field, ("redcap_event_name"), (instance fields?)]
    records = [r[project.def_field] for r in record_list] # List of [def_field] for each row in records (includes duplicates)

    # records is now a list of all record IDs, with duplicate entries corresponding to events/instances.
    # Since a project.export_records(records = 'id_1') request will pull all rows for 'id_1'. 

    records = list(unique_everseen(records)) # remove duplicate record IDs.

    try:
        response = []
        if (format == "csv"):
            column_headers_written = False

        # THIS SECTION MISTAKENLY REMOVES CARRIAGE RETURNS.
        for record_chunk in chunks(records, chunk_size):
            # Export a chunk of records. Format is a csv-format string.
            chunked_response = project.export_records(records=record_chunk, events=events, fields=fields, forms=forms, export_data_access_groups=True, format=format) # includes column headers
            
#            if (format == "csv"):
#                if column_headers_written: # only write column headers for first chunk.
#                    response.extend(chunked_response.splitlines()[1:]) # remove first row of current chunk (the column headers).
#                else:
#                    response.extend(chunked_response.splitlines()) # include first row of current chunk.
#                    column_headers_written = True
#            elif (format == "json"):
#                response.extend(chunked_response)
#        if (format == "csv"):
#            response = "\n".join(response) # convert list of csv lines back into a csv.
#            response += "\n" # append newline to match format of non-chunked export.

            if (format == 'csv'):
                if (not column_headers_written):
                    # Add current chunk of data including column headers.
                    response = chunked_response
                    column_headers = response.split('\n')[0]+'\n' # string specifying column names in CSV files (include the newline character)
                    column_headers_written = True
                else:
                    # Add current chunk of data excluding column headers.
                    chunked_response = chunked_response.split(column_headers)[1] # remove column headers from chunk
                    response += chunked_response
            elif (format == "json"):
                response.extend(chunked_response)

    except RedcapError: # THIS EXCEPTION DOESN'T SEEM TO WORK PROPERLY
        msg = "Chunked export failed for chunk_size={:d}".format(chunk_size)
        raise ValueError(msg)
    else:
        return response
    return

def exportRecords(api_url, api_key, record_id_list=None, events=None, fields=None, forms=None,  format='json', quiet=False, label=False, label_overwrite=False, chunk_thres=1000000, chunk_size=400):
    """This function exports records from a project and returns a string in either csv or json format. 
    The user can select which records, events, fields, or forms to export. By default, all records, 
    events, and fields are exported. This function uses the PyCap method export_records when the size
    of data to be exported is sufficiently small to not cause errors. When the data to be exported is 
    large enough to possibly cause error, a chunked export method (slower) is used instead. The 
    maximum number of cells that will be exported before resorting to the chunked export method can be 
    set in the 'chunk_thres' parameter."""

    # Load project.
    project = redcap.Project(api_url, api_key)

    # If format='csv' and label=True, first export as json, then label, then convert to csv.
    if label:
        print "Labelling feature is currently broken. Rerun with label=False."
        sys.exit()
    if label:
        requested_format = format
        format = "json"

    # Approximate size of data to export. Export data using method appropriate for request size.
    first_col = project.export_records(records=record_id_list, fields=[project.def_field], events=events)
    try:
        first_record_id = first_col[0][project.def_field]
        project_empty = False
    except IndexError: # Catch case in which project contains no records.
        project_empty = True
        records = []
    if (not project_empty):
        num_rows = len(first_col) # number of rows in requested export.
        first_row = project.export_records(records=[first_record_id], fields=fields, forms=forms)
        num_cols = len(first_row[0]) # number of columns in requested export.
        if (not quiet):
    #        print "Number of columns to export: "+str(num_cols)
    #        print "Number of rows to export: "+str(num_rows)
    #        print "Number of cells to export (rows x columns): "+str(num_cols*num_rows)
            pass
        if (num_rows*num_cols < chunk_thres): # If number of cells requested is less than chunk_thres
            if (not quiet):
    #            print "Exporting records in one piece."
                pass
            records = project.export_records(records=record_id_list, events=events, fields=fields, forms=forms, export_data_access_groups=True, format=format)
            # type(records) = unicode
        else:
    #        chunk_size = 400  # Timing for IPSS with DAGs: (200, 308s), (300, 296s), (400, 284s, 286s, 287s, 331s), (800, 283s)
            if (not quiet):
                print "Exporting records in chunks of size", chunk_size
            records = exportRecordsChunked(project, record_ids=record_id_list, events=events, fields=fields, forms=forms, quiet=quiet, format=format, chunk_size=chunk_size)
            # type(records) = unicode
        ## NEED TO CHANGE TO ALLOW FOR LABELS WHEN ONLY CERTAIN FIELDS ARE REQUESTED.
        ## Label entries as "HIDDEN" or "INVALID" if label=True. 
        if label:
            if (not quiet):
                msg = "Replacing values with placeholders."
                if label_overwrite:
                    msg += " Overwriting fields containing data with labels."
                print msg
            if (events != None) or (fields != None) or (forms != None): # If only certain events, fields, or forms requeted.
                records_all = exportRecords(api_url, api_key, record_id_list=record_id_list, quiet=True) # Use all records with requested IDs in labelling function. Could be optimized.
                all_requested = False
            else:
                records_all = records
                all_requested = True
            records_requested = records
            records = labelRecords(api_url, api_key, records_all, records_requested, all_requested, project, requested_format, label_overwrite=label_overwrite)
    
        if (format == 'csv'):
            # type(records) = unicode
            records = records.encode('utf-8')
            # type(records) = str
    return records
