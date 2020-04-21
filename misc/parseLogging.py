#!/usr/bin/env python

# Standard modules
import os, sys
import pandas
import argparse

# My modules in current directory
from ApiSettings import ApiSettings

def separateDate(column_time_date):
    return column_time_date.split()[0]

def separateTime(column_time_date):
    return column_time_date.split()[1]

def separateTimeDate(df):
    df['date'] = df['Time / Date'].apply(separateDate)
    df['time'] = df['Time / Date'].apply(separateTime)
    del df['Time / Date']
    return df

def parseID(column_action):
    """Extract the record ID from the Action column in the logging (for record modification rows only)."""
    strings = column_action.split()
    if (not '(' in strings[2]):
        return strings[2]
    else:
        return strings[3]

def parseEventName(column_action):
    """Extract event name / arm name. This is not guaranteed to work every time but usually will. Currently does not generate the unique event name, but could enable it to possibly."""    
    if (column_action[-1] != ')'):
        return ''
    else:
        return column_action.split(')')[-2].split('(')[-1]

def parseInstance(column_changes):
    """Extract the instance number from the Changes column in the logging (for record modification rows only)."""    
    try:
        return column_changes.split('[instance = ')[1].split(']')[0]
    except IndexError:
        return ''

def parseChanges(column_changes):
    changes = {} # list of (field_name, value) tuples

    # Examples: 
    # carcath(1) = checked, cath(2) = checked, ballo(1) = checked, ballod = '2015-09-02', othpro(1) = unchecked, othprosp = '', othprod = ''
    # doe = '2006-08-01', othcond(1) = checked, othconsp = 'PPERI', dateest = '1', childrac(9) = unchecked, fathrac(9) = unchecked, mothrac(9) = unchecked

    # Get checkbox changes.
#    for substring in column_changes.split(') = checked,')[:-1]:
    for substring in column_changes.split(') = checked')[:-1]:
        field_name = substring.split('(')[-2].split()[-1]
        option = substring.split('(')[-1]
        full_field_name = field_name + "___" + option
        if full_field_name in changes:
            print "Error: same field changed twice in one line."
            print column_changes
            print changes
            print full_field_name
            sys.exit()
        changes[full_field_name] = '1'
#    for substring in column_changes.split(') = unchecked,')[:-1]:
    for substring in column_changes.split(') = unchecked')[:-1]:
        field_name = substring.split('(')[-2].split()[-1]
        option = substring.split('(')[-1]
        full_field_name = field_name + "___" + option
        if full_field_name in changes:
            print "Error: same field changed twice in one line."
            print column_changes
            print changes
            print full_field_name
            sys.exit()
        changes[full_field_name] = '0'

    # Get non-checkbox changes.
    substring_list = column_changes.split(" = '")
    num_substrings = len(substring_list)
    for ii in range(num_substrings)[:-1]:
        field_name = substring_list[ii].split(", ")[-1]
        if (ii < num_substrings - 2):
            value = substring_list[ii+1].split("', ")[0]
        else:
            value = substring_list[ii+1][:-1].split("', ")[0]
#        if (field_name == 'redcap_data_access_group'): # Handle separately becuase the logging prints a weird message for DAG changes.
#            value = value[:-1]
        if (field_name == 'Assign record to Data Access Group (redcap_data_access_group'):
            field_name = 'redcap_data_access_group'
            value = value.rstrip("'")
        if field_name in changes:
            print "Error: same field changed twice in one line."
            print column_changes
            sys.exit()
        changes[field_name] = value
    return changes

def selectChanges(column_changes_dict, field_name):
#    select_changes = {}
    select_changes = ''
    for key, value in column_changes_dict.iteritems():
        if (field_name == key) or (field_name + '___' in key):
            #select_changes[key] = value
            select_changes = key+" = '"+value+"'"
#    select_changes = str(select_changes).lstrip("{").rstrip("}")
#    select_changes_split = select_changes.split(':')
#    try:
#        field_name_substring = select_changes_split[0].lstrip("u").strip("'")
#        field_value_substring = select_changes_split[1].lstrip("u").strip("'")
#    except:
#        print key, value
#    select_changes = ':'.join([field_name_substring, field_value_substring])
    return select_changes

def createReport(log_paths, records=None, fields=None, out_path=None, quiet=False):
    """
    Parameters:
        log_paths: a list of paths to REDCap logging data stored in CSV (UTF-8).
    Returns:
        report_df: a summary of the data history;
    """

    # Load log_paths and put them all in a single dataframe.
    log_df = pandas.DataFrame()
    log_num = 1
    for sublog_path in log_paths:
        # I can't find an authorative statement about what encoding the logging file is. REDCap says that import data must be encoded in UTF-8. When I export Logging from IPSS V3, I get a utf-8 decoding error for byte 95.
        if (os.path.exists(sublog_path)):
            try:
                sublog_df = pandas.read_csv(sublog_path, dtype=unicode, encoding='utf-8').fillna('')
            except UnicodeDecodeError:
                raise Exception("Cannot decode logging file '"+sublog_path+"' using utf-8 encoding. One way to fix this is by opening the logging file in Excel, and select the File Format: CSV UTF-8 (Comma delimited) (.csv)")
        else:
            raise Exception("Log path does not exist: '"+sublog_path+"'")
        sublog_df['source'] = sublog_path
        sublog_df['log_num'] = log_num
        log_num += 1
        log_df = log_df.append(sublog_df)
    
    # Remove all rows that do not correspond to a record modification.
    log_df = log_df.loc[(log_df['Action'].str.contains('Created Record')) | (log_df['Action'].str.contains('Updated Record')), :]
    
    # Separate date and time into separate columns.
    log_df = separateTimeDate(log_df)

    # Sort log based on log number, date, time (
    log_df.sort_values(['log_num', 'date', 'time'], ascending=(False, False, False), inplace=True)

    # Reset index.
    log_df.reset_index(inplace=True, drop=True)    

    # Change name of column from 'List of Data Changes OR Fields Exported' to 'Changes'.
    new_columns = {'List of Data Changes OR Fields Exported':'Changes'}
    log_df.rename(columns=new_columns, inplace=True)
    
    # Add columns to store record ID, instance number
    log_df['record_id'] = log_df['Action'].apply(parseID)
    log_df['event'] = log_df['Action'].apply(parseEventName)
    log_df['instance'] = log_df['Changes'].apply(parseInstance)
    
    # Add column to store list of tuples: (field_name, value)
    log_df['change_dict'] = log_df['Changes'].apply(parseChanges)
    
    # Generate report on requested record and field
    report_df = log_df.copy()

    if (records != None):
        report_df = report_df.loc[report_df['record_id'].isin(records), :]

    if (fields != None):
        # Add a column for each requested field.
        for field in fields:
            report_df[field] = report_df['change_dict'].apply(selectChanges, args=(field,))

        # Remove all rows not corresponding to changes in the requested fields.
        report_df = report_df.loc[(report_df[fields]!='').any(axis=1), :]

        
    # Reorder columns.
    if (fields != None):
        report_df = report_df[['log_num', 'source', 'date', 'time', 'record_id', 'event', 'instance', 'Username', 'Action', 'Changes'] + fields]
    else:
        report_df = report_df[['log_num', 'source', 'date', 'time', 'record_id', 'event', 'instance', 'Username', 'Action', 'Changes']]

    # Print some stuff to console.
    if (not quiet):
        print report_df
#        cols_to_print = ['record_id', 'log_num', 'date', 'time', 'event', 'instance', 'Username']
#        if (fields != None):
#            cols_to_print.extend(fields)
#        else:
#            cols_to_print.append('Changes')
#        print report_df[cols_to_print]    

    if (out_path != None):
        writer = pandas.ExcelWriter(out_path, engine='openpyxl')
        report_df.to_excel(writer, encoding='utf-8', index=False)
        writer.close()
    
    return report_df


#### Execute main function if script is called directly.
if (__name__ == '__main__'):
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find json file containing API keys and URLs.
    
    # Create argument parser.
    description = """
    Returns:
        A summary of the data history entries in the specified REDCap logs. The data history query can be limited to specifics record and/or fields. The returned summary can be saved by specifying an output path.
    """
    
    # Create argument parser.
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    
    # Define positional arguments.
    
    # Define optional arguments.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--log_paths', action='store', type=str, nargs='*', help='paths to logs to be parsed. If multiple paths are specified, the logs will be concatenated and treated as a single log. If logs correspond to different versions of a REDCap project, list the logs in order of version number (i.e. most recent version last).', metavar=('LOG_PATH_1,', 'LOG_PATH_2'))
    group.add_argument('-n', '--code_name', help="If this option is used, all CSV files in the directory '"+os.path.join(api_settings.settings['logging_path'], 'CODE_NAME')+"' will be assumed to be logging CSV files, and this script will parse them all together.", type=str)
    group.add_argument('-d', '--logs_dir', help="Path to directory containing log files. If this option is used, all CSV files in the specified directory will be assumed to be logging CSV files, and this script will parse them all together.", type=str)
    parser.add_argument('-r', '--records', help='record IDs to query', action='store', type=str, nargs="+", metavar=("ID_1", "ID_2"))
    parser.add_argument('-f', '--fields', help='fields to query', action='store', type=str, nargs="+", metavar=("FIELD_1", "FIELD_2"))
    parser.add_argument('-o', '--out_path', action='store', type=str, help='path to save report to. If none specified, report will not be saved.')
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print report to screen')
    
    # Parse arguments.
    args = parser.parse_args()

    # Build list of paths to logs to parse.
    if (not args.log_paths is None):
        log_paths = args.log_paths
    elif (not args.logs_dir is None):
        log_paths = [os.path.join(args.logs_dir, name) for name in os.listdir(args.logs_dir) if name.endswith(".csv")]
        log_paths.sort()
    elif (not args.code_name is None):
        logs_dir = os.path.join(api_settings.settings['logging_path'], args.code_name)
        log_paths = [os.path.join(logs_dir, name) for name in os.listdir(logs_dir) if name.endswith(".csv")]
        log_paths.sort()
    print 'DEBUG: log_paths:', log_paths
        
    # Generate report
    createReport(log_paths=log_paths, records=args.records, fields=args.fields, out_path=args.out_path, quiet=args.quiet)
