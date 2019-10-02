import os, sys

from Check import Check
from dates import compareDates

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.getRecord import getEventFieldInstance

# Create list of checks (must be called 'checklist')
checklist = []

#### Check: 14 days post stroke = No, (4) Medications will most likely be No as well. Otherwise, case should be inspected.
name = "seiz_meds_no_seiz"
description = "If the patient had no seizures within 14 days post stroke, they should not have received anticonvulsants within 14 days post stroke. Fields: seiz_14, medications"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["seiz_14", "medications"] # first field should lie in the field, event, instance which you would like to be reported.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    
    if (row["seiz_14"] == "0"): # if no seizures within 14 days post-stroke
        if (row["medications"] == "1"): # if received anticonvulsants within 14 days post-stroke
            element_bad = True
    return element_bad 

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction # delete names so that spelling errors in variable names are detected in future check definitions


#### Check: For patients with stroke at onset, last seizure timing > first seizure timing
name = "last_seiz_after_first"
description = "For patients with stroke at onset, the last seizure should have occurred after the first seizure. Fields: hrspoststroke, hrspoststroke2_dfa, hrspoststroke2_d81, hrspoststroke2_dfa2_e3c"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["hrspoststroke", "hrspoststroke2_dfa", "hrspoststroke2_d81", "hrspoststroke2_dfa2_e3c"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False
    
    row = records[row_index]
    
    if (row["seiz_14"] == "1"): # if patient had seizures within 14 days post-stroke.
        first_seiz_hrs = row["hrspoststroke"]
        first_seiz_days = row["hrspoststroke2_dfa"]
        if (row["hrspoststroke2_d81"] != ""): # if last seizure specified in hours
            if (first_seiz_hrs == "") and (first_seiz_days == ""): # if first but no last
                element_bad = True
            elif (first_seiz_hrs != ""): # if first seizure specified in hours
                if (row["hrspoststroke2_d81"] < first_seiz_hrs): # if last before first
                    element_bad = True
            elif (first_seiz_days != ""): # if last < 24h and first > 24h
                element_bad = True
        if (row["hrspoststroke2_dfa2_e3c"] != ""): # if last seizure specified in days
            if (first_seiz_hrs == "") and (first_seiz_days == ""):
                element_bad = True
            elif (first_seiz_days != ""): # if first seizure specified in days
                if (row["hrspoststroke2_dfa2_e3c"] < first_seiz_days):
                    element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: If seizure was presenting sign of stroke, then an acute, post-stroke seizure probably occurred prior to stroke diagnosis
name = "seiz_pres_sign_seiz_prior_to_stroke"
description = "If seizure was a presenting sign of stroke, then an acute, post-stroke seizure probably occurred prior to stroke diagnosis. Fields: bpdate_v2, bpsys_v2"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["bpsys_v2", "bpdate_v2"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    if (row["bpsys_v2"] != row["bpdate_v2"]):
        element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction

#### Check: Date of 3 month followup should be before date of last SIPS visit
name = "date_3m_fup_after_last_visit"
description = "Date of 3 month followup should be after date of last SIPS visit. Fields: date_v2, date_last_visit"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["date_v2", "date_last_visit"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    truth, blanks = compareDates(metadata, records, "date_v2", "date_last_visit", row_index, comparison="l")
    if (not blanks) and (truth):
        element_bad = True
    return element_bad
        
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Estimated date of the first seizure since last visit should be after date of last SIPS visit
name = "date_1st_seiz_since_last_vis_aft_date_last_vis"
description = "Estimated date of the first seizure since last visit should be after date of last SIPS visit. Fields: date_last_visit, datesz_since_last_visit"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["date_last_visit", "datesz_since_last_visit"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    truth, blanks = compareDates(metadata, records, "datesz_since_last_visit", "date_last_visit", row_index, comparison="l")
    if (not blanks) and (truth):
        element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Number of all anticonvulsants tried should be greater than or equal to the number of current anticonvulsants.
name = "tot_acs_geq_cur_acs"
description = "Total number of anticonvulsants tried should be greater than or equal to the number of current anticonvulsants. Fields: current_ac, acs_tried"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["current_ac","acs_tried"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    if (row["current_ac"] != "") and (row["acs_tried"] != ""): # if both fields not empty
        if (int(row["current_ac"]) > int(row["acs_tried"])): # if total number greater than current number
            element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: If patient had seizures with and without triggers in past 14 days, then they must have had more than 1 seizure in the last 14 days
name = "seiz_w_and_wout_trig_then_many_seizs"
description = "If patient had seizures with and without triggers in past 14 days, then they must have had more than 1 seizure in the past 14 days. Fields: numsz_since_last_visit, sz_with_triggers, sz_without_triggers"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["numsz_since_last_visit", "sz_with_triggers", "sz_without_triggers"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]

    if (row["sz_with_triggers"] == '1') and (row["sz_without_triggers"] == '1'):
        if (row["numsz_since_last_visit"] != ""):
            if (int(row["numsz_since_last_visit"]) <= 1):
                element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: The number of seizure episodes needing rescue medications since last visit must not be greater than the number of seizures since last visit
name = "num_seiz_req_meds_leq_num_seiz"
description = "The number of seizure episodes needing rescue medications since last visit must not be greater than the number of seizures since last visit. Fields: numsz_since_last_visit, sz_ep_rescue_med"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["numsz_since_last_visit", "sz_ep_rescue_med"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False
    
    row = records[row_index]

    if (row["sz_ep_rescue_med"] != "") and (row["numsz_since_last_visit"] != ""):
        if (int(row["sz_ep_rescue_med"]) > int(row["numsz_since_last_visit"])):
            element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: The number of admissions for seizures must not be greater than the number of E.D. visits for seizures
name = "num_admits_for_seiz_leq_num_ed_vis"
description = "The number of admissions for seizures must not be greater than the number of E.D. visits for seizures. Fields: e_d_visits_for_seizures, admissions"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["e_d_visits_for_seizures", "admissions"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]

    if (row["admissions"] != "") and (row["e_d_visits_for_seizures"] != ""):
        if (int(row["admissions"]) > int(row["e_d_visits_for_seizures"])):
            element_bad = True
    
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: If seizure started on one side, it must have been the left or right side, not both
name = "seiz_one_side_only"
description = "If seizure started on one side, it must have been the left or right side, not both. Field: sz_side"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["sz_side___1", "sz_side___2"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]

    if (row["sz_side___1"] == '1') and (row["sz_side___2"] == '1'):
        element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: If head turned to one side during seizure, it should only turn turn to one side
name = "seiz_turn_one_side_only"
description = "If head turned to one side during seizure, it should only turn to one side. Field: sz_side2_9c4"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["sz_side2_9c4___1", "sz_side2_9c4___2"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]

    if (row["sz_side2_9c4___1"] == '1') and (row["sz_side2_9c4___2"] == '1'):
        element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Modified Randkin Scale and KOSCHI must be obey the relationships: mRS=6 then KOSCHI=1, mRS=5 then KOSCHI=2 or 3a, mRS=4 then KOSCHI=3b, mRS=1 then KOSCHI=5a, mRS=0 then KOSCHI=5b
name = "rankin_koschi_consistency"
description = "Modified Rankin Scale and KOSCHI must be obey the relationships: mRS=6 then KOSCHI=1, mRS=5 then KOSCHI=2 or 3a, mRS=4 then KOSCHI=3b, mRS=1 then KOSCHI=5a, mRS=0 then KOSCHI=5b. Fields: mrs, koschi"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = True
target_fields = ["mrs", "koschi"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]

    m = row["mrs"]
    k = row["koschi"]
    if (m != "") and (k != ""):
        if (m == "7") and (k != "1"): # MRS=6 then KOSCHI=1
            element_bad = True
        elif (m == "6") and (k != "2") and (k != "3"):# MRS=5 then KOSCHI=2 or 3a
            element_bad = True
        elif (m == "5") and (k != "4"):# MRS=4 then KOSCHI=3b
            element_bad = True
        elif (m == "2") and (k != "7"):# MRS=1 then KOSCHI=5a
            element_bad = True
        elif (m == "1") and (k != "8"):# MRS=0 then KOSCHI=5b
            element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: The date of the last SIPS study visit should equal the date written in the form corresponding to the previous SIPS visit
name = "date_last_visit_consistent_bw_forms"
description = "The date of the last SIPS study visit should equal the date written in the form corresponding to the previous SIPS visit. Fields: date_last_visit (in listed event), date_v2 (in previous event)"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["date_last_visit"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    if (records[row_index]["redcap_event_name"] != "3_month_arm_1"): # Previous date ambiguous for this event; so skip it.
        check_row = True
    else:
        check_row = False
    return check_row

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    
    event = row["redcap_event_name"]
    
    if (row["date_last_visit"] != ""): # if there is an entry for last visit date
#        if (event == "3_month_arm_1"):
#            prev_field_name = "date_enrolled_sips2"
#            prev_event = "acute_arm_1"
#            prev_form_name = "acute_crf"
        if (event == "12_month_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "3_month_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup1_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "12_month_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup1_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup1_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup2_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup1_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup3_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup2_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup4_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup3_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup5_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup4_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup6_arm_1"):
            prev_field_name = "date_v2"
            prev_event = "additional_fup5_arm_1"
            prev_form_name = "follow_up_crf"
        date_in_last_form = getEventFieldInstance(row_index, prev_event, prev_field_name, prev_form_name, None, def_field, form_repetition_map, records, record_id_map)

        if (date_in_last_form != ""):
            if (date_in_last_form != row["date_last_visit"]):
                element_bad = True
                
        return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: The total number of anticonvulsants tried must not decrease from one follow-up visit to the next
name = "num_tot_acs_consistent_bw_event"
description = "The total number of anticonvulsants tried must not decrease from one follow-up visit to the next. Field: acs_tried (in listed and previous events)"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["acs_tried"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    check_row = True
    if (records[row_index]["redcap_event_name"] == "3_month_arm_1"):
        check_row = False
    return check_row

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    
    event = row["redcap_event_name"]

    if (row["acs_tried"] != ""): # if there is an entry for last visit date
        if (event == "12_month_arm_1"):
            prev_event = "3_month_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup1_arm_1"):
            prev_event = "12_month_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup1_arm_1"):
            prev_event = "additional_fup1_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup2_arm_1"):
            prev_event = "additional_fup1_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup3_arm_1"):
            prev_event = "additional_fup2_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup4_arm_1"):
            prev_event = "additional_fup3_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup5_arm_1"):
            prev_event = "additional_fup4_arm_1"
            prev_form_name = "follow_up_crf"
        elif (event == "additional_fup6_arm_1"):
            prev_event = "additional_fup5_arm_1"
            prev_form_name = "follow_up_crf"
        prev_acs_tried = getEventFieldInstance(row_index, prev_event, "acs_tried", prev_form_name, None, def_field, form_repetition_map, records, record_id_map)

        if (prev_acs_tried != ""):
            if (int(prev_acs_tried) > int(row["acs_tried"])):
                element_bad = True
                
        return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: Seizure count should be consistent between follow-up forms
name = "num_seiz_consistent_bw_events"
description = "The total number of seizures should be consistent between follow-up forms (# previous year = # month 0-3 + # . Fields: (seizures_past_year, numsz_since_last_visit) "
description = "Total number of seizures in past year (12 month follow-up) should equal number of seizures since last visit (12 month follow-up) + number of seizures since last visit (3 month follow-up). Fields: seizures_past_year (12 month), numsz_since_last_visit (12 month, 3 month)"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["seizures_past_year"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map): # For restriction to specific events when other events contain the same field
    check_row = True
    if (records[row_index]["redcap_event_name"] != "12_month_arm_1"):
        check_row = False
    return check_row

fieldConditions = None

def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    element_bad = False

    row = records[row_index]
    
    event = row["redcap_event_name"]

    if (row["seizures_past_year"] != ""): # if there is an entry for last visit date
        num_seiz_3_12 = row["numsz_since_last_visit"]

        prev_event = "3_month_arm_1"
        prev_form_name = "follow_up_crf"
        prev_field_name = "numsz_since_last_visit"
        num_seiz_0_3 = getEventFieldInstance(row_index, prev_event, prev_field_name, prev_form_name, None, def_field, form_repetition_map, records, record_id_map)

        if (num_seiz_0_3 != "") and (num_seiz_3_12 != ""): # if both other counts not blank
            if (int(num_seiz_0_3) + int(num_seiz_3_12) != int(row["seizures_past_year"])):
                element_bad = True
                
        return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
