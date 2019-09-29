#!/usr/bin/env python

import pandas as pd
import os, sys

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
#print df_fup_sips2.loc[df_fup_sips2['date_v2'] == '', :]
#print df_rrq_ipss.loc[df_rrq_ipss['assedat'] == '', :]
#print df_out_ipss.loc[df_out_ipss['fuionset'] == '', :]
#print df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] == '', :]

# Generate list of data that will be excluded from each form.
df_rrq_ipss_ex = df_rrq_ipss.loc[df_rrq_ipss['assedat'] == '', :]
df_out_ipss_ex = df_out_ipss.loc[df_out_ipss['fuionset'] == '', :]
df_soi_psom2_ex = df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] == '', :]

print df_rrq_ipss_ex
print df_out_ipss_ex
print df_soi_psom2_ex

# Remove rows with empty dates in IPSS & PSOM prior to merge.
df_rrq_ipss = df_rrq_ipss.loc[df_rrq_ipss['assedat'] != '', :]
df_out_ipss = df_out_ipss.loc[df_out_ipss['fuionset'] != '', :]
df_soi_psom2 = df_soi_psom2.loc[df_soi_psom2['fuionset_soi'] != '', :]

# Check row number preservation
print "fup_sips2 rows:", len(df_fup_sips2)
print "rrq_ipss rows:", num_rows_org_rrq_ipss, len(df_rrq_ipss), len(df_rrq_ipss_ex), (num_rows_org_rrq_ipss == len(df_rrq_ipss) + len(df_rrq_ipss_ex))
print "out_ipss rows:", num_rows_org_out_ipss, len(df_out_ipss), len(df_out_ipss_ex), (num_rows_org_out_ipss == len(df_out_ipss) + len(df_out_ipss_ex))
print "soi_psom2 rows:", num_rows_org_soi_psom2, len(df_soi_psom2), len(df_soi_psom2_ex), (num_rows_org_soi_psom2 == len(df_soi_psom2) + len(df_soi_psom2_ex))

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
print "The following duplicate merge keys must be dealt with before merging:"
unmatched_indices_rrq_ipss = findUnmatchedIndices(df_fup_sips2, df_rrq_ipss, on_right=['ipssid', 'assedat'])
findUnmatchedIndices(df_rrq_ipss, df_fup_sips2, on_left=['ipssid', 'assedat'], on_right=['ipssid', 'date_v2'])
unmatched_indices_out_ipss = findUnmatchedIndices(df_fup_sips2, df_out_ipss, on_right=['ipssid', 'fuionset'])
findUnmatchedIndices(df_out_ipss, df_fup_sips2, on_left=['ipssid', 'fuionset'], on_right=['ipssid', 'date_v2'])
unmatched_indices_soi_psom2 = findUnmatchedIndices(df_fup_sips2, df_soi_psom2, on_right=['ipssid', 'fuionset_soi'])
findUnmatchedIndices(df_soi_psom2, df_fup_sips2, on_left=['ipssid', 'fuionset_soi'], on_right=['ipssid', 'date_v2'])

# Add unmatched rows to excluded data dataframes
df_rrq_ipss_ex = pd.concat([df_rrq_ipss_ex, df_rrq_ipss.loc[unmatched_indices_rrq_ipss,:]])
df_out_ipss_ex = pd.concat([df_out_ipss_ex, df_out_ipss.loc[unmatched_indices_out_ipss,:]])
df_soi_psom2_ex = pd.concat([df_soi_psom2_ex, df_soi_psom2.loc[unmatched_indices_soi_psom2,:]])
df_rrq_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_rrq_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
df_out_ipss_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_out_ipss_excluded_rows.xlsx', encoding='utf-8', index=False)
df_soi_psom2_ex.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_soi_psom2_excluded_rows.xlsx', encoding='utf-8', index=False)

## Modify data prior to merge.
# Remove IPSS and PSOM event columns
df_rrq_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)
df_out_ipss.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)
df_soi_psom2.drop(['redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'], axis=1, inplace=True)

# Rename all fields in PSOM and IPSS prior to merge (change names back later).
def renameColumns(df, suffix, exclude=['ipssid']):
    """Append 'suffix' to all columns in dataframe, other than those in 'exclude'"""
    for col in df.columns:
        if col in exclude:
            continue
        else:
            new_col = col+suffix
            df = df.rename(columns={col:new_col})
    return df

df_fup_sips2 = renameColumns(df_fup_sips2, suffix='_rename_fup_sips2', exclude=['ipssid', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'redcap_data_access_group', 'strage'])
df_rrq_ipss = renameColumns(df_rrq_ipss, suffix='_rename_rrq_ipss')
df_out_ipss = renameColumns(df_out_ipss, suffix='_rename_out_ipss')
df_soi_psom2 = renameColumns(df_soi_psom2, suffix='_rename_soi_psom2')

# Merge all data together
df_all = df_fup_sips2
print len(df_all)
df_all = df_all.merge(df_rrq_ipss, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'assedat_rename_rrq_ipss'])
print len(df_all)
df_all = df_all.merge(df_out_ipss, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'fuionset_rename_out_ipss'])
print len(df_all)
df_all = df_all.merge(df_soi_psom2, how='left', left_on=['ipssid', 'date_v2_rename_fup_sips2'], right_on=['ipssid', 'fuionset_soi_rename_soi_psom2'])
print len(df_all)
df_all.to_excel('/Users/steven ufkes/Documents/stroke/data_packages/2019-09_SIPS_final_data_package/df_all.xlsx', encoding='utf-8', index=False)

# Split data back into separate forms


# Use SIPS event names to rename all of the variables
