#!/usr/bin/env python

# Standard modules
import os, sys

# Non-standard modules
import redcap
import pandas

# My modules from current directory
from getIPSSIDs import getIPSSIDs

# My modules from other directories
sufkes_git_repo_dir = "/Users/steven ufkes/scripts" # change this to the path to which the sufkes Git repository was cloned.
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_misc"))
from exportProjectInfo import exportProjectInfo
from getEvents import getEvents
from exportFormEventMapping import exportFormEventMapping
from exportRepeatingFormsEvents import exportRepeatingFormsEvents
from exportFormsOrdered import exportFormsOrdered
from createFormRepetitionMap import createFormRepetitionMap
from parseMetadata import parseMetadata
from exportRecords import exportRecords
from createRecordIDMap import createRecordIDMap
from getDAGs import getDAGs
from createDAGRecordMap import createDAGRecordMap
from exportRecords import exportRecords
from getRecordIDList import getRecordIDList

# Set directory to save report to.
dir_ipss = "/Users/steven ufkes/Documents/stroke/ipss"
dir_report = os.path.join(dir_ipss, "auto-reports")

# Get API URLs and keys.
api_url_key_list_path = os.path.join(dir_ipss, "api_url_key_list.txt")
with open(api_url_key_list_path, 'r') as fh:
    try:
        api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
    except IndexError:
        print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
        sys.exit()
#api_url_arch = api_pairs[0][0]
#api_key_arch = api_pairs[0][1]
api_url_ipss = api_pairs[1][0]
api_key_ipss = api_pairs[1][1]
api_url_psom = api_pairs[2][0]
api_key_psom = api_pairs[2][1]

# Get list of record IDs in IPSS. Exclude SickKids registry-only patients.
#record_ids = getRecordIDList(api_url_ipss, api_key_ipss)
#registry_data = exportRecords(api_url_ipss, api_key_ipss, record_id_list=record_ids, fields=["substud"], events=["acute_arm_1"])
#for row in registry_data:
#    if (row["substud___8"] == "1"):
#        record_ids.remove(row["ipssid"])
record_ids = getIPSSIDs(inc_registry_only=False, inc_unknown_stroke_type=False)
record_ids_post_2014 = getIPSSIDs(inc_registry_only=False, inc_unknown_stroke_type=False, inc_pre_2014=False)
record_ids_non_sk = getIPSSIDs(inc_registry_only=False, inc_unknown_stroke_type=False, inc_sk_patients=False)
record_ids_psom = getIPSSIDs(db="psom", inc_registry_only=False, inc_unknown_stroke_type=False)

# Load REDCap project (a PyCap object).
project = redcap.Project(api_url_ipss, api_key_ipss)
def_field = project.def_field
project_info = exportProjectInfo(api_url_ipss, api_key_ipss)
project_longitudinal = bool(project_info["is_longitudinal"])
project_repeating = bool(project_info["has_repeating_instruments_or_events"])
events = getEvents(project, project_info, project_longitudinal)
metadata_raw = project.export_metadata()
form_event_mapping = exportFormEventMapping(project, project_longitudinal)
repeating_forms_events = exportRepeatingFormsEvents(api_url_ipss, api_key_ipss, project_repeating)
forms = exportFormsOrdered(api_url_ipss, api_key_ipss)
form_repetition_map = createFormRepetitionMap(project_longitudinal, project_repeating, form_event_mapping, repeating_forms_events, forms)
metadata = parseMetadata(def_field, project_info, project_longitudinal, project_repeating, events, metadata_raw, form_event_mapping, repeating_forms_events, forms, form_repetition_map)

# Export records for non-registry-only patients.
#records_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids_arch, label=True)
records = exportRecords(api_url_ipss, api_key_ipss, record_id_list=record_ids, label_overwrite=False, label=True)
#records_post_2014 = exportRecords(api_url_ipss, api_key_ipss, record_id_list=record_ids_post_2014, label_overwrite=False, label=True)
records_post_2014 = [row for row in records if (row["ipssid"] in record_ids_post_2014)]
#records_non_sk = exportRecords(api_url_ipss, api_key_ipss, record_id_list=record_ids_non_sk, label_overwrite=False, label=True)
records_non_sk = [row for row in records if (row["ipssid"] in record_ids_non_sk)]
records_psom = exportRecords(api_url_psom, api_key_psom, record_id_list=record_ids_psom, label_overwrite=False, label=True)


#for row in records:
#    for field_name in ["handfist___1", "respdif___1", "neofeed___1", "tpatype___1", "astranti___1"]:
#        print field_name, row[field_name]


# Remap field names (e.g. fuionset_soi -> fuionset) for PSOM data to be consistent with IPSS.
mapping = {'fuionset_soi': 'fuionset', "psomsen___1": "psomsen___3", "psomsen___2": "psomsen___4", "psomsen___3": "psomsen___5", "psomsen___4": "psomsen___6", "psomsen___5": "psomsen___7", "psomsen___6": "psomsen___8", "psomsen___7": "psomsen___9", "psomsen___8": "psomsen___10", "psomsen___9": "psomsen___11", "psomsen___10": "psomsen___12", "psomsen___11": "psomsen___13", "psomsen___12": "psomsen___14"}
## DOESN'T WORK BECAUSE FUIONSET IS ALSO A VARIABLE IN PSOM.
records_psom_modified = []
for row_index in range(len(records_psom)):
    #records_psom[row_index][map[1]] = records_psom[row_index].pop(map[0])
    row = records_psom[row_index]
    new_row = {}
    # Remap fuionset to something else since it already exists in PSOM.
    key = 'fuionset'
    new_key = 'fuionset_history'
    new_row[new_key] = row[key]

    for key in row:
        if key in mapping:
            new_key = mapping[key]
        else:
            new_key = key
        new_row[new_key] = row[key]
    records_psom_modified.append(new_row)
#    print len(set(row.keys())), len(set(new_row.keys()))
#    print "keys in old not new:", [key for key in row.keys() if (not key in new_row.keys())]
#    print "keys in new not old:", [key for key in new_row.keys() if (not key in row.keys())]
records_psom[:] = records_psom_modified[:]

records_outcome = [] # Outcome PSOM data taken from IPSS (for non-SK patients) and PSOM (for SK patients).
records_outcome.extend(records_non_sk) # IPSS data without SickKids patients
records_outcome.extend(records_psom) # PSOM data

# Create report on completion rates.
report_path = os.path.join(dir_report, "var_completion.csv")

# Write column headings.
columns = ["num_checks", "num_records_checked", "num_checks_with_data", "num_records_complete", "field_completion_rate", "record_completion_rate"]

## Write lists of column headings
# Non-checkbox, non-compsite variables
fields_normal = ["daent", "doe", "motheth", "fatheth", "childeth", "redcap_data_access_group", "gender", "card", "art", "dissprov", "moyaprov", "fcaprov", "vascprov", "artoth", "sickle", "genetsy", "prothrom", "infect", "heatrau", "systhro", "ilnes", "ilnes_acute", "intproc", "othrisk", "abconc", "mentst", "hemi", "ataxia", "visdef", "speedef", "pednihs", "datefu", "assedat", "ppsomsc", 'acutsta', 'neustat', 'neurdef', 'discloc', 'psomdate', 'psomscr']
# Checkbox, non-composite -- at least one option must be selected for completion. While the first option is specified, the entire field (all options) are examined.
fields_cb = ["mothrac___1", "fathrac___1", "childrac___1", "seizur___1", "neudefsp___1", "headach___1", "respdif___1", "neofeed___1", "handfist___1", "fueven___1"]
# Non-checkbox, composite variables -- all subfields must have an entry for completion.
fields_composite = {"age":["doe", "birmont", "biryear"], "dob":["birmont", "biryear"]}
# All-checkbox, composite variables -- at least one subfield must have an entry for completion.
fields_composite_cb = {"stroke_type":["chais___1", "chcsvt___1", "neoais___1", "neocsvt___1", "ppis___1", "ppcsvt___1", "pvi___1", "preart___1", "othcond___1"], "cong_heart_ds":["chd___1", "ahd___1", "cardoth___1"]}
# Radiographic features normal fields. Look at only >2014 records for these.
fields_radio_treat_normal = ["scanty", "inffind", "infnum", "vasimg", "vascfin", "ecass", "csvtinfn", "pstrtrea", "asttpa", "astrtrea"]
fields_radio_treat_cb = ["infsize___1", "artter___1", "infloc___1", "vascim___1", "vaslate___1", "vesseff___1", "csvtimag___1", "csinfloc___1", "csvtloc___1", "tpatype___1", "astranti___1", "anticosp___1"]
# Outcome - PSOM -- Need to look in two databases for this (PSOM for SK patients, IPSS for non-SK patients)
fields_outcome_normal = ['fuionset', 'fpsomr', 'fpsoml', 'fpsomlae', 'fpsomlar', 'fpsomcb', 'totpsom']
fields_outcome_cb = ['psomsen___3']

# Create Pandas DataFrame for report.
report_df = pandas.DataFrame(columns=columns)

def addRow(report_df, field_name, num_checks, num_records_checked, num_full_checks, num_full_records):
    field_name = field_name.split("___")[0]
#    print "Adding row for:", field_name

#    print "num_checks:", num_checks
#    print "num_records_checked:", num_records_checked
#    print "num_full_checks:", num_full_checks
#    print "num_full_records:", num_full_records

    report_df = report_df.append(pandas.Series(name=field_name))
    report_df["num_checks"][field_name] = num_checks
    report_df["num_records_checked"][field_name] = num_records_checked
    report_df["num_checks_with_data"][field_name] = num_full_checks
    report_df["num_records_complete"][field_name] = num_full_records
    report_df["field_completion_rate"][field_name] = float(num_full_checks)/float(num_checks)
    report_df["record_completion_rate"][field_name] = float(num_full_records)/float(num_records_checked)
    return report_df

for var_list in [fields_normal, fields_cb, fields_composite, fields_composite_cb, fields_radio_treat_normal, fields_radio_treat_cb, fields_outcome_normal, fields_outcome_cb]:
    if (var_list in [fields_normal, fields_radio_treat_normal, fields_outcome_normal]):
        if (var_list == fields_normal):
            records_selected = records
        elif (var_list == fields_radio_treat_normal):
            records_selected = records_post_2014
        elif (var_list == fields_outcome_normal):
            records_selected = records_outcome
        else:
            print 'ERROR: Unknown record selection for var_list.'
            continue
        for field_name in var_list:
            # Count filled and empty fields and record IDs.
            num_checks = 0 # number of times check was performed
            num_records = 0 # number of unique record IDs checked
            num_full_checks = 0 # number of times a missing value was found
            ids_checked = [] # record IDs that have been checked
            ids_not_full = [] # records IDs with field missing in at least one row
            for row_index in range(len(records_selected)):
                row = records_selected[row_index]
                id = row["ipssid"]
                value = row[field_name]
                if ("rr_" in value): # if row is hidden by branching logic, or field is not included in row's (event, form, instance).
                    continue
                else:
                    num_checks += 1
                    if (not id in ids_checked):
                        ids_checked.append(id)
                    if (value != ""):
                        num_full_checks += 1
                    elif (not id in ids_not_full):
                        ids_not_full.append(id)
            num_records_checked = len(ids_checked)
            num_full_records = len(ids_checked) - len(ids_not_full)

            # Add row to DataFrame
            report_df = addRow(report_df, field_name, num_checks, num_records_checked, num_full_checks, num_full_records)

    # Non-composite, checkbox fields -- at least one option must be selected for completion.
    elif (var_list in [fields_cb, fields_radio_treat_cb, fields_outcome_cb]):
        if (var_list == fields_cb):
            records_selected = records
        elif (var_list == fields_radio_treat_cb):
            records_selected = records_post_2014
        elif (var_list == fields_outcome_cb):
            records_selected = records_outcome
        else:
            print 'ERROR: Unknown record selection for var_list.'
            continue
        for var_name in var_list:
            num_checks = 0
            num_records = 0
            num_full_checks = 0
            ids_checked = []
            ids_not_full = []
            for row_index in range(len(records_selected)):
                row = records_selected[row_index]
                id = row["ipssid"]
                cb_full = False
                cb_hidden_invalid = True
                # Determine whether checkbox field is filled, or hidden/invalid.
                for cb_field_name in metadata[var_name].choices:
#                    print cb_field_name, row[cb_field_name]
                    if (not "rr_" in row[cb_field_name]): # if the checkbox field is hidden or invalid
                        cb_hidden_invalid = False
                        if (row[cb_field_name] == "1"): # if option is checked
                            cb_full = True
                            break
#                print "Checkbox hidden/invalid:", cb_hidden_invalid
#                print "Checkbox full:", cb_full
                if cb_hidden_invalid:
                    continue
                else:
                    num_checks += 1
                    if (not id in ids_checked):
                        ids_checked.append(id)
                    if cb_full:
                        num_full_checks += 1
                    elif (not id in ids_not_full):
                        ids_not_full.append(id)
            num_records_checked = len(ids_checked)
            num_full_records = len(ids_checked) - len(ids_not_full)
                        
            # Add row to DataFrame
            report_df = addRow(report_df, var_name, num_checks, num_records_checked, num_full_checks, num_full_records)
    
    # Composite, non-checkbox fields - all subfields must be selected for completion.
    elif (var_list in [fields_composite]):
        if (var_list == fields_composite):
            records_selected = records
        else:
            print 'ERROR: Unknown record selection for var_list.'
            continue
        for var_name in var_list:
            num_checks = 0
            num_records = 0
            num_full_checks = 0
            ids_checked = []
            ids_not_full = []
            for row_index in range(len(records_selected)):
                row = records_selected[row_index]
                id = row["ipssid"]
                cv_full = True # all subfields must be filled or else composite variable is considered empty.
                cv_hidden_invalid = True # all subfields must be hidden or else composite variable is considered unhidden.
                # Determine whether composite field is filled, or hidden/invalid.
                for cv_field_name in var_list[var_name]:
                    if (not "rr_" in row[cv_field_name]): # if the checkbox field is hidden or invalid
                        cv_hidden_invalid = False
                        if (row[cv_field_name] == ""): # if option is not empty
                            cv_full = False
                            break
                if cv_hidden_invalid:
                    continue
                else:
                    num_checks += 1
                    if (not id in ids_checked):
                        ids_checked.append(id)
                    if cv_full:
                        num_full_checks += 1
                    elif (not id in ids_not_full):
                        ids_not_full.append(id)
            num_records_checked = len(ids_checked)
            num_full_records = len(ids_checked) - len(ids_not_full)
                        
            # Add row to DataFrame
            report_df = addRow(report_df, var_name, num_checks, num_records_checked, num_full_checks, num_full_records)

    # Composite, checkbox fields -- at least one subfield must be filled in for completion (if subfield is checkbox, at least one option must be selected).
    elif (var_list in [fields_composite_cb]):
        if (var_list == fields_composite_cb):
            records_selected = records
        else:
            print 'ERROR: Unknown record selection for var_list.'
            continue
        for var_name in var_list:
            num_checks = 0
            num_records = 0
            num_full_checks = 0
            ids_checked = []
            ids_not_full = []
            for row_index in range(len(records_selected)):
                row = records_selected[row_index]
                id = row["ipssid"]
                cv_full = False # Assume all subfields are full until an empty one is found.
                cv_hidden_invalid = True # Assume all subfields are hidden until an unhidden one is found.
                # Determine whether checkbox field is filled, or hidden/invalid.
                for sub_field_name in var_list[var_name]: # loop over sub fields (which are of checkbox type)
                    cb_full = False # Assume checkbox subfield is empty until a selected option is found
                    cb_hidden_invalid = True
                    for cb_field_name in metadata[sub_field_name].choices: # loop over subfield options
#                        print cb_field_name, row[cb_field_name]
                        if (not "rr_" in row[cb_field_name]): # if the checkbox field is hidden or invalid
                            cb_hidden_invalid = False
                            if (row[cb_field_name] == "1"): # if option is checked
                                cb_full = True
                                break
#                    print "Checkbox hidden/invalid:", cb_hidden_invalid
#                    print "Checkbox full:", cb_full
                    if (not cb_hidden_invalid): # if an unhidden subfield was found.
                        cv_hidden_invalid = False
                        if cb_full: # if an empty subfield was found
                            cv_full = True
                            break
                if cv_hidden_invalid:
                    continue
                else:
                    num_checks += 1
                    if (not id in ids_checked):
                        ids_checked.append(id)
                    if cv_full:
                        num_full_checks += 1
                    elif (not id in ids_not_full):
                        ids_not_full.append(id)
            num_records_checked = len(ids_checked)
            num_full_records = len(ids_checked) - len(ids_not_full)
                        
            # Add row to DataFrame
            report_df = addRow(report_df, var_name, num_checks, num_records_checked, num_full_checks, num_full_records)

print report_df

# Rename columns pretty for report.
report_df.rename(columns={'num_checks': '# checks', 'num_records_checked': '# records checked', 'num_checks_with_data': '# cells with data', 'num_records_complete':'# records complete', 'field_completion_rate': 'variable completion rate (# cells with data / # checks)', 'record_completion_rate': 'record completion rate (# records complete / # records checked)'}, inplace=True)

report_df.to_csv(report_path)
