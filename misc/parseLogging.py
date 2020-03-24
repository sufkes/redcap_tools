#!/usr/bin/env python

import os, sys
import pandas
import argparse

## SAMPLES ##
# Action                                       List of Data Changes OR Fields Exported
# Updated Record 13953-11 (Acute)              Assign record to Data Access Group (redcap_data_access_group = 'utsw')
# Updated Record 20914 (Follow-up)             Assign record to Data Access Group ([instance = 2], redcap_data_access_group = 'hsc')
# Created Record 13953-11 (Acute)              dateentered = '2019-04-09', admityes = '1', daent = '2019-04-07', gender = '2', birmont = '3', biryear = '2012', patient_information_complete = '0', ipssid = '13953-11'
# Updated Record (import) 20425 (Follow-up)    ipssid = '20425'
# Updated Record (import) 20391 (Follow-up)    [instance = 3], harel = ''
# Updated Record 1674 (Acute)                  pstrtrea = '2', asttpa = '1', tpatype(2) = checked, tparevas = '1', revassp(1) = checked, tpadose = '2', tpacaths = '04:00', tpainjst = '04:47', tpainjen = '05:10', tpamicro = '7', tpacathwi = '06:30', tpadescr = '"The left ICA injection at the end of the procedure indicated no flow through the terminal L ICA and L MCA M1 segment, despite earlier opening and hopefully, the nonfilling was due to a combination of residual clot and vasospasm."', recanres = '3', tpatime = '1', treatment_complete = '0'
# Updated Record (API) 17                      record_id = '17'
# Updated Record 14021-3 (Confirmation and Tracking - Arm 1: Cases)    enrolldate = '2019-04-05', img_silc = '1', img_ucsf = '1'


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
    select_changes = {}
    for key, value in column_changes_dict.iteritems():
        if (field_name == key) or (field_name + '___' in key):
            select_changes[key] = value
    select_changes = str(select_changes).lstrip("{").rstrip("}")
    return select_changes

def createReport(logs, record=None, field=None, out_path=None, quiet=False):
    """
    Parameters:
        logs: a list of paths to REDCap logging data stored in CSV (UTF-8).
    Returns:
        report_df: a summary of the data history;
    """

    # Load logs and put them all in a single dataframe.
    log_df = pandas.DataFrame()
    log_num = 1
    for sublog_path in logs:
        # I can't find an authorative statement about what encoding the logging file is. REDCap says that import data must be encoded in UTF-8. When I export Logging from IPSS V3, I get a utf-8 decoding error for byte 95.
        try:
            sublog_df = pandas.read_csv(sublog_path, dtype=unicode, encoding='utf-8').fillna('')
        except UnicodeDecodeError:
            raise Exception("Cannot decode logging file '"+sublog_path+"' using utf-8 encoding. One way to fix this is by opening the logging file in Excel, and select the File Format: CSV UTF-8 (Comma delimited) (.csv)")
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

    if (record != None):
        report_df = report_df.loc[(report_df['record_id']==record), :]

    if (field != None):
        report_df['change_requested'] = report_df['change_dict'].apply(selectChanges, args=(field,))
        report_df = report_df.loc[(report_df['change_requested'] != ''), :]

        
    # Reorder columns.
    if (field != None):
        report_df = report_df[['log_num', 'date', 'time', 'record_id', 'event', 'instance', 'Username', 'Action', 'Changes', 'change_requested']]
    else:
        report_df = report_df[['log_num', 'date', 'time', 'record_id', 'event', 'instance', 'Username', 'Action', 'Changes']]

    # Print some stuff to console.
    if (not quiet):
        cols_to_print = ['record_id', 'log_num', 'date', 'time', 'event', 'instance', 'Username']
        if (field != None):
            cols_to_print.append('change_requested')
        else:
            cols_to_print.append('Changes')
        print report_df[cols_to_print]    

    if (out_path != None):
#        writer = pandas.ExcelWriter(out_path, engine='xlsxwriter')
#        writer = pandas.ExcelWriter(out_path)
        writer = pandas.ExcelWriter(out_path, engine='openpyxl')
        report_df.to_excel(writer, encoding='utf-8', index=False)
        writer.close()
    

#    print report_df
#    print log_df.loc[log_df['change_dict'] != '', :]
#    lookat = range(10)
#    lookat = log_df.loc[(log_df['record_id']=='20070'),:].index
#    for ii in lookat:
#        print
#        print "EXAMPLE "+str(ii)+" (ID: "+log_df.loc[ii, 'record_id']+", source: "+log_df.loc[ii, 'source']+")"+":"
#        print log_df.loc[ii,'Changes']
#        print log_df.loc[ii,'change_dict']
    return report_df


#### Execute main function if script is called directly.
if (__name__ == '__main__'):
    # Create argument parser.
    description = """
    Returns:
        A summary of the data history entries in the specified REDCap logs. The data history query can be limited to a specific record and/or field. The returned summary can be saved by specifying an output path.
    """
    
    # Create argument parser.
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    
    # Define positional arguments.
    
    # Define optional arguments.
    default_logs = ['/Users/steven ufkes/Documents/stroke/ipss/logs/IPSS_V1_Logging_2019-04-10_0901.csv', '/Users/steven ufkes/Documents/stroke/ipss/logs/IPSS_V2_Logging_2019-04-10_0900.csv', '/Users/steven ufkes/Documents/stroke/ipss/logs/IPSS_V3_Logging_2020-03-16_1108.csv']
    parser.add_argument('-l', '--logs', action='store', type=str, nargs='*', help='paths to logs to be parsed. If multiple paths are specified, the logs will be concatenated and treated as a single log. If logs correspond to different versions of a REDCap project, list the logs in order of version number (i.e. most recent version last).', default=default_logs, metavar=('LOG_PATH_1,', 'LOG_PATH_2'))
    parser.add_argument('-r', '--record', action='store', type=str, help='name of record to query', metavar='RECORD_ID')
    parser.add_argument('-f', '--field', action='store', type=str, help='name of field to query')
    parser.add_argument('-o', '--out_path', action='store', type=str, help='path to save report to. If none specified, report will not be saved.')
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print report to screen')
    
    # Parse arguments.
    args = parser.parse_args()

    # Generate report
    createReport(logs=args.logs, record=args.record, field=args.field, out_path=args.out_path, quiet=args.quiet)
