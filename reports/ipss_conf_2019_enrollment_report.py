#!/usr/bin/env python

## Import modules
# Standard modules
import os, sys, argparse
import csv
from pprint import pprint

# Non-standard modules
import redcap, pandas

# My modules in current directory
from getIPSSIDs import getIPSSIDs

# My modules in other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.Color import Color
from misc.exportRecords import exportRecords
from misc.getRecordIDList import getRecordIDList
from misc.getDAGs import getDAGs

def addDAGInfo(report_df, path_dag_info):
    """This function adds columns for institution name and country Pandas DataFrames with DAG as the 
    index."""
    # Get list of column headers for rearrangement later.
    column_headers_old = list(report_df)
    
    # Add columns for DAG institution name and country.
    dag_info_df = pandas.read_csv(path_dag_info, index_col=0)
    dag_info_headers = list(dag_info_df)
    report_df = report_df.join(dag_info_df).fillna('')
    
    # Rearrange columns so that dag, institiution name, and country are first.
    column_headers_new = dag_info_headers
    column_headers_new.extend(column_headers_old)

    report_df = report_df.reindex(columns=column_headers_new)
    return report_df

## Define functions to generate data and write reports.
def getPatientInfo(url_arch, url_ipss, key_arch, key_ipss):
    ## Get list of record IDs for each project. Exclude registry-only patients. Exclude patients with unknown stroke type.
#    record_ids_arch = getRecordIDList(url_arch, key_arch)
#    registry_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids_arch, fields=["registry"], events=["acute_arm_1"])
#    for row in registry_arch:
#        if (row["registry"] == "1"):
#            record_ids_arch.remove(row["pk_patient_id"])
#    record_ids_ipss = getRecordIDList(url_ipss, key_ipss)
#    registry_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, fields=["substud"], events=["acute_arm_1"])
#    for row in registry_ipss:
#        if (row["substud___8"] == "1"):
#            record_ids_ipss.remove(row["ipssid"])
#    record_ids_ipss_only = [record_id for record_id in record_ids_ipss if not record_id in record_ids_arch]
#    for record_id in record_ids_arch:
#        if (not record_id in record_ids_ipss):
#            print "Record with ID", record_id, "in Archive, but not in IPSS"

    # Create one list of record ID which are non-registry and have known stroke type.
    record_ids = getIPSSIDs(inc_registry_only=False, inc_unknown_stroke_type=False)

    ## Create dict with patient information: {record_id: {dag:"...", enroll_date:"...", ...} }
    patient_info = {}
    for record_id in record_ids: # add item (another dict) for each patient in the Archive
        patient_info[record_id] = {}
#        patient_info[record_id]["in_arch"] = True
#        if (record_id in record_ids_ipss):
#            patient_info[record_id]["in_ipss"] = True # boolean describing presence of record in Archive
#        else:
#            patient_info[record_id]["in_ipss"] = False # boolean describing presence of record in IPSS
#    for record_id in record_ids_ipss_only: # add item (another dict) for each patient in the IPSS that has not yet been added.
#        patient_info[record_id] = {}
#        patient_info[record_id]["in_arch"] = False
#        patient_info[record_id]["in_ipss"] = True
    

    ## Get enrollment date for each record.
    # Archive - Use 'dateofentry', then 'visit_date".
#    print "Project        : Archive"
    dateofentry_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids, fields=["dateofentry"], events=["acute_arm_1"])
#    if (len(record_ids_arch) != len(dateofentry_arch)): # look for record id missing from exported data
#        for record_id in record_ids_arch:
#            id_in_data = False
#            for row in dateofentry_arch:
#                if (row["pk_patient_id"] == record_id):
#                    id_in_data = True
#                    break
#            if (not id_in_data):
#                print "Record with ID "+str(record_id)+" not found in exported data"
#    num_missing = 0 
    for row in dateofentry_arch:
        if (row["dateofentry"] == ""):
#            num_missing += 1
            pass
        else:
            if ("enroll_date" in patient_info[row["pk_patient_id"]]):
                print "This record was counted twice: "+str(row["pk_patient_id"])
                continue
            patient_info[row["pk_patient_id"]]["enroll_date"] = int(row["dateofentry"][:4])

    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])
   
#    print "Field used     : dateofentry"
#    print "Number missing : ", num_missing
    
    record_ids_leftover = [id for id in record_ids if (not "enroll_date" in patient_info[id])]
    visit_date_leftover = exportRecords(url_arch, key_arch, record_id_list=record_ids_leftover, fields=["visit_date"], events=["acute_arm_1"])
#    num_missing = 0
    for row in visit_date_leftover:
        if (row["visit_date"] == ""):
#            num_missing += 1
            pass
        else:
            if ("enroll_date" in patient_info[row["pk_patient_id"]]):
                print "This record was counted twice: "+str(row["pk_patient_id"])
                continue
            patient_info[row["pk_patient_id"]]["enroll_date"] = int(row["visit_date"][:4]) 
    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])
   
#    print "Field used     : visit_date"
#    print "Number missing : ", num_missing
    
    # IPSS - use 'dateentered' (works for all but 6 patients).
#    print
#    print "Project        : IPSS"
    record_ids_leftover = [id for id in record_ids if (not "enroll_date" in patient_info[id])]
    dateentered_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_leftover, fields=["dateentered"], events=["acute_arm_1"])
#    if (len(record_ids_ipss_only) != len(dateentered_ipss)): # look for record id missing from exported data
#        for record_id in record_ids_ipss_only:
#            id_in_data = False
#            for row in dateentered_ipss:
#                if (row["ipssid"] == record_id):
#                    id_in_data = True
#                    break
#            if (not id_in_data):
#                print "Record with ID "+str(record_id)+" not found in exported data"    
#    num_missing = 0
    for row in dateentered_ipss:
        if (row["dateentered"] == ""):
#            num_missing += 1
            pass
        else:
            if ("enroll_date" in patient_info[row["ipssid"]]):
                print "This record was counted twice: "+str(row["ipssid"])
                continue
            patient_info[row["ipssid"]]["enroll_date"] = int(row["dateentered"][:4])
    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])
#    print "Field used     : dateentered"
#    print "Number missing : ", num_missing

    enroll_dates = set()
    for id, info in patient_info.iteritems():
        if ('enroll_date' in info):
            enroll_dates.add(info['enroll_date'])
            if (not info['enroll_date'] in range(2003, 2020)):
                print "Record enroll date outside [2003, 2019]:", id
        else:
            print "Record with no enrollment date:", id
#    print "enroll_dates:", sorted(list(enroll_dates))
    
    ## Get DAG for each record:
    dags_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids, fields=["pk_patient_id"])
    dags_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids, fields=["ipssid"])
    for row in dags_arch:
        record_id = row["pk_patient_id"]
        dag = row["redcap_data_access_group"]
        patient_info[record_id]["dag"] = dag
    for row in dags_ipss:
        record_id = row["ipssid"]
        dag = row["redcap_data_access_group"]
        if (not "dag" in patient_info[record_id]) or (patient_info[record_id]["dag"] == ""): # add DAG from IPSS if not added already
            patient_info[record_id]["dag"] = dag # overwriting DAG for records in Archive should not be a problem.
    
#    for id in patient_info:
#        if (not "dag" in patient_info[id]) or (patient_info[id]["dag"] == ""):
#            print "Record with ID", id, "does not have a DAG assigned"
        
    
    ## Get stroke type for each patient. # Need to decide how we want to break this down further.
#    stroke_type_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids_arch, fields=["ais", "csvt", "pperi", "preart", "other_stroke", "age_at_event"], events=["acute_arm_1"])
    stroke_type_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids, fields=["chais", "chcsvt", "neoais", "neocsvt", "ppis", "ppcsvt", "pvi", "preart", "othcond"], events=["acute_arm_1"])

    for record_id in patient_info:
        patient_info[record_id]["stroke_type"] = {}
        patient_info[record_id]["stroke_type"]["neo_ais"] = "2"
        patient_info[record_id]["stroke_type"]["neo_csvt"] = "2"
        patient_info[record_id]["stroke_type"]["child_ais"] = "2"
        patient_info[record_id]["stroke_type"]["child_csvt"] = "2"
        patient_info[record_id]["stroke_type"]["pp_ais"] = "2"
        patient_info[record_id]["stroke_type"]["pp_csvt"] = "2"
        patient_info[record_id]["stroke_type"]["pp_vi"] = "2"
        patient_info[record_id]["stroke_type"]["art"] = "2"
        patient_info[record_id]["stroke_type"]["other"] = "2"

    for row in stroke_type_ipss: # 0 - no, 1 - yes, 2 - unknown
        record_id = row["ipssid"]
        # neonatal AIS
        patient_info[record_id]["stroke_type"]["neo_ais"] = row["neoais___1"]
        # neonatal CSVT
        patient_info[record_id]["stroke_type"]["neo_csvt"] = row["neocsvt___1"]
        # child AIS
        patient_info[record_id]["stroke_type"]["child_ais"] = row["chais___1"]
        # child CSVT
        patient_info[record_id]["stroke_type"]["child_csvt"] = row["chcsvt___1"]
        # presumed perinatal AIS
        patient_info[record_id]["stroke_type"]["pp_ais"] = row["ppis___1"]
        # presumed perinatal CSVT
        patient_info[record_id]["stroke_type"]["pp_csvt"] = row["ppcsvt___1"]
        # presumed perinatal VI
        patient_info[record_id]["stroke_type"]["pp_vi"] = row["pvi___1"]
        # arteriopathy
        patient_info[record_id]["stroke_type"]["art"] = row["preart___1"]
        # other
        patient_info[record_id]["stroke_type"]["other"] = row["othcond___1"]

    # Look for patients without an identified stroke type.
    record_ids_with_unidentified_stroke_type = []
    for id, record in patient_info.iteritems():
        identified_type = False
        for stroke_type, value in record["stroke_type"].iteritems():
            if (value == "1"):
                identified_type = True
                break
        if (not identified_type):
#            print "Record with ID", id, "has an unidentified stroke type."
            record_ids_with_unidentified_stroke_type.append(id)
    
    # Check if stroke type can be identified in Archive instead.
#    stroke_type_arch_leftover = exportRecords(url_arch, key_arch, record_id_list=record_ids_with_unidentified_stroke_type, fields=["ais", "csvt", "pperi", "preart", "other_stroke", "age_at_event"], events=["acute_arm_1"])
#    for row in stroke_type_arch_leftover:
#        print row["pk_patient_id"], row["ais"], row["csvt"], row["pperi"], row["preart"], row["other_stroke"]#, row["age_at_event"]
#        stroke_type_found = False
#        if (row["ais"] == "1") and (row["age_at_event"] == "0"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["neo_ais"] = "1"
#            stroke_type_found = True
#        if (row["csvt"] == "1") and (row["age_at_event"] == "0"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["neo_csvt"] = "1"
#            stroke_type_found = True
#        if (row["ais"] == "1") and (row["age_at_event"] == "1"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["child_ais"] = "1"
#            stroke_type_found = True
#        if (row["csvt"] == "1") and (row["age_at_event"] == "1"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["child_csvt"] = "1"
#            stroke_type_found = True
#        if (row["preart"] == "1"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["art"] = "1"
#            stroke_type_found = True
#        if (row["other_stroke"] == "1"):
#            patient_info[row["pk_patient_id"]]["stroke_type"]["other"] = "1"
#            stroke_type_found = True
#        if stroke_type_found:
#            record_ids_with_unidentified_stroke_type.remove(row["pk_patient_id"])

    # Print some stats on the acquired patient information.
    num_no_year = 0
    num_no_dag = 0
    for record_id, record in patient_info.iteritems():
        if (record["dag"] == ""):
            num_no_dag += 1 
        if (not "enroll_date" in record):
            num_no_year += 1
    print "Number of duplicated record IDs:", len(record_ids) - len(set(record_ids))
    print "Number of unique record IDs:", len(set(record_ids))
    print "Number of record IDs in patient_info:", len(patient_info)
    print "Number of records with no DAG:", num_no_dag
    print "Number of records with no enrollment date:", num_no_year
    print "Number of records with unidentified stroke type:", len(record_ids_with_unidentified_stroke_type)    
    return patient_info

# User reports
def getUserInfo(url_ipss, key_ipss):
    # Load IPSS logging data. Doesn't seem to have complete data on when users were added, so I won't use it for now.
    log_path_ipss_1 = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_1_log.csv" # IPSS version 1 (archived)
    log_path_ipss_2 = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_2_log.csv" # IPSS version 2 (archived)
    log_path_ipss_3 = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_3_log.csv" # IPSS version 3 (current version)
    df_1 = pandas.read_csv(log_path_ipss_1)
    df_2 = pandas.read_csv(log_path_ipss_2)
    df_3 = pandas.read_csv(log_path_ipss_3)
    log_list = [df_1, df_2, df_3]
    
    users = redcap.Project(url_ipss, key_ipss).export_users()
    user_info = {} # {username: {dag:"...", year_added:"...", ...}, ...}
    for user in users:
        username = user["username"]
        user_info[username] = {}
        user_info[username]["dag"] = user["data_access_group"]
        user_info[username]["current"] = True
        user_info[username]["action_dates"] = set()
    
    # Julie Paterson is the one person not accounted for in the logs for any of IPSS 1, 2, or 3. Add her manually here.
    user_info["julie.paterson"] = {}
    user_info["julie.paterson"]["dag"] = ""
    user_info["julie.paterson"]["current"] = False
    user_info["julie.paterson"]["year_added"] = 2014
    user_info["julie.paterson"]["action_dates"] = set()

    # Store list of unidentified users who performed actions noted in the log, but will not be added as project users. Most of these are REDCap administrators.
    redcap_admins = set()

    # Get get the year each user was added.
    for df in log_list:    
#        for index in reversed(range(len(df))): # Reverse to read in order or occurrence.
        for index in df.index[::-1]:
            user_action = str(df["Username"][index]).lower()
            action = str(df["Action"][index])
            date_time = str(df["Time / Date"][index])
            date = date_time[:4]+date_time[5:7]+date_time[8:10]
#            print date, user_action
            changes = str(df["List of Data Changes OR Fields Exported"][index])
            if ("Created User" in action):
                year = date_time[:4]
                username = action.split()[-1].lower()
                if (not username in user_info):
                    user_info[username] = {}
                    user_info[username]["current"] = False
#                    user_info[username]["dag"] = "Unknown"
                user_info[username]["year_added"] = int(year)
                user_info[username]['action_dates'] = set()
            if ("Assign user to data access group" in changes): # Look for DAG assignment in log.
                username = changes.split("'")[1].lower()
                dag = changes.split("'")[3].lower()
                user_info[username]["dag"] = dag 
#                print changes, username, dag
            # Add date of user's action to action_dates
            if (not(user_action) in user_info.keys()):
                if (not user_action in redcap_admins):
                    redcap_admins.add(user_action)
                    print "Warning: Unidentified user performed an action. Assume it is a REDCap administrator, and do not include in report:", user_action
                continue
            if (not 'action_dates' in user_info[user_action].keys()):
                user_info[user_action]['action_dates'] = set()
                user_info[user_action]['action_dates'].add(int(date))
            else:
                user_info[user_action]['action_dates'].add(int(date))

    dag_path_ipss_1 = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_1_dags.csv"
    dag_path_ipss_2 = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_2_dags.csv"
    df_dag_1 = pandas.read_csv(dag_path_ipss_1).astype(str)
    df_dag_2 = pandas.read_csv(dag_path_ipss_2).astype(str)
    for df in [df_dag_1, df_dag_2]:
        for index in range(len(df)):
            username = str(df["user"][index]).split()[0].strip(",")
            dag = df["dag"][index]
            if (username == "nan"): # if DAG has no users in log, skip to next entry.
                continue
            # Add DAG info to user if currently unknown.
            if (not username in user_info):
                print "Unidentified user:", username
            if (not "dag" in user_info[username]) or (user_info[username]["dag"] == ""): # only set if currently unassigned
                if (dag == "nan"):
                    user_info[username]["dag"] = ""
                else:
                    user_info[username]["dag"] = dag

    # Delete fake/test/invalid users.
    exclusion_list = ["ipsstest1", "ipsstest2", "ipsstest3", "kathleen.colao@ucsf.edu", "Kathleen.Colao@ucsf.edu", "susan.dang", "hojun.lim", "daniel.ostromich", "michele.petrovic", "priyanka.shah", "philip.alexander", "justin.foong", "allyssa.johnston", "shun.cheung", "ashley.schipani", "kathryn.sievers", "anissa.mumin", "furqan.syed", "amanda.robertson", "michael.choi"]
    for username in exclusion_list:
        if username in user_info.keys():
            del user_info[username]

    # Count users with known creation dates.
    num_year_known = 0
    num_dag_known = 0
    for username, info in user_info.iteritems():
        if ("year_added" in info):
            num_year_known += 1
        if ("dag" in info):
            num_dag_known += 1
            if (info["dag"] == ""):
#                print "User without DAG assigned:", username
                pass
        else: # Users with as yet undetermined DAGs probably had their username deleted, but still appear in the logs.
            user_info[username]["dag"] = ""
#            print "User with missing DAG information:", username
            pass
    print "Number of users:", len(user_info)
    print "Number of users with known start date:", num_year_known
    print "Number of users with known DAG:", num_dag_known

    return user_info

def reportPatientInfo(patient_info, out_dir, path_dag_info):
    ## Miscellaneous items used in all of the enrollment reports
    min_year = 2003
    max_year = 2019
    year_list = range(min_year, max_year+1)

    records_ipss = exportRecords(url_ipss, key_ipss, fields=["ipssid"])
    dags = getDAGs(records_ipss)[1]
    # Put "Unassigned" at end of list.
    dags_old = dags
    dags = sorted(dags_old)[1:]
    dags.extend(sorted(dags_old)[:1])


    # Check if all records belong to one of the DAGs in the list just created.
    for record_id, record in patient_info.iteritems():
        if (not record["dag"] in dags):
            print "Record with ID", record_id, "in DAG",record[dag],"is part of unidentified DAG."

    # Enrollment by site per year
    report_path = os.path.join(out_dir, "enrollment_dag.csv")    

    # Write row/column headings
    columns = year_list    
    index = [dag if (dag != "") else "Unassigned" for dag in dags]

    # Create pandas DataFrame to store report.
    report_df = pandas.DataFrame(columns=columns, index=index)

    # Add row for each DAG.
    for dag in dags:
        if (dag != ""):
            dag_name = dag
        else:
            dag_name = "Unassigned"
        for year in year_list:
            num_enrolled_dag_year = 0
            for record_id, record in patient_info.iteritems():
                if ("enroll_date" in record) and (type(record["enroll_date"]) != type(year)): 
                    print "WARNING: comparison of different types in 'enroll_date'."
                if (record["dag"] == dag) and ("enroll_date" in record) and (record["enroll_date"] == year):
                    num_enrolled_dag_year += 1
            report_df[year][dag_name] = num_enrolled_dag_year

    # Add columns/rows to store column/row totals.
    report_df["Total"] = report_df.sum(axis=1).astype(int) # Total column
    report_df = report_df.append(report_df.sum(axis=0).astype(int).rename("Total")) # Total row

    # Add instition name and country columns to dataframe.
    report_df = addDAGInfo(report_df, path_dag_info)

    report_df.to_csv(report_path)
    print report_df

    ## Enrollment by stroke type per year
    report_path = os.path.join(out_dir, "enrollment_stroke_type.csv")
    
    # Write row/column headings
    columns = year_list
    index = ["Neonatal AIS", "Neonatal CSVT", "Neonatal AIS & CSVT", "Childhood AIS", "Childhood CSVT", "Childhood AIS & CSVT", "Presumed perinatal AIS", "Presumed perinatal CSVT", "Presumed perinatal AIS & CSVT", "Presumed perinatal VI", "Arteriopathy", "Other"]
    
    report_df = pandas.DataFrame(0, columns=columns, index=index)
    
    # Add each patient with known stroke type to report.
    for id, record in patient_info.iteritems():
        if ("enroll_date" in record) and (record["enroll_date"] in columns): # If enrollment date is known and included in the report.
            year = record["enroll_date"]
            if (record["stroke_type"]["neo_ais"] == "1") and (record["stroke_type"]["neo_csvt"] == "1"):
                report_df[year]["Neonatal AIS & CSVT"] += 1
            elif (record["stroke_type"]["neo_ais"] == "1"):
                report_df[year]["Neonatal AIS"] += 1
            elif (record["stroke_type"]["neo_csvt"] == "1"):
                report_df[year]["Neonatal CSVT"] += 1
            elif (record["stroke_type"]["child_ais"] == "1") and (record["stroke_type"]["child_csvt"] == "1"):
                report_df[year]["Childhood AIS & CSVT"] += 1
            elif (record["stroke_type"]["child_ais"] == "1"):
                report_df[year]["Childhood AIS"] += 1
            elif (record["stroke_type"]["child_csvt"] == "1"):
                report_df[year]["Childhood CSVT"] += 1
            elif (record["stroke_type"]["pp_ais"] == "1") and (record["stroke_type"]["pp_csvt"] == "1"):
                report_df[year]["Presumed perinatal AIS & CSVT"] += 1
            elif (record["stroke_type"]["pp_ais"] == "1"):
                report_df[year]["Presumed perinatal AIS"] += 1
            elif (record["stroke_type"]["pp_csvt"] == "1"):
                report_df[year]["Presumed perinatal CSVT"] += 1
            elif (record["stroke_type"]["pp_vi"] == "1"):
                report_df[year]["Presumed perinatal VI"] += 1
            elif (record["stroke_type"]["art"] == "1"):
                report_df[year]["Arteriopathy"] += 1
            elif (record["stroke_type"]["other"] == "1"):
                report_df[year]["Other"] += 1

    report_df["Total"] = report_df.sum(axis=1).astype(int) # Total column
    report_df = report_df.append(report_df.sum(axis=0).astype(int).rename("Total")) # Total row
    report_df.to_csv(report_path)            
    print report_df
           
    return

def reportUserInfo(user_info, out_dir, path_dag_info):
    # Users per DAG
    report_path = os.path.join(out_dir, "user_dag.csv")

    ## Miscellaneous items used in the user information report.
    min_year = 2014
    max_year = 2019
    year_list = range(min_year, max_year+1)

    # Get alphabetized DAG list. Put unassigned at the end of the list.
    dags_unsorted = [] # Could include dags not present in current IPSS. Do it this way to be safe.
    for username, info in user_info.iteritems():
        dag = info["dag"]
        if (not dag in dags_unsorted):
            dags_unsorted.append(dag)

    dags = sorted(dags_unsorted)[1:]
    dags.extend(sorted(dags_unsorted)[:1])

    # Write column, row headings.
    columns = year_list
    index = [dag if (dag != "") else "Unassigned" for dag in dags]

    # Create report.
    report_df = pandas.DataFrame(columns=columns, index=index)

    # Add row for each DAG.
    for dag in dags:
        if (dag != ""):
            dag_name = dag
        else:
            dag_name = "Unassigned"
        for year in year_list:
            num_added_dag_year = 0
            for username, info in user_info.iteritems():
                if (not 'year_added' in info):
#                    print "User with no year_added:", username
                    continue
                if (type(info["year_added"]) != type(year)):
                    print "WARNING: Comparison of different types in 'year_added'"
                if (info["dag"] == dag) and (info["year_added"] == year):
                    num_added_dag_year += 1
            report_df[year][dag_name] = num_added_dag_year

    for username, info in user_info.iteritems():
        if (not 'year_added' in info):
            print "User with no 'year_added':", username

    report_df["Total"] = report_df.sum(axis=1).astype(int) # Total column
    report_df = report_df.append(report_df.sum(axis=0).astype(int).rename("Total")) # Total row

    # Add instition name and country columns to dataframe.
    report_df = addDAGInfo(report_df, path_dag_info)

    report_df.to_csv(report_path)
    print report_df

    return

def reportUserInfo_TAF20190912(user_info, out_dir, path_dag_info):
    # This is a sketchy hacked version of reportUserInfo() which was hastily assembled to complete the task:
    
    # Users per DAG
    report_path = os.path.join(out_dir, "user_dag_TAF20190912.csv")

    ## Miscellaneous items used in the user information report.
 #   min_year = 2014
 #   max_year = 2019
 #   year_list = range(min_year, max_year+1)

    # Get alphabetized DAG list. Put unassigned at the end of the list.
    dags_unsorted = [] # Could include dags not present in current IPSS. Do it this way to be safe.
    for username, info in user_info.iteritems():
        dag = info["dag"]
        if (not dag in dags_unsorted):
            dags_unsorted.append(dag)

    dags = sorted(dags_unsorted)[1:]
    dags.extend(sorted(dags_unsorted)[:1])

    # Write column, row headings.
 #   columns = year_list
    columns = ['number_of_active_users_in_TAF_period']
    index = [dag if (dag != "") else "Unassigned" for dag in dags]

    # Create report.
    report_df = pandas.DataFrame(columns=columns, index=index)
    report_df['active_users_in_TAF_period'] = ''

    # Add row for each DAG.
    for dag in dags:
        if (dag != ""):
            dag_name = dag
        else:
            dag_name = "Unassigned"
 #       for year in year_list:
        num_added_dag_year = 0
        for username, info in user_info.iteritems():
#            if (not 'year_added' in info):
#                    print "User with no year_added:", username
#                continue
#            if (type(info["year_added"]) != type(year)):
#                print "WARNING: Comparison of different types in 'year_added'"
            if (info["dag"] == dag):
                if (not 'action_dates' in info.keys()):
                    print "WARNING: user does not have action_dates:", username
                    continue
                for action_date in info['action_dates']:
                    if (20180701 < action_date) and (action_date < 20190630):
#                        print "Found TAF action"
                        num_added_dag_year += 1
                        report_df['active_users_in_TAF_period'][dag_name] += username + ' '
                        break
                    else:
#                        print username, action_date
                        pass
        report_df['number_of_active_users_in_TAF_period'][dag_name] = num_added_dag_year

    for username, info in user_info.iteritems():
        if (not 'action_dates' in info):
            print "User with no 'action_dates':", username

    report_df.append(pandas.Series(name='Total'))
    report_df.loc['Total', 'number_of_active_users_in_TAF_period'] = report_df['number_of_active_users_in_TAF_period'].sum(axis=0)

    # Add instition name and country columns to dataframe.
    report_df = addDAGInfo(report_df, path_dag_info)

    report_df.to_csv(report_path)
    print report_df

    return

## Create argument parser.
description = """This script automatically generates the following reports:
  - number of patients enrollled per year per DAG
  - cumulative number of patients entrolled per year per DAG
  - number of AIS, CSVT etc. patients enrollled per year (per DAG?)
  - number of users per DAG
  - number of users in REDCap per year

Schematic:
1. Compile list of record IDs in Archive and IPSS
2. Assign an enrolllment date to each ID according to the following rules:
  - Archive: Try 'dateofentry', then another variable, then logging data if needed.
  - IPSS: Try 'dateentered', then date of clinical onsent, then another variable, then logging data if needed.
3. Create reports
4. Export users
5. Create reports"""
parser = argparse.ArgumentParser(description=description)

# Define optional arguments.
default_in_path = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/api_url_key_list.txt"
default_out_dir = "/Users/steven ufkes/Documents/stroke/ipss/auto-reports/"
parser.add_argument("-i", "--in_path", help="path to text file containing API URLs and keys for projects to generate reports on. File should contain 1 space-separated (API URL, API key) pair per line.", type=str, default=default_in_path)
parser.add_argument("-o", "--out_dir", help="directory to save reports to", type=str, default=default_out_dir)

# Parse arguments.
args = parser.parse_args()

# Build list of API (url, key) tuples.
with open(args.in_path, 'r') as fh:
    try:
        api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
    except IndexError:
        print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
        sys.exit()

# Get API URL and key for Archive and IPSS.
url_arch = api_pairs[0][0]
url_ipss = api_pairs[1][0]

key_arch = api_pairs[0][1]
key_ipss = api_pairs[1][1]

## Generate data and write report
# Get information about the IPSS DAGs to include in reports.
path_dag_info = '/Users/steven ufkes/Documents/stroke/ipss/auto-reports/ipss_dag_info.csv'
#dag_info = getDAGInfo(path_dag_info)

# Patient enrollment information
#patient_info = getPatientInfo(url_arch, url_ipss, key_arch, key_ipss)
#reportPatientInfo(patient_info, args.out_dir, path_dag_info)

# User information
user_info = getUserInfo(url_ipss, key_ipss)

#print user_info['steven.ufkes']['action_dates']
#reportUserInfo(user_info, args.out_dir, path_dag_info)
reportUserInfo_TAF20190912(user_info, args.out_dir, path_dag_info)
