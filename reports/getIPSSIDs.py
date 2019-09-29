#!/usr/bin/env python

import os, sys

# My modules in other directories
sufkes_git_repo_dir = "/Users/steven ufkes/scripts" # change this to the path to which the sufkes Git repository was cloned.
sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_misc"))
from exportRecords import exportRecords
from getRecordIDList import getRecordIDList

def getIPSSIDs(db="ipss", inc_registry_only=True, inc_unknown_stroke_type=True, inc_pre_2014=True, inc_sk_patients=True, inc_neonatal_stroke=True, inc_placeholders=True, inc_adult_stroke=True, inc_melas=True, inc_non_ipss=True, inc_non_sips=True, inc_non_sips2=True, inc_non_sips2_cohort1=True, inc_non_sips2_cohort2=True, inc_sips_exclusions=True, inc_sips_exclusions_2=True, inc_patient_info_incomp=True, inc_core_incomplete=True, inc_non_vips_enrolled=True):
    '''
    Parameters:
        db:                       str - database to get IDs from. Allowed values: 'ipss', 'arch', 'psom', 'sips2', 'vips2', 'psom2'
        inc_registry_only:        bool - whether to include IDs of SickKids registry-only patients
        inc_unknown_stroke_type:  bool - whether to include IDs of records with unknown stroke type
        inc_pre_2014:             bool - whether to include IDs of patients enrolled before 2014 based on IPSS 'originalipss' field
        inc_sk_patients:          bool - whether to include IDs of patients with 'hsc' data access group in IPSS
        inc_neonatal_stroke:      bool - whether to include IDs of patients who suffered a neonatal stroke
        inc_placeholders:         bool - whether to include IDs of patients with almost no real data, whose records likely exist as placeholders
        inc_adult_stroke:         bool - whether to include IDs of patients who did not suffer a stroke as a child
        inc_melas:                bool - whether to include IDs patients with MELAS
        inc_non_ipss:             bool - whether to include IDs that do not exist in the IPSS
        inc_non_sips:             bool - whether to include IDs that are not in SIPS I or SIPS II based on the IPSS field 'substud'
        inc_non_sips2:            bool - whether to include IDs that are not in SIPS II
        inc_non_sips2_cohort1     bool - whether to include IDs that are not in SIPS II cohort I
        inc_non_sips2_cohort2     bool - whether to include IDs that are not in SIPS II cohort II
        inc_sips_exclusions:      bool - whether to include SIPS patients that were excluded merely screened based on SIPS II field 'screened'
        inc_sips_exclusions_2:    bool - whether to include SIPS patients that were excluded based screened based on SIPS II field 'screened' and 'actcohortsp'
        inc_patient_info_incomp   bool - whether to include IDs of patients for whom patient_information_complete != 2 (STILL INCLUDE ALL SLCH PATIENTS).
        inc_core_incomplete       bool - whether to include IDs of patients for whom any of the 'core' forms are not marked as complete (core forms, here, include 'patient_information', 'cardiac_arteriopathy_risk_factors', 'other_child_and_neonatal_risk_factors', and 'clinical_presentation')
        inc_non_vips_enrolled:    bool - whether to include patient who are not enrolled in VIPS, based on the condition of the VIPS field vscreen_sfoutc=4.
        
    Returns:
        record_ids:               list - record IDs in the specified database after specified exclusions
    '''


    # Define optional arguments.
    api_pairs_path = "/Users/steven ufkes/Documents/stroke/data_packages/api_url_key_list.txt"

    # Build list of API (url, key) tuples.
    with open(api_pairs_path, 'r') as fh:
        try:
            api_pairs = [(p.split()[0], p.split()[1]) for p in fh.readlines() if (p.strip() != "") and (p.strip()[0] != "#")] # separate lines by spaces; look only at first two items; skip whitespace lines.
        except IndexError:
            print "Error: cannot parse list of API (url, key) pairs. Each line in text file must contain the API url and API key for a single project separated by a space."
            sys.exit()

    # Get API URL and key for each database
    url_arch = api_pairs[0][0]
    url_ipss = api_pairs[1][0]
    url_psom = api_pairs[2][0]
    url_sips2 = api_pairs[3][0]
    url_vips2 = api_pairs[4][0]
    url_psom2 = api_pairs[5][0]

    key_arch = api_pairs[0][1]
    key_ipss = api_pairs[1][1]
    key_psom = api_pairs[2][1]
    key_sips2 = api_pairs[3][1]
    key_vips2 = api_pairs[4][1]
    key_psom2 = api_pairs[5][1]

    # Create lists of record IDs with various exclusions.
    record_ids_arch = getRecordIDList(url_arch, key_arch)
    record_ids_ipss = getRecordIDList(url_ipss, key_ipss)    
    record_ids_psom = getRecordIDList(url_psom, key_psom)
    record_ids_sips2 = getRecordIDList(url_sips2, key_sips2)
    record_ids_vips2 = getRecordIDList(url_vips2, key_vips2)
    record_ids_psom2 = getRecordIDList(url_psom2, key_psom2)

    # Export all data required to determine ID exclusions.
    req_fields_arch = set()
    req_fields_ipss = set()
    req_fields_psom = set()
    req_fields_sips2 = set()
    req_fields_vips2 = set()
    req_fields_psom2 = set()

    req_events_ipss = set()
    req_events_arch = set()
    req_events_psom = set()
    req_events_sips2 = set()
    req_events_vips2 = set()
    req_events_psom2 = set()

    # Generate list of fields & events which must be exported in order to refine the ID lists.
    if (not inc_registry_only) or (not inc_non_sips) or (not inc_non_sips2) or (not inc_non_sips2_cohort1) or (not inc_non_sips2_cohort2):
        req_fields_ipss.update(['substud', 'sip_cohort'])
        req_events_ipss.add('acute_arm_1')
    if (not inc_unknown_stroke_type):
        req_fields_ipss.update(["chais", "chcsvt", "neoais", "neocsvt", "ppis", "ppcsvt", "pvi", "preart", "othcond"])
        req_events_ipss.add('acute_arm_1')
    if (not inc_pre_2014):
        req_fields_ipss.add('originalipss')
        req_events_ipss.add('acute_arm_1')
    if (not inc_sk_patients):
        pass # only need ipssid and redcap_data_access_group
    if (not inc_neonatal_stroke):
        req_fields_ipss.add('strage')
        req_events_ipss.add('acute_arm_1')
    if (not inc_adult_stroke):
        req_fields_ipss.update(['birmont', 'biryear', 'doe', 'daent', 'strage', 'substud'])
        req_events_ipss.add('acute_arm_1')
    if (not inc_melas):
        req_fields_ipss.update(['genetsy', 'genetsys'])
        req_events_ipss.add('acute_arm_1')
    if (not inc_placeholders):
        pass # the data for this filter will be exported separately. 
    if (not inc_sips_exclusions):
        req_fields_sips2.add('screened')
        req_events_sips2.add('confirmation_and_t_arm_1')
    if (not inc_sips_exclusions_2):
        req_fields_sips2.update(['screened', 'actcohortsp'])
        req_events_sips2.update(['confirmation_and_t_arm_1', 'acute_arm_1'])
    if (not inc_patient_info_incomp):
        req_fields_ipss.add('patient_information_complete')
        req_events_ipss.add('acute_arm_1')
    if (not inc_core_incomplete):
        req_fields_ipss.update(['patient_information_complete', 'cardiac_and_arteriopathy_risk_factors_complete', 'other_child_and_neonatal_risk_factors_complete', 'clinical_presentation_complete', 'status_at_discharge_complete'])
        req_events_ipss.add('acute_arm_1')
    if (not inc_non_vips_enrolled):
        req_fields_vips2.add('vscreen_sfoutc')
        req_events_vips2.update(['confirmation_and_t_arm_1', 'confirmation_and_t_arm_2'])

    # Export data required to refine ID lists.
    if (req_fields_arch != set()): # if data is required from Archive
        filter_data_arch = exportRecords(url_arch, key_arch, fields=req_fields_arch, events=req_events_arch)
    if (req_fields_ipss != set()): # if data is required from IPSS
        filter_data_ipss = exportRecords(url_ipss, key_ipss, fields=req_fields_ipss, events=req_events_ipss)
    if (req_fields_psom != set()): # if data is required from PSOM
        filter_data_psom = exportRecords(url_psom, key_psom, fields=req_fields_psom, events=req_events_psom)
    if (req_fields_sips2 != set()): # if data is required from PSOM
        filter_data_sips2 = exportRecords(url_sips2, key_sips2, fields=req_fields_sips2, events=req_events_sips2)
    if (req_fields_vips2 != set()): # if data is required from VIPS V2
        filter_data_vips2 = exportRecords(url_vips2, key_vips2, fields=req_fields_vips2, events=req_events_vips2)
    if (req_fields_psom2 != set()): # if data is required from PSOM V2
        filter_data_psom2 = exportRecords(url_psom2, key_psom2, fields=req_fields_psom2, events=req_events_psom2)

    ## Generate lists of IDs which satisfy certain conditions.
    # Registry only patients. 
    if (not inc_registry_only):
        # Registry-only records based on IPSS data
        # * All patients labelled registry-only in Archive are labelled likewise in IPSS.
        # * All '9203-' patients are labelled registry only in IPSS.
        record_ids_registry_only_ipss = set()
#        registry_data_ipss = exportRecords(url_ipss, key_ipss, fields=["substud"], events=["acute_arm_1"])
#        for row in registry_data_ipss:
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row["substud___8"] == "1") or ('9203-' in id):
                record_ids_registry_only_ipss.add(id)

    # Unknown stroke type based on IPSS data
    if (not inc_unknown_stroke_type):
#        stroke_type_data_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, fields=["chais", "chcsvt", "neoais", "neocsvt", "ppis", "ppcsvt", "pvi", "preart", "othcond"], events=["acute_arm_1"])
        record_ids_known_stroke_type_ipss = set()
#        for row in stroke_type_data_ipss:
        for row in filter_data_ipss:
            if (row["chais___1"] == "1") or (row["chcsvt___1"] == "1") or (row["neoais___1"] == "1") or (row["neocsvt___1"] == "1") or (row["ppis___1"] == "1") or (row["ppcsvt___1"] == "1") or (row["pvi___1"] == "1") or (row["preart___1"] == "1") or (row['othcond___1'] == "1"):
                id = row["ipssid"]
                record_ids_known_stroke_type_ipss.add(id)
        record_ids_unknown_stroke_type_ipss = [id for id in record_ids_ipss if (not id in record_ids_known_stroke_type_ipss)]

    # Patients that have been entered since the launch of IPSS in REDCap from 2014 to present.
    if (not inc_pre_2014):
#        originalipss_data_ipss = exportRecords(url_ipss, key_ipss, fields=["originalipss"], events=["acute_arm_1"])
        record_ids_pre_2014_ipss = set()
#        for row in originalipss_data_ipss:
        for row in filter_data_ipss:
            if (row["originalipss___1"] == '1'):
                id = row["ipssid"]
#                if (not id in record_ids_pre_2014_ipss):
#                    record_ids_pre_2014_ipss.append(id)
                record_ids_pre_2014_ipss.add(id)

    # SickKids patients (based on DAG)
    if (not inc_sk_patients):
#        ipssid_data_ipss = exportRecords(url_ipss, key_ipss, fields=["ipssid"])
        record_ids_sk_ipss = set()
#        for row in ipssid_data_ipss:
        for row in filter_data_ipss:
            if (row["redcap_data_access_group"] == "hsc"):
                id = row['ipssid']
#                if (not id in record_ids_sk_ipss):
#                    record_ids_sk_ipss.append(id)
                record_ids_sk_ipss.add(id)

    # Neonatal stroke based on IPSS data
    if (not inc_neonatal_stroke):
#        stroke_age_data_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, fields=['strage'], quiet=True)
        record_ids_neonatal_ipss = set()
#        for row in stroke_age_data_ipss:
        for row in filter_data_ipss:
            if (row['strage'] == '0'):
                id = row['ipssid']
#                if (not id in record_ids_neonatal_ipss):
#                    record_ids_neonatal_ipss.append(id)
                record_ids_neonatal_ipss.add(id)

    # Non-pediatric stroke (>= 19 years of age at date of stroke)
    if (not inc_adult_stroke):
#        adult_stroke_data_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, fields=['birmont', 'biryear', 'doe', 'daent', 'strage', 'substud'], quiet=True)
        record_ids_adult_stroke = set()
        record_ids_stroke_age_known = set()
#        for row in adult_stroke_data_ipss:
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row['birmont'] != '') and (row['biryear'] != '') and (row['doe'] != ''):
                record_ids_stroke_age_known.add(id)
                stroke_age = float(row['doe'][:4]) + float(row['doe'][5:7])/12 - float(row['biryear']) - float(row['birmont'])/12
                if (stroke_age >= 19.0 + 1.0/12.0): # only year/month of birth is known, so pad cutoff by 1 month.
                    record_ids_adult_stroke.add(id)
#                    print id
            elif (row['birmont'] != '') and (row['biryear'] != '') and (row['daent'] != ''):
                record_ids_stroke_age_known.add(id)
                stroke_age = float(row['daent'][:4]) + float(row['daent'][5:7])/12 - float(row['biryear']) - float(row['birmont'])/12
                if (stroke_age >= 19.0 + 1.0/12.0): # only year/month of birth is known, so pad cutoff by 1 month.
                    record_ids_adult_stroke.add(id)
#                    print id
#            elif (row['strage'] == '0'):
#                record_ids_stroke_age_known.add(id)
#            elif (row['substud___8'] == '1'):
#                record_ids_stroke_age_known.add(id)
#            elif (row['biryear'] != ''):
#                if int(row['biryear']) > 2000:
#                    record_ids_stroke_age_known.add(id)
#            elif (row['biryear'] != '') and (row['doe'] != ''): # no new information.
#                record_ids_stroke_age_known.add(id)
#                stroke_age = float(row['doe'][:4]) + float(row['doe'][5:7])/12 - float(row['biryear'])
#                if (stroke_age > 19.0 + 1.0):
#                    record_ids_adult_stroke_ipss.add(id)
#            elif (row['biryear'] != '') and (row['birmont'] != '') and (row['stk_year'] != ''):
#                record_ids_stroke_age_known.add(id)
#                stroke_age = float(row['stk_year']) - float(row['biryear']) - float(row['birmont'])/12
#                if (stroke_age > 19.0 + 1.0/12.0):
#                    record_ids_adult_stroke_ipss.add(id)
#    print len(record_ids_ipss), len(record_ids_stroke_age_known)
 
    # MELAS patients
    if (not inc_melas):
#        melas_data_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, fields=['genetsy', 'genetsys'], quiet=True)
#        melas_data_arch = exportRecords(url_arch, key_arch, record_id_list=record_ids_arch, fields=['melas'], quiet=True) # Doesn't provide any additional information
        record_ids_melas = set()
#        for row in melas_data_ipss:
        for row in filter_data_ipss:
            id = row['ipssid']
            desc = row['genetsys'].lower()
            if (row['genetsy'] == '1') and (('melas' in desc) or ('mitochondrial encephalopathy' in desc) or ('lactic acidosis' in desc)):
                record_ids_melas.add(id)
#        for row in melas_data_arch: # Doesn't provide any additional information
#            id = row['pk_patient_id']
#            if (row['melas'] == '1'):
#                print id, row['melas']
#                record_ids_melas.add(id)
            
    # Records deemed as placeholders based on condition that they have no data in either the clinical presentation or cardiac risk factors forms.
    if (not inc_placeholders):
        record_ids_nonplaceholders_ipss = set()
        placeholder_data_ipss = exportRecords(url_ipss, key_ipss, record_id_list=record_ids_ipss, forms=['clinical_presentation', 'cardiac_and_arteriopathy_risk_factors'], quiet=True)
        count = 0
        for row in placeholder_data_ipss:
            id = row['ipssid']
            if (id in record_ids_nonplaceholders_ipss):
                continue
            row_has_data = False
            for field, value in row.iteritems():
#                print row['ipssid'], field, value
                if (field in ['ipssid', 'redcap_data_access_group', 'redcap_event_name', 'redcap_repeat_instrument', 'redcap_repeat_instance', 'clinical_presentation_complete', 'cardiac_and_arteriopathy_risk_factors_complete']):
                    continue
                elif ('___' in field): # if it is a checkbox field
                    if (value == '1'): # if checkbox is checked
                        row_has_data = True
                        break
                else:
                    if (value != ''): # if field has data
                        row_has_data = True
                        break
            if row_has_data:
                record_ids_nonplaceholders_ipss.add(id)
        record_ids_placeholders_ipss = [id for id in record_ids_ipss if (not id in record_ids_nonplaceholders_ipss)]

    # SIPS I or SIPS II patients:
    if (not inc_non_sips):
        # SIPS records based on IPSS data
        record_ids_sips_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row["substud___4"] == "1") or (row["substud___6"] == "1"):
                record_ids_sips_ipss.add(id)

    # SIPS II patients
    if (not inc_non_sips2):
        # SIPS2 records based on IPSS data
        record_ids_sips2_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row["substud___4"] == "1"):
                record_ids_sips2_ipss.add(id)

    # SIPS II cohort I patients
    if (not inc_non_sips2_cohort1):
        # SIPS2 cohort I records based on IPSS data
        record_ids_sips2_cohort1_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row["substud___4"] == "1") and (row['sip_cohort'] == '1'):
                record_ids_sips2_cohort1_ipss.add(id)

    # SIPS II cohort II patients
    if (not inc_non_sips2_cohort2):
        # SIPS2 cohort II records based on IPSS data
        record_ids_sips2_cohort2_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row["substud___4"] == "1") and (row['sip_cohort'] == '2'):
                record_ids_sips2_cohort2_ipss.add(id)

    # Patients excluded from SIPS studies based on SIPS II variable 'screened'
    if (not inc_sips_exclusions):
        record_ids_sips_exclusions_sips2 = set()
        for row in filter_data_sips2:
            id = row['ipssid']
            if (row["screened"] in ['1', '3']):
                record_ids_sips_exclusions_sips2.add(id)

    # Patients excluded from SIPS studies based on SIPS II variable 'screened'
    if (not inc_sips_exclusions_2):
        record_ids_sips_exclusions_2_sips2 = set()
        actcohort2_ids = set()
        for row in filter_data_sips2:
            id = row['ipssid']
            if (row["screened"] in ['1']):
                record_ids_sips_exclusions_2_sips2.add(id)
            if (row['actcohortsp'] == '2'):
                actcohort2_ids.add(id)
        for row in filter_data_sips2:
            id = row['ipssid']
            if (id in actcohort2_ids) and (row['screened'] == '3'):
                record_ids_sips_exclusions_2_sips2.add(id)
            
    # Patients for whom patient_information_complete != 2.
    if (not inc_patient_info_incomp):
        print "WARNING: Requested only IDs with patient_information_complete = 2; Including *all* SLCH patients regardless of this field."
        record_ids_patient_information_complete_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row['patient_information_complete'] == '2') or (row['redcap_data_access_group'] == 'slch'):
                record_ids_patient_information_complete_ipss.add(id)

    # Patients for whom any of the "core" forms are not marked as complete
    if (not inc_core_incomplete):
        record_ids_core_incomplete_ipss = set()
        for row in filter_data_ipss:
            id = row['ipssid']
            if (row['patient_information_complete'] != '2') or (row['cardiac_and_arteriopathy_risk_factors_complete'] != '2') or (row['other_child_and_neonatal_risk_factors_complete'] != '2') or (row['clinical_presentation_complete'] != '2'):# or (row['status_at_discharge_complete'] != '2'):
                record_ids_core_incomplete_ipss.add(id)

    # Patients who are enrolled in VIPS.
    if (not inc_non_vips_enrolled):
        record_ids_vips_enrolled = set()
        for row in filter_data_vips2:
            id = row['ipssid']
            if (row['vscreen_sfoutc'] == '4'):
                record_ids_vips_enrolled.add(id)

    ## Exclude IDs based on request. 
    if (db == "ipss"):
        record_ids = record_ids_ipss
    elif (db == "arch"):
        record_ids = record_ids_arch
    elif (db == "psom"):
        record_ids = record_ids_psom
    elif (db == "sips2"):
        record_ids = record_ids_sips2
    elif (db == "vips2"):
        record_ids = record_ids_vips2
    elif (db == "psom2"):
        record_ids = record_ids_psom2

    if (not inc_registry_only): # if excluding registry-only
        record_ids = [id for id in record_ids if (not id in record_ids_registry_only_ipss)]
    if (not inc_unknown_stroke_type): # if excluding unknown stroke type
        record_ids = [id for id in record_ids if (not id in record_ids_unknown_stroke_type_ipss)]
    if (not inc_pre_2014): # if excluding patients added before 2014
        record_ids = [id for id in record_ids if (not id in record_ids_pre_2014_ipss)]
    if (not inc_sk_patients): # if excluding SickKids patients
        record_ids = [id for id in record_ids if (not id in record_ids_sk_ipss)]
    if (not inc_neonatal_stroke): # if excluding neonatal stroke cases
        record_ids = [id for id in record_ids if (not id in record_ids_neonatal_ipss)]
    if (not inc_adult_stroke): # if excluding adult stroke cases
        record_ids = [id for id in record_ids if (not id in record_ids_adult_stroke)]
    if (not inc_melas): # if excluding adult stroke cases
        record_ids = [id for id in record_ids if (not id in record_ids_melas)]
    if (not inc_placeholders): # if excluding Chloe's list of incomplete patients
        record_ids = [id for id in record_ids if (not id in record_ids_placeholders_ipss)]
    if (not inc_non_ipss): # if excluding records not in IPSS.
        record_ids = [id for id in record_ids if (id in record_ids_ipss)]
    if (not inc_non_sips): # if excluding records not in SIPS I or SIPS II.
        record_ids = [id for id in record_ids if (id in record_ids_sips_ipss)]
    if (not inc_non_sips2): # if excluding records not in SIPS II
        record_ids = [id for id in record_ids if (id in record_ids_sips2_ipss)]
    if (not inc_non_sips2_cohort1): # if excluding records not in SIPS II cohort I
        record_ids = [id for id in record_ids if (id in record_ids_sips2_cohort1_ipss)]
    if (not inc_non_sips2_cohort2): # if excluding records not in SIPS II cohort II
        record_ids = [id for id in record_ids if (id in record_ids_sips2_cohort2_ipss)]
    if (not inc_sips_exclusions): # if excluding records not in SIPS II
        record_ids = [id for id in record_ids if (not id in record_ids_sips_exclusions_sips2)]
    if (not inc_sips_exclusions_2): # if excluding records not in SIPS II (method 2)
        record_ids = [id for id in record_ids if (not id in record_ids_sips_exclusions_2_sips2)]
    if (not inc_patient_info_incomp):
        record_ids = [id for id in record_ids if (id in record_ids_patient_information_complete_ipss)]
    if (not inc_core_incomplete):
        record_ids = [id for id in record_ids if (not id in record_ids_core_incomplete_ipss)]
    if (not inc_non_vips_enrolled):
        record_ids = [id for id in record_ids if (id in record_ids_vips_enrolled)]
    return record_ids

# For testing. 
if (__name__ == "__main__"):
    id_lists = []
#    id_lists.append(getIPSSIDs())
#    id_lists.append(getIPSSIDs(inc_core_incomplete=False))
#    id_lists.append(getIPSSIDs(db='ipss', inc_registry_only=False, inc_unknown_stroke_type=True, inc_pre_2014=True, inc_sk_patients=True, inc_neonatal_stroke=False, inc_placeholders=False, inc_adult_stroke=False, inc_melas=False, inc_non_ipss=False, inc_core_incomplete=False)) # malig
#    id_lists.append(getIPSSIDs(db='ipss', inc_registry_only=False, inc_unknown_stroke_type=True, inc_pre_2014=True, inc_sk_patients=True, inc_neonatal_stroke=True, inc_placeholders=False, inc_adult_stroke=False, inc_melas=True, inc_non_ipss=False, inc_core_incomplete=False)) # subhem
#    id_lists.append(getIPSSIDs(db='ipss', inc_non_sips2_cohort1=False))
#    id_lists.append(getIPSSIDs(db='ipss', inc_non_sips2_cohort2=False))
#    id_lists.append(getIPSSIDs(db='vips2', inc_non_vips_enrolled=True))
#    id_lists.append(getIPSSIDs(db='vips2', inc_non_vips_enrolled=False))
    
    sips_final_ids_ipss = getIPSSIDs(db='ipss', inc_non_sips=False, inc_sips_exclusions_2=False)
    with open('sips_final_ids_ipss_delete_me.txt', 'wb') as handle:
        handle.writelines(sips_final_ids_ipss)
    sips_final_ids_sips2 = getIPSSIDs(db='sips2', inc_non_sips=False, inc_sips_exclusions_2=False)
    sips_final_ids_psom2 = getIPSSIDs(db='psom2', inc_non_sips=False, inc_sips_exclusions_2=False)
    print "union size:", len(set(sips_final_ids_sips2).union(set(sips_final_ids_ipss)))
    print "intersection size:", len(set(sips_final_ids_sips2).intersection(set(sips_final_ids_ipss)))
    for id in ['10183-1', '559-27', '10184-3']:
        if id in sips_final_ids_ipss:
            print "Bad ID allowed in IPSS:", id
        if id in sips_final_ids_sips2:
            print "Bad ID allowed in sips2:", id
        if id in sips_final_ids_psom2:
            print "Bad ID allowed in psom2:", id
    for id in sips_final_ids_ipss:
        if id not in sips_final_ids_sips2:
            print "ID in IPSS not in SIPS 2:", id
    for id in sips_final_ids_psom2:
        if id not in sips_final_ids_ipss:
            print "ID in PSOM not in IPSS:", id

    id_lists.append(sips_final_ids_ipss)
    id_lists.append(sips_final_ids_sips2)
    id_lists.append(sips_final_ids_psom2)
    for ids in id_lists:
        for id in ids:
            #        print id
            pass
        print "Number of IDs:", len(ids)
