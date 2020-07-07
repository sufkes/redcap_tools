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
from misc.ApiSettings import ApiSettings

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
def getPatientInfo(url_arch, url_ipss, key_arch, key_ipss, enroll_date_min=2003, enroll_date_max=2020):
    # Create one list of record ID which are non-registry and have known stroke type.
    #record_ids = getIPSSIDs(ex_registry_only=True, ex_unknown_stroke_type=True, from_code_name="ipss_v3")
    #print "DEBUG: CHANGE getIPSSIDs arguments back to IPSS V4."
    record_ids = getIPSSIDs(ex_registry_only=True, ex_unknown_stroke_type=True)


    ## Create dict with patient information: {record_id: {dag:"...", enroll_date:"...", ...} }
    patient_info = {}
    for record_id in record_ids: # add item (another dict) for each patient in the Archive
        patient_info[record_id] = {}

    ## Get enrolment date for each record.
    # Archive - Use 'dateofentry', then 'visit_date".
    dateofentry_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids, fields=["dateofentry"], events=["acute_arm_1"], validate=False)
    for row in dateofentry_arch:
        if (row["dateofentry"] == ""):
            pass
        else:
            if ("enroll_date" in patient_info[row["pk_patient_id"]]):
                print "This record was counted twice: "+str(row["pk_patient_id"])
                continue
            patient_info[row["pk_patient_id"]]["enroll_date"] = int(row["dateofentry"][:4])

    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])
   
    record_ids_leftover = [id for id in record_ids if (not "enroll_date" in patient_info[id])]
    visit_date_leftover = exportRecords(url_arch, key_arch, record_id_list=record_ids_leftover, fields=["visit_date"], events=["acute_arm_1"], validate=False)
    for row in visit_date_leftover:
        if (row["visit_date"] == ""):
            pass
        else:
            if ("enroll_date" in patient_info[row["pk_patient_id"]]):
                print "This record was counted twice: "+str(row["pk_patient_id"])
                continue
            patient_info[row["pk_patient_id"]]["enroll_date"] = int(row["visit_date"][:4]) 
    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])
   
    # IPSS - use 'dateentered' (works for all but 6 patients).
    record_ids_leftover = [id for id in record_ids if (not "enroll_date" in patient_info[id])]
    dateentered_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_leftover, fields=["dateentered"], events=["acute_arm_1"], validate=False)
    for row in dateentered_ipss:
        if (row["dateentered"] == ""):
            pass
        else:
            if ("enroll_date" in patient_info[row["ipssid"]]):
                print "This record was counted twice: "+str(row["ipssid"])
                continue
            patient_info[row["ipssid"]]["enroll_date"] = int(row["dateentered"][:4])
    num_missing = len([id for id in record_ids if (not "enroll_date" in patient_info[id])])

    enroll_dates = set()
    for id, info in patient_info.iteritems():
        if ('enroll_date' in info):
            enroll_dates.add(info['enroll_date'])
            if (not info['enroll_date'] in range(enroll_date_min, enroll_date_max+1)):
                print "Record enroll date outside ["+str(enroll_date_min)+", "+str(enroll_date_max)+"]:", id
        else:
            print "Record with no enrolment date:", id
    
    ## Get DAG for each record:
    dags_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids, fields=["pk_patient_id"], validate=False)
    dags_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids, fields=["ipssid"], validate=False)
    for row in dags_arch:
        record_id = row["pk_patient_id"]
        dag = row["redcap_data_access_group"]
        patient_info[record_id]["dag"] = dag
    for row in dags_ipss:
        record_id = row["ipssid"]
        dag = row["redcap_data_access_group"]
        if (not "dag" in patient_info[record_id]) or (patient_info[record_id]["dag"] == ""): # add DAG from IPSS if not added already
            patient_info[record_id]["dag"] = dag # overwriting DAG for records in Archive should not be a problem.
    
    ## Get stroke type for each patient. # Need to decide how we want to break this down further.
    #stroke_type_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids, fields=["chais", "chcsvt", "neoais", "neocsvt", "ppis", "ppcsvt", "pvi", "preart", "othcond"], events=["acute_arm_1"])
    stroke_type_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids, fields=["stroke_type"], events=["acute_arm_1"])

    # Set stroke types to unknown initially.
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

        #'chais___1':'stroke_type___1',
        #'chcsvt___1':'stroke_type___2',
        #'neoais___1':'stroke_type___3',
        #'neocsvt___1':'stroke_type___4',
        #'ppis___1':'stroke_type___5',
        #'ppcsvt___1':'stroke_type___6',
        #'pvi___1':'stroke_type___7',
        #'preart___1':'stroke_type___8',
        #'othcond___1':'stroke_type___9'
        
    for row in stroke_type_ipss: # 0 - no, 1 - yes, 2 - unknown
        record_id = row["ipssid"]
        # neonatal AIS
        patient_info[record_id]["stroke_type"]["neo_ais"] = row["stroke_type___3"]
        # neonatal CSVT
        patient_info[record_id]["stroke_type"]["neo_csvt"] = row["stroke_type___4"]
        # child AIS
        patient_info[record_id]["stroke_type"]["child_ais"] = row["stroke_type___1"]
        # child CSVT
        patient_info[record_id]["stroke_type"]["child_csvt"] = row["stroke_type___2"]
        # presumed perinatal AIS
        patient_info[record_id]["stroke_type"]["pp_ais"] = row["stroke_type___5"]
        # presumed perinatal CSVT
        patient_info[record_id]["stroke_type"]["pp_csvt"] = row["stroke_type___6"]
        # presumed perinatal VI
        patient_info[record_id]["stroke_type"]["pp_vi"] = row["stroke_type___7"]
        # arteriopathy
        patient_info[record_id]["stroke_type"]["art"] = row["stroke_type___8"]
        # other
        patient_info[record_id]["stroke_type"]["other"] = row["stroke_type___9"]

    # Look for patients without an identified stroke type.
    record_ids_with_unidentified_stroke_type = []
    for id, record in patient_info.iteritems():
        identified_type = False
        for stroke_type, value in record["stroke_type"].iteritems():
            if (value == "1"):
                identified_type = True
                break
        if (not identified_type):
            record_ids_with_unidentified_stroke_type.append(id)
    
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
    print "Number of records with no enrolment date:", num_no_year
    print "Number of records with unidentified stroke type:", len(record_ids_with_unidentified_stroke_type)    
    return patient_info

def reportPatientInfo(patient_info, out_dir, path_dag_info=None, min_year=2003, max_year=2020):
    ## Miscellaneous items used in all of the enrolment reports
    year_list = range(min_year, max_year+1)

    # Generate a list of DAGs
    dags = set()
    for record_id, record in patient_info.iteritems():
        dag = record["dag"]
        dags.add(dag)
    dags = list(dags)
    
    # Put "" ("Unassigned") at end of list.
    dags_old = dags
    dags = sorted(dags_old)[1:]
    dags.extend(sorted(dags_old)[:1])

    # Enrolment by site per year
    report_path = os.path.join(out_dir, "enrolment_dag.csv")    

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
    if (not path_dag_info is None):
        report_df = addDAGInfo(report_df, path_dag_info)

    report_df.to_csv(report_path)
    print report_df

    ## Enrolment by stroke type per year
    report_path = os.path.join(out_dir, "enrolment_stroke_type.csv")
    
    # Write row/column headings
    columns = year_list
    index = ["Neonatal AIS", "Neonatal CSVT", "Neonatal AIS & CSVT", "Childhood AIS", "Childhood CSVT", "Childhood AIS & CSVT", "Presumed perinatal AIS", "Presumed perinatal CSVT", "Presumed perinatal AIS & CSVT", "Presumed perinatal VI", "Arteriopathy", "Other"]
    
    report_df = pandas.DataFrame(0, columns=columns, index=index)
    
    # Add each patient with known stroke type to report.
    for id, record in patient_info.iteritems():
        if ("enroll_date" in record) and (record["enroll_date"] in columns): # If enrolment date is known and included in the report.
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

def enrollmentReportIPSS(url_arch, url_ipss, key_arch, key_ipss, out_dir, dag_info=None, min_year=2003, max_year=2020):
    # Get enrollment information.
    patient_info = getPatientInfo(url_arch, url_ipss, key_arch, key_ipss, enroll_date_min=min_year, enroll_date_max=max_year)

    # Write enrollment report.
    reportPatientInfo(patient_info, out_dir, dag_info, min_year=min_year, max_year=max_year)
    
if (__name__ == "__main__"):
    # Create instance of ApiSettings class. Use this to the find file containing API keys and URLs.
    api_settings = ApiSettings()
    
    ## Create argument parser.
    description = """This script automatically generates the following reports:
    - number of patients enrollled per year per DAG
    - cumulative number of patients entrolled per year per DAG
    - number of AIS, CSVT etc. patients enrollled per year (per DAG?)

    Schematic:
    1. Compile list of record IDs in Archive and IPSS
    2. Assign an enrolllment date to each ID according to the following rules:
      - Archive: Try 'dateofentry', then another variable, then logging data if needed.
      - IPSS: Try 'dateentered', then date of clinical onsent, then another variable.
    3. Create reports
    4. Export users
    5. Create reports"""

    parser = argparse.ArgumentParser(description=description)

    # Define positional arguments.
    parser.add_argument("out_dir", help="directory to save reports to", type=str)
    
    # Define optional arguments.
    parser.add_argument("-d", "--dag_info", help="path to CSV file containing supplementary information about each data accses group. The columns must be labelled 'dag', 'institution_name', 'country'. If this is provided, the institution name and country will be added to the reports.", type=str)
    parser.add_argument("--min_year", help="earliest enrollment year to report. Default: 2003", type=int, default=2003)
    parser.add_argument("--max_year", help="latest enrollment year to report. Default: 2020", type=int, default=2020)
    
    # Parse arguments.
    args = parser.parse_args()

    # Get API URL and key for Archive and IPSS.
    url_arch, key_arch, code_name_arch = api_settings.getApiCredentials(code_name="ipss_arch")
    url_ipss, key_ipss, code_name_ipss = api_settings.getApiCredentials(code_name="ipss_v4")


    ## Generate data and write report
    enrollmentReportIPSS(url_arch, url_ipss, key_arch, key_ipss, args.out_dir, args.dag_info, args.min_year, args.max_year)
