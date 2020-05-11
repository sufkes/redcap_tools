#!/usr/bin/env python

import os, sys
from pprint import pprint

# My modules in other directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.exportRecords import exportRecords
from misc.getRecordIDList import getRecordIDList
from misc.ApiSettings import ApiSettings

def getIPSSIDs(from_code_name="ipss_v4", ex_registry_only=False, ex_unknown_stroke_type=False, ex_pre_2003=False, ex_pre_2014=False, ex_post_20191001=False, ex_sk_patients=False, ex_neonatal_stroke=False, ex_placeholders=False, ex_adult_stroke=False, ex_melas=False, ex_non_ipss=False, ex_non_sips=False, ex_non_sips2=False, ex_non_sips2_cohort1=False, ex_non_sips2_cohort2=False, ex_sips_exclusions=False, ex_sips_exclusions_2=False, ex_patient_info_incomp=False, ex_core_incomplete=False, ex_non_vips_enrolled=False, ex_vips_screen_nonenroll=False):
    '''
    Parameters:
        from_code_name:            str - code_name of database to get IDs from. Allowed values are the code names defined in user's api_keys.yml file.
        ex_registry_only:          bool - whether to exclude IDs of SickKids registry-only patients based on IPSS data
        ex_unknown_stroke_type:    bool - whether to exclude IDs of records with unknown stroke type based on IPSS data
        ex_pre_2003:               bool - whether to exclude IDs of patients enrolled before 2003 based on IPSS field dateentered
        ex_pre_2014:               bool - whether to exclude IDs of patients enrolled before 2014 based on IPSS field originalipss
        ex_post_20191001           bool - whether to indlude IDs added on or after 2019-10-01 based on the IPSS field dateentered
        ex_sk_patients:            bool - whether to exclude IDs of patients with 'hsc' data access group in IPSS
        ex_neonatal_stroke:        bool - whether to exclude IDs of patients who suffered a neonatal stroke based on IPSS data
        ex_placeholders:           bool - whether to exclude IDs of patients with almost no real data, whose records likely exist as placeholders based on IPSS data
        ex_adult_stroke:           bool - whether to exclude IDs of patients who did not suffer a stroke as a child based on IPSS data
        ex_melas:                  bool - whether to exclude IDs patients with MELAS based on IPSS data
        ex_non_ipss:               bool - whether to exclude IDs that do not exist in the IPSS
        ex_non_sips:               bool - whether to exclude IDs that are not in SIPS I or SIPS II based on IPSS data
        ex_non_sips2:              bool - whether to exclude IDs that are not in SIPS II based on IPSS data
        ex_non_sips2_cohort1       bool - whether to exclude IDs that are not in SIPS II cohort I based on IPSS data
        ex_non_sips2_cohort2       bool - whether to exclude IDs that are not in SIPS II cohort II based on IPSS data
        ex_sips_exclusions:        bool - whether to exclude SIPS patients that were excluded merely screened based on SIPS II field 'screened'
        ex_sips_exclusions_2:      bool - whether to exclude SIPS patients that were excluded based screened based on SIPS II field 'screened' and 'actcohortsp'
        ex_patient_info_incomp     bool - whether to exclude IDs of patients for whom patient_information_complete != 2 in IPSS, *but still include all SLCH patients*.
        ex_core_incomplete         bool - whether to exclude IDs of patients for whom any of the 'core' forms are not marked as complete (core forms, here, include 'patient_information', 'cardiac_arteriopathy_risk_factors', 'other_child_and_neonatal_risk_factors', and 'clinical_presentation')
        ex_non_vips_enrolled:      bool - whether to exclude patients who are not enrolled in VIPS, based on the condition of the VIPS field vscreen_sfoutc=4.
        ex_vips_screen_nonenroll:  bool - whether to exclude patients who are "VIPS screened, not enrolled" based on the IPSS field 'vips_screened'

    Returns:
        record_ids:               list - record IDs in the specified database after specified exclusions
    '''

    ## Get list of exlusions requested (i.e. get a list of all args set to False).
    exclusion_args = []
    for key, val in locals().iteritems():
        if (val is True) and (key[:3] == 'ex_'):
            exclusion_args.append(key)
    
    ## Get API tokens and URLs for all projects used in the filters
    api_settings = ApiSettings() # Create instance of ApiSettings class. Use this to find file containing API keys and URLs.    

    token_dict = {} # keys are code names, values are a tuple with (url, token) for that project
    for code_name in ["ipss_arch", "ipss_v4", "sips2_v2", "vips2", "psom_v2"]:
        url, key, code_name = api_settings.getApiCredentials(code_name=code_name)
        token_dict[code_name] = (url, key)
    
    ## Get list of all record IDs in the database specified with the 'from_code_name' option
    from_url, from_key, from_code_name = api_settings.getApiCredentials(code_name=from_code_name)
    record_ids_all = getRecordIDList(from_url, from_key)
    
    ## Generate lists of fields & events which must be exported from each project in order to filter the record IDs. It would be fine to export all data, but this would take a long time.
    required_data_dict = {
        "ex_registry_only":{
            "ipss_v4":{
                "fields":["substud"],
                "events":["acute_arm_1"]
            }
        },
        "ex_unknown_stroke_type":{
            "ipss_v4":{
                "fields":["stroke_type"],
                "events":["acute_arm_1"]
            }
        },
        "ex_pre_2003":{
            "ipss_v4":{
                "fields":["dateentered"],
                "events":["acute_arm_1"]
            }
        },
        "ex_pre_2014":{
            "ipss_v4":{
                "fields":["originalipss"],
                "events":["acute_arm_1"]
            }
        },
        "ex_post_20191001":{
            "ipss_v4":{
                "fields":["dateentered"],
                "events":["acute_arm_1"]
            }
        },
        "ex_sk_patients":{
            "ipss_v4":{
                "fields":["ipssid"],
                "events":["acute_arm_1", "followup_arm_1"] # Need both in case record only has data in followup_arm_1
            }
        },
        "ex_neonatal_stroke":{
            "ipss_v4":{
                "fields":["strage"],
                "events":["acute_arm_1"]
            }
        },
        "ex_placeholders":{
            "ipss_v4":{
                "forms":["clinical_presentation", "cardiac_and_arteriopathy_risk_factors"], # note that here we need all fields in the form.
                "events":["acute_arm_1"]
            }
        },
        "ex_adult_stroke":{
            "ipss_v4":{
                "fields":["birmont", "biryear", "doe", "daent", "strage", "substud"],
                "events":["acute_arm_1"]
            }
        },
        "ex_melas":{
            "ipss_v4":{
                "fields":["genetsy", "genetsys"],
                "events":["acute_arm_1"]
            }
        },
        "ex_non_ipss":{
            "ipss_v4":{
                "fields":["ipssid"],
                "events":["acute_arm_1", "followup_arm_1"] # Need both in case record only has data in followup_arm_1
                }
        },
        "ex_non_sips":{
            "ipss_v4":{
                "fields":["substud"],
                "events":["acute_arm_1"]
            }
        },
        "ex_non_sips2":{
            "ipss_v4":{
                "fields":["substud"],
                "events":["acute_arm_1"]
            }
        },
        "ex_non_sips2_cohort1":{
            "ipss_v4":{
                "fields":["substud", "sip_cohort"],
                "events":["acute_arm_1"]
            }
        },
        "ex_non_sips2_cohort2":{
            "ipss_v4":{
                "fields":["substud", "sip_cohort"],
                "events":["acute_arm_1"]
            }
        },
        "ex_sips_exclusions":{
            "sips2_v2":{
                "fields":["screened"],
                "events":["confirmation_and_t_arm_1"]
            }
        },
        "ex_sips_exclusions_2":{
            "sips2_v2":{
                "fields":["screened", "actcohortsp"],
                "events":["confirmation_and_t_arm_1", "acute_arm_1"]
            }
        },
        "ex_patient_info_incomp":{
            "ipss_v4":{
                "fields":["patient_information_complete"],
                "events":["acute_arm_1"]
            }
        },
        "ex_core_incomplete":{
            "ipss_v4":{
                "fields":["patient_information_complete", "cardiac_and_arteriopathy_risk_factors_complete", "other_child_and_neonatal_risk_factors_complete", "clinical_presentation_complete", "status_at_discharge_complete"],
                "events":["acute_arm_1"]
            }
        },
        "ex_non_vips_enrolled":{
            "vips2":{
                "fields":["vscreen_sfoutc"],
                "events":["confirmation_and_t_arm_1", "confirmation_and_t_arm_2"]
            }
        },
        "ex_vips_screen_nonenroll":{
            "ipss_v4":{
                "fields":["vips_screened"],
                "events":["acute_arm_1"]
            }
        }
    }

    ## Build dicts for arguments to be passed to exportRecords.
    exportRecords_args = {} # keys are the code names of projects from which data will be export. Values are the args to be passed to exportRecords for those projects.
    for arg in exclusion_args:
        for code_name, project_data in required_data_dict[arg].iteritems():
            if (not code_name in exportRecords_args.keys()):
                exportRecords_args[code_name] = {"fields":None, "forms":None, "events":None}
            for key, val in project_data.iteritems():
                if (exportRecords_args[code_name][key] is None):
                    exportRecords_args[code_name][key] = val
                else:
                    exportRecords_args[code_name][key].extend(val)

    # Remove duplicates from the lists of args (not necessary, but do it for visual clarity).
    for code_name, args in exportRecords_args.iteritems():
        for arg, val in args.iteritems():
            if (not val is None):
                args[arg] = list(set(val))

    ## Export all data required for the specified filters. Don't export data from unneed projects.
    filter_data = {} # keys are project code names; values are the actual data sets exported from the projects.
    for code_name, args in exportRecords_args.iteritems():
        api_url = token_dict[code_name][0]
        api_key = token_dict[code_name][1]
        filter_data[code_name] = exportRecords(api_url, api_key, **args)

        
    #### Generate lists of IDs to exclude based on specified exclusions.
    ## Keep track of which records are excluded by each exclusion argument.
    excluded_ids = {} # key is exclusin arg; value is list of IDs excluded by that condition.
    
    ## SickKids Registry-only patients
    if ex_registry_only:
        # Registry-only records based on IPSS data
        # * All patients labelled registry-only in Archive are labelled likewise in IPSS.
        # * All '9203-' patients are labelled registry only in IPSS.
        excluded_ids["ex_registry_only"] = set()

        for row in filter_data['ipss_v4']:
            id = row['ipssid']
            if (row["substud___8"] == "1") or ('9203-' in id):
                excluded_ids["ex_registry_only"].add(id)

                
    ## Unknown stroke type
    if ex_unknown_stroke_type:
        record_ids_known_stroke_type_ipss = set()
        
        for row in filter_data['ipss_v4']:
            if (row["stroke_type___1"] == "1") or (row["stroke_type___2"] == "1") or (row["stroke_type___3"] == "1") or (row["stroke_type___4"] == "1") or (row["stroke_type___5"] == "1") or (row["stroke_type___6"] == "1") or (row["stroke_type___7"] == "1") or (row["stroke_type___8"] == "1") or (row['stroke_type___9'] == "1"):
                id = row["ipssid"]
                record_ids_known_stroke_type_ipss.add(id)
        excluded_ids["ex_unknown_stroke_type"] = set([id for id in record_ids_all if (not id in record_ids_known_stroke_type_ipss)])

        
    ## Patients that were entered before 2003
    if ex_pre_2003:
        excluded_ids["ex_pre_2003"] = set()

        for row in filter_data['ipss_v4']:
            id = row["ipssid"]
            date_entered = row["dateentered"].replace('-','') # convert 2019-01-23 to 20190123
            try:
                if (int(date_entered) < 20030101):
                    excluded_ids["ex_pre_2003"].add(id)
                else:
                    pass
            except ValueError: # occurs when value stored in 'dateentered' is blank (or possible another nonsense format)
                if (id[:2] == '7-'): # all '7-' patients are assume to be added after 2003.
                    continue
                elif (id[:5] == '9203-'): # all '9203-' patients are known to be entered before 2003.
                    excluded_ids["ex_pre_2003"].add(id)                    
                else: # If record has not dateentered, and is not a 7- or 9203- patient (who are known to be added before 20191001)
                    print "Warning: Assuming record '"+id+"' was added after 2003"

                
    ## Patients that have been entered since the launch of IPSS in REDCap from 2014 to present.
    if ex_pre_2014:
        excluded_ids["ex_pre_2014"] = set()

        for row in filter_data["ipss_v4"]:
            if (row["originalipss___1"] == '1'):
                id = row["ipssid"]
                excluded_ids["ex_pre_2014"].add(id)

                
    ## Patients that were entered after 2019-10-01
    if ex_post_20191001:
        excluded_ids["ex_post_20191001"] = set()
        for row in filter_data["ipss_v4"]:
            id = row["ipssid"]
            date_entered = row["dateentered"].replace('-','') # convert 2019-01-23 to 20190123
            try:
                if (int(date_entered) >= 20191001):
                    excluded_ids["ex_post_20191001"].add(id)
                else:
                    pass
            except ValueError: # occurs when value stored in 'dateentered' is blank (or possible another nonsense format)
                if (id[:2] == '7-') or (id[:5] == '9203-'):
                    continue
                else: # If record has not dateentered, and is not a 7- or 9203- patient (who are known to be added before 20191001)
                    excluded_ids["ex_post_20191001"].add(id)
                    print "Warning: Assuming record '"+id+"' was added after 20191001"

                    
    ## SickKids patients (based on DAG)
    if ex_sk_patients:
        excluded_ids["ex_sk_patients"] = set()
        
        for row in filter_data["ipss_v4"]:
            if (row["redcap_data_access_group"] == "hsc"):
                id = row['ipssid']
                excluded_ids["ex_sk_patients"].add(id)

                
    ## Neonatal stroke based on IPSS data
    if ex_neonatal_stroke:
        excluded_ids["ex_neonatal_stroke"] = set()

        for row in filter_data["ipss_v4"]:
            if (row['strage'] == '0'):
                id = row['ipssid']
                excluded_ids["ex_neonatal_stroke"].add(id)

                
    ## Records deemed to be "placeholders" based on condition that they have no data in either the clinical presentation or cardiac risk factors forms.
    if ex_placeholders:
        record_ids_nonplaceholder_ipss = set()

        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (id in record_ids_nonplaceholder_ipss):
                continue
            row_has_data = False
            for field, value in row.iteritems():
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
                record_ids_nonplaceholder_ipss.add(id)
        excluded_ids["ex_placeholders"] = [id for id in record_ids_all if (not id in record_ids_nonplaceholder_ipss)]
                
                
    ## Non-pediatric stroke (>= 19 years of age at date of stroke)
    if ex_adult_stroke:
        excluded_ids["ex_adult_stroke"] = set()
        
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row['birmont'] != '') and (row['biryear'] != '') and (row['doe'] != ''):
                stroke_age = float(row['doe'][:4]) + float(row['doe'][5:7])/12 - float(row['biryear']) - float(row['birmont'])/12
                if (stroke_age >= 19.0 + 1.0/12.0): # only year/month of birth is known, so pad cutoff by 1 month.
                    excluded_ids["ex_adult_stroke"].add(id)
                    
            elif (row['birmont'] != '') and (row['biryear'] != '') and (row['daent'] != ''):
                stroke_age = float(row['daent'][:4]) + float(row['daent'][5:7])/12 - float(row['biryear']) - float(row['birmont'])/12
                if (stroke_age >= 19.0 + 1.0/12.0): # only year/month of birth is known, so pad cutoff by 1 month.
                    excluded_ids["ex_adult_stroke"].add(id)


    ## MELAS patients
    if ex_melas:
        excluded_ids["ex_melas"] = set()
        
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            desc = row['genetsys'].lower()
            if (row['genetsy'] == '1') and (('melas' in desc) or ('mitochondrial encephalopathy' in desc) or ('lactic acidosis' in desc)):
                excluded_ids["ex_melas"].add(id)

                
    ## Patients not in IPSS database
    if ex_non_ipss:
        ipss_ids = set()
        for row in filter_data["ipss_v4"]:
            id = row["ipssid"]
            ipss_ids.add(id)
        excluded_ids["ex_non_ipss"] = [id for id in record_ids_all if (not id in ipss_ids)]        

                
    ## Patients not enrolled in SIPS I or SIPS II
    if ex_non_sips:
        record_ids_sips_ipss = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row["substud___4"] == "1") or (row["substud___6"] == "1"):
                record_ids_sips_ipss.add(id)
        excluded_ids["ex_non_sips"] = [id for id in record_ids_all if (not id in record_ids_sips_ipss)]
        

    ## Patients not enrolled in SIPS II
    if ex_non_sips2:
        record_ids_sips2_ipss = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row["substud___4"] == "1"):
                record_ids_sips2_ipss.add(id)
        excluded_ids["ex_non_sips2"] = [id for id in record_ids_all if (not id in record_ids_sips2_ipss)]

                
    ## SIPS II cohort I patients
    if ex_non_sips2_cohort1:
        record_ids_sips2_cohort1_ipss = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row["substud___4"] == "1") and (row['sip_cohort'] == '1'):
                record_ids_sips2_cohort1_ipss.add(id)
        excluded_ids["ex_non_sips2_cohort1"] = [id for id in record_ids_all if (not id in record_ids_sips2_cohort1_ipss)]
                
                
    ## SIPS II cohort II patients
    if ex_non_sips2_cohort2:
        record_ids_sips2_cohort2_ipss = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row["substud___4"] == "1") and (row['sip_cohort'] == '2'):
                record_ids_sips2_cohort2_ipss.add(id)
        excluded_ids["ex_non_sips2_cohort2"] = [id for id in record_ids_all if (not id in record_ids_sips2_cohort2_ipss)]
                
                
    ## Patients excluded from SIPS studies based on SIPS II variable 'screened'
    if ex_sips_exclusions:
        excluded_ids["ex_sips_exclusions"] = set()
        
        for row in filter_data["sips2_v2"]:
            id = row['ipssid']
            if (row["screened"] in ['1', '3']):
                excluded_ids["ex_sips_exclusions"].add(id)

                
    ## Patients excluded from SIPS studies based on SIPS II variables 'screened' and 'actcohortsp'
    if ex_sips_exclusions_2:
        excluded_ids["ex_sips_exclusions_2"] = set()
        
        actcohort2_ids = set()
        for row in filter_data["sips2_v2"]:
            id = row['ipssid']
            if (row["screened"] in ['1']):
                excluded_ids["ex_sips_exclusions_2"].add(id)
            if (row['actcohortsp'] == '2'):
                actcohort2_ids.add(id)
        for row in filter_data["sips2_v2"]:
            id = row['ipssid']
            if (id in actcohort2_ids) and (row['screened'] == '3'):
                excluded_ids["ex_sips_exclusions_2"].add(id)

                
    ## Patients for whom patient_information_complete != 2.
    if ex_patient_info_incomp:
        record_ids_patient_information_complete_ipss = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row['patient_information_complete'] == '2') or (row['redcap_data_access_group'] == 'slch'):
                record_ids_patient_information_complete_ipss.add(id)
        excluded_ids["ex_patient_info_incomp"] = [id for id in record_ids_all if (not id in record_ids_patient_information_complete_ipss)]

        
    ## Patients for whom any of the "core" forms are not marked as complete
    if ex_core_incomplete:
        excluded_ids["ex_core_incomplete"] = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row['patient_information_complete'] != '2') or (row['cardiac_and_arteriopathy_risk_factors_complete'] != '2') or (row['other_child_and_neonatal_risk_factors_complete'] != '2') or (row['clinical_presentation_complete'] != '2'):
                excluded_ids["ex_core_incomplete"].add(id)

                
    # Patients who are not enrolled in VIPS.
    if ex_non_vips_enrolled:
        record_ids_vips_enrolled = set()
        for row in filter_data["vips2"]:
            id = row['ipssid']
            if (row['vscreen_sfoutc'] == '4'):
                record_ids_vips_enrolled.add(id)
        excluded_ids["ex_non_vips_enrolled"] = [id for id in record_ids_all if (not id in record_ids_vips_enrolled)]

        
    # Patients who are "VIPS screened not enrolled" based on the IPSS field 'vips_screened'.
    if ex_vips_screen_nonenroll:
        excluded_ids["ex_vips_screen_nonenroll"] = set()
        for row in filter_data["ipss_v4"]:
            id = row['ipssid']
            if (row['vips_screened'] == '1'):
                excluded_ids["ex_vips_screen_nonenroll"].add(id)


    ## Remove all excluded IDs, and return the filtered list.
    record_ids = record_ids_all
    for exclusion, excluded_id_set in excluded_ids.iteritems():
        record_ids = [id for id in record_ids if (not id in excluded_id_set)]
    return record_ids

#### Run tests.
if (__name__ == "__main__"):
    test_args = ["ex_registry_only", "ex_unknown_stroke_type", "ex_pre_2003", "ex_pre_2014", "ex_post_20191001", "ex_sk_patients", "ex_neonatal_stroke", "ex_placeholders", "ex_adult_stroke", "ex_melas", "ex_non_ipss", "ex_non_sips", "ex_non_sips2", "ex_non_sips2_cohort1", "ex_non_sips2_cohort2", "ex_sips_exclusions", "ex_sips_exclusions_2", "ex_patient_info_incomp", "ex_core_incomplete", "ex_non_vips_enrolled", "ex_vips_screen_nonenroll"]

    rr = getIPSSIDs(from_code_name="ipss_v4", ex_sk_patients=True)
    print rr
    sys.exit()
    
    all = getIPSSIDs()
    print "All"
    print len(all)
    print
    
    for test_arg in test_args:
        args_dict = {test_arg:True}
        print args_dict
        some = getIPSSIDs(from_code_name='ipss_v4', **args_dict)
        print len(some)
        print

    sys.exit()
    id_lists = []
    
#    all = getIPSSIDs(db='ipss', ex_vips_screen_nonenroll=True)
#    some = getIPSSIDs(db='ipss', ex_vips_screen_nonenroll=False)
    
    id_lists.append(all)
    id_lists.append(some)
    for id in all:
        if (not id in some):
            print "Excluded ID:", id
            pass

    for ids in id_lists:
        for id in ids:
            #        print id
            pass
        print "Number of IDs:", len(ids)
