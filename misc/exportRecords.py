#!/usr/bin/env python

# Standard modules
import sys, argparse
import warnings
from more_itertools import unique_everseen

# Non-standard modules
import redcap

# My modules from current directory
from labelRecords import labelRecords
from ProgressBar import ProgressBar
from ApiSettings import ApiSettings

def exportRecordsChunked(project, record_ids=None, events=None, fields=None, forms=None, format='json', quiet=False, chunk_size=400):
    """Function to export records for large projects. So far, this function is known to be required for only for the IPSS database."""

    if (not quiet):
        p_chunk = ProgressBar("Export records " + str(chunk_size) + " rows at a time")
    
    def chunks(l, n):
        """Yield successive n-sized chunks from list l"""
        milestone = max(len(l)/2000, 1) 
        for ii in xrange(0, len(l), n):
            if (not quiet) and (ii % milestone == 0):
                #sys.stdout.write('\r')
                #sys.stdout.write('%.2f%% complete' % (float(ii)/float(len(l))*1e2,))
                #sys.stdout.flush()
                p_chunk.update(float(ii)/float(len(l)))
            yield l[ii:ii+n]
        if (not quiet):
            #sys.stdout.write('\r')
            #sys.stdout.write('%.2f%% complete' % (float(100),))
            #sys.stdout.write('\n')
            #sys.stdout.flush()
            p_chunk.stop()

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

def exportRecords(api_url, api_key, record_id_list=None, events=None, fields=None, forms=None, validate=True,  format='json', export_form_completion=False, quiet=False, label=False, label_overwrite=False, chunk_thres=1000000, chunk_size=400):
    """This function exports records from a project and returns a string in either csv or json format. 
    The user can select which records, events, fields, or forms to export. By default, all records, 
    events, and fields are exported. This function uses the PyCap method export_records when the size
    of data to be exported is sufficiently small to not cause errors. When the data to be exported is 
    large enough to possibly cause error, a chunked export method (slower) is used instead. The 
    maximum number of cells that will be exported before resorting to the chunked export method can be 
    set in the 'chunk_thres' parameter."""

    #warnings.warn('exportRecords() may return a different number of rows depending on what variables are requested. The number of rows may differ depending on whether export_form_completion = True or False.')
    ### NOTE: exportRecords() may return a different number of rows depending on what variables are requested. The number of rows may differ depending on whether export_form_completion=True/False.
    
    # Load project.
    project = redcap.Project(api_url, api_key)

    # If specific records, events, forms, or fields are requested, validate the requests. REDCap may return nonsense if non-existent records, events, fields, or forms are requested.
    if validate:
        if (record_id_list != None):
            # If specific records are requested, ensure that they all exist in the project. Raise warnings for requested records not found in the project. If none of the requested records are found in the project, return nothing.
            # Load list of all record IDs.
            record_ids_all = project.export_records(fields=[project.def_field]) # may contain additional fields and mutliple rows per record
            record_ids_all = set([row[project.def_field] for row in record_ids_all]) # set of all IDs without duplicates
            missing_ids = []
            for id in record_id_list:
                if (not id in record_ids_all):
                    if (not id in missing_ids):
                        missing_ids.append(id)
            if (missing_ids != []): # if any of the requested IDs is missing from the project
                warnings.warn("The following requested IDs were not found: "+" ".join(["'"+missing_id+"'" for missing_id in missing_ids]))
                record_id_list = [id for id in record_id_list if (not id in missing_ids)]
        if (events != None):
            # If specific events are requested, ensure that they all exist in the project. Raise warnings for requested events not found in the project. If none of the requested events are found in the project, return nothing.
            # Load list of all events.
            if (not project.is_longitudinal() ): # if the project doesn't use events
                events_all = []
            else:
                events_info = project.events
                events_all = [event_info['unique_event_name'] for event_info in events_info]
            missing_events = []
            for event in events:
                if (not event in events_all):
                    if (not event in missing_events):
                        missing_events.append(event)
            if (missing_events != []):
                warnings.warn("The following requested events were not found: "+" ".join(["'"+missing_event+"'" for missing_event in missing_events]))
                events = [event for event in events if (not event in missing_events)]
        if (forms != None):
            # If specific forms are requested, ensure that they all exist in the project. Raise warnings for requested forms not found in the project. If none of the requested forms or fields are found in the project, return nothing.
            # Load list of all forms.
            forms_all = project.forms
            missing_forms = []
            for form in forms:
                if (not form in forms_all):
                    if (not form in missing_forms):
                        missing_forms.append(form)
            if (missing_forms != []):
                warnings.warn("The following requested forms were not found: "+" ".join(["'"+missing_form+"'" for missing_form in missing_forms]))
                forms = [form for form in forms if (not form in missing_forms)]
        if (fields != None):
            # If specific fields are requested, ensure that they all exist in the project. Raise warnings for requested fields not found in the project. If none of the requested forms or fields are found in the project, return nothing.
            data_fields_all = project.field_names
            form_complete_fields_all = [form_name+'_complete' for form_name in project.forms]
            fields_all = data_fields_all + form_complete_fields_all
            missing_fields = []
            for field in fields:
                if (not field in fields_all):
                    if (not field in missing_fields):
                        missing_fields.append(field)
            if (missing_fields != []):
                warnings.warn("The following requested fields were not found: "+" ".join(["'"+missing_field+"'" for missing_field in missing_fields]))
                fields = [field for field in fields if (not field in missing_fields)]
                
    # If format='csv' and label=True, first export as json, then label, then convert to csv. THIS IS A SPOOF/HACK SOLUTION, A MORE SENSIBLE APPROACH SHOULD REPLACE THIS.
    if label:
        requested_format = format
        format = "json" 

    # If form completion variables are requested, generate a list of the form_complete variable names, and add it to the list of fields requested.
    if export_form_completion:
        form_complete_names = []
        if (forms != None) and (forms != []): # If specific forms are requested, only export the form_complete fields for those forms.
            for form_name in forms:
                form_complete_name = form_name + '_complete'
                form_complete_names.append(form_complete_name)
            if (fields != None):
                # In this case (forms!=None and fields!=None), add the form_complete fields to the list of requested fields.
                fields.extend(form_complete_names)
            else:
                # In this case (forms!=None and fields==None), set fields to the list of form_complete fields.
                fields = form_complete_names
        elif (fields != None): # If specific forms are not requested, but specific fields are requested, don't export any form_complete fields (other than those explicitly requested).
            # In this case (forms==None and fields!=None), do not add any form_complete fields.
            pass        
        elif (fields == None) and (forms == None): # If no specific fields or forms are requested,
#            form_info = exportFormsOrdered(api_url, api_key)
#            for form_dict in form_info:
#                form_name = form_dict['instrument_name']
#                form_complete_name = form_name + '_complete'
#                form_complete_names.append(form_complete_name)
            forms_all = project.forms
            for form_name in forms_all:
                form_complete_name = form_name + '_complete'
                form_complete_names.append(form_complete_name)
            # In this case (forms==None and fields==None), generate a list of all fields, including the form_complete fields. Then set fields to the list of all fields + the list of form_complete fields.
            assert (forms == None) and (fields == None)
#            metadata = project.export_metadata() # list of dicts, one for each field. form_complete fields are not included.
#            field_names_all = [field_dict['field_name'] for field_dict in metadata]
            field_names_all = project.field_names
            fields = field_names_all + form_complete_names
        else: # ?if forms is an empty list and fields is not None
            pass

    # If specific forms were requested, and they exist in the project, add all the fields in those forms to the list of fields. This is done becuase for some reason, redcap.project.Project.export_records will erroneously include form_complete fields if and only if specific forms are requested (whether or not the forms actually exist).
    if (forms != None):
        if (fields == None):
            fields = [] # if specific fields were not requested, intialize a list of fields to export.
        # At this point, forms and fields are boths lists. If forms is not empty, add all of the fields contained in its forms to fields.
        if (len(forms) > 0):
            metadata = project.export_metadata() # list of dicts, one for each field. form_complete fields are not included.
            for field_dict in metadata:
                field_name = field_dict['field_name']
                form_name = field_dict['form_name']
                if (form_name in forms): # if the form containing the current field was requested.
                    if (not field_name in fields):
                        fields.append(field_name)
        # At this point, all of the fields in the requested forms, including the form_complete fields, should be in the fields list. Thus, the forms list is no longer needed.
        forms = None
        
    ## Check if the requested data actually exists in the project, and approximate size of data.
    # The following if boolean expression will return False if:
    # (a) specific records were requested, and none of them exist
    # (b) specific events were requested, and none of them exist
    # (c) specific forms or fields were requested, and none of them exist
#    if (record_id_list != []) and (events != []) and (not ((forms == []) and (fields == []))) and (not ((forms == []) and (fields == None))) and (not ((forms == None) and (fields == []))): # this made sense before adding the section of code which puts all of the fields that are in the requested forms into the list of requested fields.
    if (record_id_list != []) and (events != []) and (fields != []):
        project_empty = False
        # Note that, at this point, it is possible that fields=None xor forms=None.
    else:
        # Print messages which explain why the exported data is nothing.
        if (record_id_list == []):
            warnings.warn("Specific records were requested, but none of them exist in the project. Returning no data.")
        if (events == []):
            warnings.warn("Specific events were requested, but none of them exist in the project. Returning no data.")
        if (fields == []):
            warnings.warn("Specific forms or fields were requested, but none of them exist in the project. Returning no data.")
        project_empty = True


#    first_col = project.export_records(records=record_id_list, fields=[project.def_field], events=events)
#    try:
#        first_record_id = first_col[0][project.def_field]
#        project_empty = False
#    except IndexError: # Catch case in which project contains no records.
#        project_empty = True

    if project_empty:
        if (format == 'json'):
            return []
        elif (format == 'csv'):
            return ''
    else:
        first_col = project.export_records(records=record_id_list, fields=[project.def_field], events=events)
        first_record_id = first_col[0][project.def_field]
        
        num_rows = len(first_col) # number of rows in requested export.
        first_row = project.export_records(records=[first_record_id], fields=fields, forms=forms)
        num_cols = len(first_row[0]) # number of columns in requested export.
        if (num_rows*num_cols < chunk_thres): # If number of cells requested is less than chunk_thres
            if (not quiet):
#                print "Exporting records in one piece."
                pass
            records = project.export_records(records=record_id_list, events=events, fields=fields, forms=forms, export_data_access_groups=True, format=format)
        else:
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
                records_all = exportRecords(api_url, api_key, record_id_list=record_id_list, quiet=True, export_form_completion=export_form_completion) # Use all records with requested IDs in labelling function. Could be optimized.
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



## Use function as a command-line tool.
if (__name__ == '__main__'):
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.
    
    ## Create argument parser.
    description = """Export records from a REDCap project to a csv file. By default, all records, fields, and events are exported. Use optional arguments to export data for only certain records, fields, or 
events. User must provide either a project API key or a project code name, not both."""
    parser = argparse.ArgumentParser(description=description)

    ## Define positional arguments.
    parser.add_argument("out_path", help="file path to write the data to")

    ## Define keyword arguments.
    # Add arguments for API URL, API key, and code name of project used to retreive these.
    parser = api_settings.addApiArgs(parser) # Adds args "-n", "--code_name", "-k", "--api_key", "-u", "--api_url" to the argument parser.
        
    parser.add_argument("-r", "--records", help="list of records to export. Default: Export all records.", nargs="+", metavar=("ID_1", "ID_2"))
    parser.add_argument("-e", "--events", help="list of events to export. Note that an event's name may differ from the event's label. For example, and event with label 'Acute' may have name 'acute_arm_1'. Default: Export all events.", nargs="+", metavar=("event_1", "event_2"))
    parser.add_argument("-f", "--fields", help="list of fields to export. Default: export all fields. To export checkbox fields, specify the base variable name (e.g. 'cb_var' instead of 'cb_var___1', 'cb_var___2', ...)", nargs="+", metavar=("field_1", "field_2"))
    parser.add_argument("-i", "--instruments", help="list of data instrument names to export. Note that an instrument's name (shown in the data dictionary) may differ from an instrument's label (shown in the Online Designer). Default: export all instruments.", nargs="+", metavar=("form_1", "form_2"))
    parser.add_argument("-c", "--export_form_completion", help="export the fields which store the completion state of a form for the specific forms requested, or for all forms if specific fields or forms are not requested. Default: False", action="store_true")
    parser.add_argument("-q", "--quiet", help="do not print export progress. Default: False", action="store_true")
    parser.add_argument("-l", "--label", help="label cells as HIDDEN or INVALID if hidden by branching logic or invalid (event, form, instance) combinations. Warning: this is still experimental.", action="store_true")
    parser.add_argument("-o", "--label_overwrite", help="if the -l --label option is specified, using this option will overwrite fields containing entries with labels.", action="store_true")

    # Print help message if no args input.
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit()
    
    # Parse arguments.
    args = parser.parse_args()
    
    # Determine the API URL and API token based on the users input and api_keys.json file.
    api_url, api_key, code_name = api_settings.getApiCredentials(api_url=args.api_url, api_key=args.api_key, code_name=args.code_name)
    
    # Export records.
    records = exportRecords(api_url, api_key, record_id_list=args.records, events=args.events, fields=args.fields, forms=args.instruments, export_form_completion=args.export_form_completion, quiet=args.quiet, format='csv', label=args.label, label_overwrite=args.label_overwrite)
    
    # Save string to csv file.
    with open(args.out_path, 'wb') as handle:
        handle.write(records)
