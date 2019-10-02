#!/usr/bin/env python

import pandas as pd
import os, sys
from datetime import date
from pprint import pprint
from collections import OrderedDict

def change_dtype(value):
    """Use to convert cells back to numbers if possible. Apply to columns using df[column].apply(change_dtype)"""
    try:
        new_value = int(value)
    except ValueError:
        try:
            new_value = float(value)
        except ValueError:
            new_value = value
    return new_value

def indicesDuplicated(*args):
    """Parameters:
        args: Pandas DataFrames
    Returns:
        index_dup: bool, whether any indices are duplicated."""
    dups = False
    for df in args:
        if any(df.index.duplicated()):
            dups = True
            print "Warning: duplicated indices"
            return dups
    return dups

def absDateDiff(start, end):
    """Parameters:
        start: str, date 1 in format yyyy-mm-dd
        end: str, date 2 in format yyyy-mm-dd
    Returns:
        absolute difference between dates in days""" 
    start_year = int(start[:4])
    start_month = int(start[5:7])
    start_day = int(start[8:10])
    end_year = int(end[:4])
    end_month = int(end[5:7])
    end_day = int(end[8:10])
    start_date = date(start_year, start_month, start_day)
    end_date = date(end_year, end_month, end_day)
    diff = end_date - start_date
    abs_diff_days = abs(diff.days)
#    print start_date, end_date, abs_diff_days
    return abs_diff_days

xlsx = pd.ExcelFile('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/data_package_sipsf_reformat_all_events_multirow.xlsx')
df_fup_sips2 = pd.read_excel(xlsx, 'follow_up_crf').fillna('').astype(unicode)
df_rrq_ipss = pd.read_excel(xlsx, 'recovery_and_recurrence').fillna('').astype(unicode)
df_out_ipss = pd.read_excel(xlsx, 'outcome').fillna('').astype(unicode) # Convert to dataframe using types specified in Excel; fill NaNs with '', then convert all columns to unicode
df_soi_psom2 = pd.read_excel(xlsx, 'summary_of_impressions').fillna('').astype(unicode)

# Record number of rows in each dataframe for future reference
num_rows_org_fup_sips2 = len(df_fup_sips2)
num_rows_org_rrq_ipss = len(df_rrq_ipss)
num_rows_org_out_ipss = len(df_out_ipss)
num_rows_org_soi_psom2 = len(df_soi_psom2)

# Check for empty date fields
#print df_fup_sips2.loc[df_fup_sips2['date_v2'] == '', :] # <- There are some blank SIPS II follow up dates.
#print df_rrq_ipss.loc[df_rrq_ipss['assedat'] == '', :]
#print df_out_ipss.loc[df_out_ipss['fuionset'] == '', :]
#print df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] == '', :]

## Initialize DataFrames to store data that will be excluded from each form.
# Populate excluded-data dataframes with those rows whose date fields are empty.
df_rrq_ipss_ex = df_rrq_ipss.loc[df_rrq_ipss['assedat'] == '', :]
df_out_ipss_ex = df_out_ipss.loc[df_out_ipss['fuionset'] == '', :]
df_soi_psom2_ex = df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] == '', :]

#print df_rrq_ipss_ex
#print df_out_ipss_ex
#print df_soi_psom2_ex

# Remove rows with empty dates in IPSS & PSOM prior to merge.
df_rrq_ipss = df_rrq_ipss.loc[df_rrq_ipss['assedat'] != '', :]
df_out_ipss = df_out_ipss.loc[df_out_ipss['fuionset'] != '', :]
df_soi_psom2 = df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] != '', :]

# Check row number preservation
#print "fup_sips2 rows:", len(df_fup_sips2)
#print "rrq_ipss rows:", num_rows_org_rrq_ipss, len(df_rrq_ipss), len(df_rrq_ipss_ex), (num_rows_org_rrq_ipss == len(df_rrq_ipss) + len(df_rrq_ipss_ex))
#print "out_ipss rows:", num_rows_org_out_ipss, len(df_out_ipss), len(df_out_ipss_ex), (num_rows_org_out_ipss == len(df_out_ipss) + len(df_out_ipss_ex))
#print "soi_psom2 rows:", num_rows_org_soi_psom2, len(df_soi_psom2), len(df_soi_psom2_ex), (num_rows_org_soi_psom2 == len(df_soi_psom2) + len(df_soi_psom2_ex))

# Check for duplicated indices
indicesDuplicated(df_fup_sips2, df_rrq_ipss, df_out_ipss, df_soi_psom2, df_rrq_ipss_ex, df_out_ipss_ex, df_soi_psom2_ex)

## Identify rows that have no date match in SIPS2, add these to the list of excluded rows from each database/form.
def findUnmatchedIndices(df_left, df_right, on_left=['ipssid', 'date_v2'], on_right=None):
    right_unmatched = []
    for index in df_right.index:
        val_1 = df_right.loc[index, on_right[0]]
        val_2 = df_right.loc[index, on_right[1]]
        left_match = df_left.loc[(df_left[on_left[0]]==val_1) & (df_left[on_left[1]]==val_2), :]
        num_match = len(left_match)
        if (num_match == 0):
            right_unmatched.append(index)
        elif (num_match == 1):
            continue # best case scenario
        elif (num_match > 1):
            print "Warning: Multiple matching rows:", on_left[0], "=", val_1+",", on_left[1], "=", val_2
    return right_unmatched

# Generate lists of indices in the RRQ, Outcome, and PSOM data which has no match in SIPS. Also report columns which 
if True:
    print "Warning: Skipping duplciate merge key check for speed"
    print '-'*80
    print "The following duplicate merge keys must be dealt with before merging:"
    unmatched_indices_rrq_ipss = findUnmatchedIndices(df_fup_sips2, df_rrq_ipss, on_right=['ipssid', 'assedat'])
    findUnmatchedIndices(df_rrq_ipss, df_fup_sips2, on_left=['ipssid', 'assedat'], on_right=['ipssid', 'date_v2'])
    unmatched_indices_out_ipss = findUnmatchedIndices(df_fup_sips2, df_out_ipss, on_right=['ipssid', 'fuionset'])
    findUnmatchedIndices(df_out_ipss, df_fup_sips2, on_left=['ipssid', 'fuionset'], on_right=['ipssid', 'date_v2'])
    unmatched_indices_soi_psom2 = findUnmatchedIndices(df_fup_sips2, df_soi_psom2, on_right=['ipssid', 'fuionset_soi'])
    findUnmatchedIndices(df_soi_psom2, df_fup_sips2, on_left=['ipssid', 'fuionset_soi'], on_right=['ipssid', 'date_v2'])
    print '-'*80

# Add unmatched rows to excluded data dataframes
#df_rrq_ipss_ex = pd.concat([df_rrq_ipss_ex, df_rrq_ipss.loc[unmatched_indices_rrq_ipss,:]])
#df_out_ipss_ex = pd.concat([df_out_ipss_ex, df_out_ipss.loc[unmatched_indices_out_ipss,:]])
#df_soi_psom2_ex = pd.concat([df_soi_psom2_ex, df_soi_psom2.loc[unmatched_indices_soi_psom2,:]])
#df_rrq_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_rrq_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
#df_out_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_out_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
#df_soi_psom2_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_soi_psom2_excluded_rows.xlsx', encoding='utf-8', index=False)


#bad_id = df_fup_sips2.loc[468,'ipssid']
#print df_fup_sips2.loc[df_fup_sips2['ipssid']==bad_id,['ipssid','date_v2']]
#print df_rrq_ipss.loc[df_rrq_ipss['ipssid']==bad_id,['ipssid','assedat']]
#print df_out_ipss.loc[df_out_ipss['ipssid']==bad_id,['ipssid','fuionset']]
#print df_soi_psom2.loc[df_soi_psom2['ipssid']==bad_id,['ipssid','fuisonset_soi']]

## Create dict which matches rows in "other" forms to rows in SIPS II { (SIPS index, SIPS date) : [(other index, other date, other ID)] } 
other_forms = [(df_rrq_ipss, 'assedat', {}, {}), (df_out_ipss, 'fuionset', {}, {}), (df_soi_psom2, 'fuionset_soi', {}, {})]
for form, date_var, sips2_to_other_dict, other_to_sips2_dict in other_forms:
    for index_other in form.index:

        # Get ID and date for current row in "other" form
        id = form.loc[index_other,'ipssid']
        date_other = form.loc[index_other, date_var]
        
        # Find the index of the SIPS row with the closest-matching date.
        checked_first_row = False
        loose_match_found = False
        for index_sips2 in df_fup_sips2.loc[df_fup_sips2['ipssid']==id,:].index:
            date_sips2 = df_fup_sips2.loc[index_sips2, 'date_v2']
            if (date_sips2 == ''):
#                print "Warning: Empty SIPS II date:", date_sips2, index_sips2
                continue
            else:
                loose_match_found = True # It is possible that no SIPS II exists at all (e.g. if the only row has a blank date)
            datediff = absDateDiff(date_sips2, date_other)
            if (not checked_first_row):
                min_datediff = datediff
                min_index_sips2 = index_sips2
                min_date_sips2 = date_sips2
                checked_first_row = True
            elif (datediff < min_datediff):
                min_datediff = datediff
                min_index_sips2 = index_sips2
                min_date_sips2 = date_sips2

        if loose_match_found: # Don't create a key if no loosely matching SIPS date was found (e.g. if the only matching SIPS II row has a blank date)
            # Add key if not in dict.
            sips2_to_other_key = (min_index_sips2, min_date_sips2)
            sips2_to_other_val_element = (index_other, date_other)
            if (not sips2_to_other_key in sips2_to_other_dict):
                sips2_to_other_dict[sips2_to_other_key] = []

            # Add "other" match to list
            sips2_to_other_dict[sips2_to_other_key].append(sips2_to_other_val_element)



# Go through date-match dicts and get only the closest date mathces; reverse the dict direction (want other -> sips2)
for form, date_var, sips2_to_other_dict, other_to_sips2_dict in other_forms:
    for key_sips2, val_other in sips2_to_other_dict.iteritems():
        index_sips2 = key_sips2[0]
        date_sips2 = key_sips2[1]

        # Find the match which is closest to the SIPS II date
        checked_first_row = False
        for row_index_other in range(len(val_other)): # row_index_other is the index in the list of tuples

            row_other = val_other[row_index_other]
            index_other = row_other[0] # index in the dataframe
            date_other = row_other[1]

            datediff = absDateDiff(date_sips2, date_other)
            if (not checked_first_row):                
                min_datediff = datediff
                min_index_other = index_other # index in the dataframe
                checked_first_row = True
            elif (datediff < min_datediff):
                min_datediff = datediff
                min_index_other = index_other # index in the dataframe
        
        # Using double-nearest match, add dict item to other_to_sips2_dict
        other_to_sips2_key = min_index_other
        other_to_sips2_val = index_sips2
        other_to_sips2_dict[other_to_sips2_key] = other_to_sips2_val
        
        # Inspect result
        current_id = df_fup_sips2.loc[index_sips2, 'ipssid']
        other_date = form.loc[min_index_other, date_var]
        sips2_date = df_fup_sips2.loc[index_sips2, 'date_v2']
        print current_id, other_date, sips2_date, min_datediff
#        if True:
#        if (other_date != sips2_date):
        if False:
            print '-'*80
            print "Index match (other -> SIPS II):", min_index_other, '->', index_sips2
            print
            print "SIPS II rows:"
            print df_fup_sips2.loc[df_fup_sips2['ipssid']==current_id, 'date_v2']
            print 
            print "Other rows:"
            print form.loc[form['ipssid']==current_id, date_var]
            print '-'*80


# Add unmapped rows to list of excluded rows.
#print len(df_rrq_ipss_ex) # num excluded before addition
df_rrq_ipss_ex = pd.concat([df_rrq_ipss_ex, df_rrq_ipss.loc[~(df_rrq_ipss.index.isin(other_forms[0][3].keys())),:]])
#print len(df_rrq_ipss) - len(other_forms[0][3].keys()) # num additional exclusions
#print len(df_rrq_ipss_ex) # num final exclusions
#print len(df_out_ipss_ex)
df_out_ipss_ex = pd.concat([df_out_ipss_ex, df_out_ipss.loc[~(df_out_ipss.index.isin(other_forms[1][3].keys())),:]])
#print len(df_out_ipss) - len(other_forms[1][3].keys())
#print len(df_out_ipss_ex)
#print len(df_soi_psom2_ex)
df_soi_psom2_ex = pd.concat([df_soi_psom2_ex, df_soi_psom2.loc[~(df_soi_psom2.index.isin(other_forms[2][3].keys())),:]])
#print len(df_soi_psom2) - len(other_forms[2][3].keys())
#print len(df_soi_psom2_ex)

# Overwrite IPSS V3 'Outcome - PSOM' Summary of Impressions fields with 'NA'.
soi_ipss_fields = ['psom_notdone___1','fuionset', 'fpsomr', 'fpsoml', 'fpsomlae', 'fpsomlar', 'fpsomcb', 'psomsen___3', 'psomsen___4', 'psomsen___5', 'psomsen___6', 'psomsen___7', 'psomsen___8', 'psomsen___9', 'psomsen___10', 'psomsen___11', 'psomsen___12', 'psomsen___13', 'psomsen___14', 'othsens', 'fpsomco___1', 'fpsomco___2', 'totpsom']
df_out_ipss.loc[(df_out_ipss['redcap_data_access_group']=='hsc'), soi_ipss_fields] = 'NA'
#print df_out_ipss[['ipssid', 'redcap_data_access_group', 'totpsom']] # seems all good at this point.
#sys.exit()

# Drop event name fields from the "other" forms.
df_rrq_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], axis=1, inplace=True)
df_out_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], axis=1, inplace=True)
df_soi_psom2.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance'], axis=1, inplace=True)

# Create dataframes for the modified fields:
suffix_map = OrderedDict([('_3mo', '3_month_arm_1'), ('_12mo', '12_month_arm_1'), ('_addfup1', 'additional_fup1_arm_1'), ('_addfup2', 'additional_fup2_arm_1'), ('_addfup3', 'additional_fup3_arm_1'), ('_addfup4', 'additional_fup4_arm_1'), ('_addfup5', 'additional_fup5_arm_1'), ('_addfup6', 'additional_fup6_arm_1')])
suffix_map = OrderedDict([(event, suffix) for suffix, event in suffix_map.iteritems()]) # reverse key-value ordering.
form_num = 0

# Create a nonsense SIPS II -> SIPS II mapping in same format as other forms, so that I don't need to handle anything differently.
sips2_to_sips2_map = {ii:ii for ii in df_fup_sips2.index}
other_forms.append((df_fup_sips2, 'date_v2', sips2_to_sips2_map, sips2_to_sips2_map))

for form, date_var, sips2_to_other_dict, other_to_sips2_dict in other_forms:
    unchanged_columns = ['ipssid', 'redcap_data_access_group', 'strage']
    if (form_num == 3): # if doing SIPS II followup form.
        unchanged_columns = ['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage']
    new_columns = unchanged_columns
    changed_columns = [col for col in form.columns if (not col in unchanged_columns)] 
#    print "Changed columns:", changed_columns
    for event_name, suffix in suffix_map.iteritems():
        for column in changed_columns:
#            print column, column+suffix
            new_columns.append(column+suffix)

    # Populate the new dataframes with values using other_to_sips2_dict
    new_df = pd.DataFrame(columns=new_columns)
    for index_other, index_sips2 in other_to_sips2_dict.iteritems():
        id = form.loc[index_other, 'ipssid']
        dag = form.loc[index_other, 'redcap_data_access_group']
        strage = form.loc[index_other, 'strage']

        # Initialize the new row if it has not yet been added.
        if (not id in list(new_df.loc[:,'ipssid'])): # If ID is not yet in the new dataframe
            new_df = new_df.append(pd.Series(), ignore_index=True)
            new_df.loc[new_df.index[-1], 'ipssid'] = id
            new_df.loc[new_df.index[-1], 'redcap_data_access_group'] = dag
            new_df.loc[new_df.index[-1], 'strage'] = strage
        
        # Populate the other rows.
        sips2_event = df_fup_sips2.loc[index_sips2, 'redcap_event_name']
        suffix = suffix_map[sips2_event]
        current_field_map = {}
#        for column in form.columns:
#            if column in unchanged_columns:
#                continue # data for these fields should already have been added.
        for column in changed_columns:
#            val = form.loc[index_other, column]
            new_column = column + suffix
            current_field_map[column] = new_column
#            new_df.loc[new_df.index[-1], new_column] = val # this is probably the slow part; try adding to whole row at once.

        # Get all original data in a pd.Series(). Now the original variable names form the index of said series.
        row_series = form.loc[index_other, changed_columns]

        # Rename the index in series to the formatted names
        row_series.rename(index=current_field_map, inplace=True) # Only rename the fields whose name should be changed.

        new_df.loc[new_df.index[-1], row_series.index] = row_series

    new_df = new_df.fillna('')

    # Convert back dtypes
    for column in new_df.columns:
        if (not column in ['redcap_event_name', 'redcap_repeat_instrument', 'redcap_data_access_group']):
            new_df.loc[:, column] = new_df.loc[:, column].apply(change_dtype)

    # Save the dataframe 
    if (form_num == 0):
        form_name = 'recovery_and_recurrence'
    elif (form_num == 1):
        form_name = 'outcome'
    elif (form_num == 2):
        form_name = 'summary_of_impressions'
    elif (form_num == 3):
        form_name = 'followup_crf'

    new_df.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/reformatted_'+form_name+'.xlsx', encoding='utf-8', index=False, sheet_name=form_name)
    form_num += 1

df_rrq_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_rrq_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
df_out_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_out_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
df_soi_psom2_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_soi_psom2_excluded_rows.xlsx', encoding='utf-8', index=False)


## Modify data prior to merge.
# Remove IPSS and PSOM event columns
#df_rrq_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)
#df_out_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)
#df_soi_psom2.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)

# Rename all fields in PSOM and IPSS prior to merge (change names back later).
#def renameColumns(df, suffix, exclude=['ipssid']):
#    """Append 'suffix' to all columns in dataframe, other than those in 'exclude'"""
#    for col in df.columns:
#        if col in exclude:
#            continue
#        else:
#            new_col = col+suffix
#            df = df.rename(columns={col:new_col})
#    return df
#
#df_fup_sips2 = renameColumns(df_fup_sips2, suffix='_rename_fup_sips2', exclude=['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'])
#df_rrq_ipss = renameColumns(df_rrq_ipss, suffix='_rename_rrq_ipss') # rename everything but 'ipssid' by default
#df_out_ipss = renameColumns(df_out_ipss, suffix='_rename_out_ipss')
#df_soi_psom2 = renameColumns(df_soi_psom2, suffix='_rename_soi_psom2')

# Merge all data together
#df_all = df_fup_sips2
#print len(df_all)
#df_all = df_all.merge(df_rrq_ipss, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'assedat_rename_rrq_ipss'])
#print len(df_all)
#df_all = df_all.merge(df_out_ipss, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'fuionset_rename_out_ipss'])
#print len(df_all)
#df_all = df_all.merge(df_soi_psom2, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'fuionset_soi_rename_soi_psom2'])
#print len(df_all)
#df_all.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_all.xlsx', encoding='utf-8', index=False)
