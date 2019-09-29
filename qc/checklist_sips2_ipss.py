import sys

from Check import Check
from getRecord import getEntryLR

# Create list of checks (must be called 'checklist')
checklist = []

#### Check: In SIPS, Acute CRF, 'Did the patient receive anticonvulsant medications within 14 days post stroke?' is checked yes (medications=1), then in IPSS, Treatment instrument, 'Anticonvulsants' should also be checked yes (anticonv=1).
name = "medications_same"
description = "In SIPS, Acute CRF, if 'Did the patient receive anticonvulsant medications within 14 days post stroke?' is checked yes (medications=1), then in IPSS, Treatment instrument, 'Anticonvulsants' should also be checked yes (anticonv=1)."
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["medications"] # list target fields in first project only.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    medications_1 = row_1["medications"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    anticonv_2, hidden = getEntryLR(record_id, event_2, instance_2, "anticonv", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    
    if (medications_1 == "1"):
        if (anticonv_2 != "1"):
            element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction

#### Check: In SIPS, Acute CRF, if 'Was a seizure a presenting sign of the stroke' is checked yes (bpdate_v2=1), then in IPSS, Clinical Presentation, 'Seizures' should have 'at stroke presentation' checked off (seizur___1=1).
name = "sz_present_at_str_same"
description = "In SIPS, Acute CRF, if 'Was a seizure a presenting sign of the stroke' is checked yes (bpdate_v2=1), then in IPSS, Clinical Presentation, 'Seizures' should have 'at stroke presentation' checked off (seizur(1)=1)."
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["bpdate_v2"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    bpdate_v2_1 = row_1["bpdate_v2"]

    # Get values from second project
    event_2 = "acute_arm_1"
    instance_2 = None

    seizur___1_2, hidden = getEntryLR(record_id, event_2, instance_2, "seizur___1", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    
    if (bpdate_v2_1 == "1") and (seizur___1_2 != "1"):
        element_bad = True
    elif ((bpdate_v2_1 == "0") or (bpdate_v2_1 == "")) and (seizur___1_2 == "1"):
        element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In SIPS, Acute CRF, if 'indicate definite vs possible seizure:' must be consistent with IPSS, Clinical Presentation, 'Indicate DEFINITE VERSUS POSSIBLE ____ seizure.' (seizind and seizinde)
name = "def_vs_pos_seiz_same"
description = "In SIPS, Acute CRF, 'indicate definite vs possible seizure' (defvsposseizure) must be consistent with IPSS, Clinical Presentation, 'Indicate DEFINITE VERSUS POSSIBLE seizure' (seizind and seizinde)"
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["defvsposseizure___1", "defvsposseizure___3", "defvsposseizure___4", "defvsposseizure___5"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    def___1_1 = row_1["defvsposseizure___1"]
    def___3_1 = row_1["defvsposseizure___3"]
    def___4_1 = row_1["defvsposseizure___4"]
    def___5_1 = row_1["defvsposseizure___5"]

    # Get values from second project
    event_2 = "acute_arm_1"
    instance_2 = None

    seizind_2, hidden = getEntryLR(record_id, event_2, instance_2, "seizind", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    seizinde_2, hidden = getEntryLR(record_id, event_2, instance_2, "seizinde", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    # The branching logic is the same for these two fields, so assign hidden state to a single variable.

    if (not hidden): # Only perform check if the fields are not hidden by branching logic in IPSS.
        # defvsposseizure___1 = 1  <=>  seizind = 1
        if (def___1_1 == "1") and (seizind_2 != "1"):
            element_bad = True
        elif (seizind_2 == "1") and (def___1_1 != "1"):
            element_bad = True

        # defvsposseizure___3 = 1  <=>  seizinde = 1
        if (def___3_1 == "1") and (seizinde_2 != "1"):
            element_bad = True
        elif (seizinde_2 == "1") and (def___3_1 != "1"):
            element_bad = True

        # defvsposseizure___4 = 1  <=>  seizind = 2
        if (def___4_1 == "1") and (seizind_2 != "2"):
            element_bad = True
        elif (seizind_2 == "2") and (def___4_1 != "1"):
            element_bad = True

        # defvsposseizure___5 = 1  <=>  seizinde = 2
        if (def___5_1 == "1") and (seizinde_2 != "2"):
            element_bad = True
        elif (seizinde_2 == "2") and (def___5_1 != "1"):
            element_bad = True
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In SIPS, Follow-up CRF, if 'Have you had seizures since your last visit?' is yes (sz_since_last=1), then in IPSS, Recovery and Recurrence, 'Q4b. Does your child suffer from seizures since being discharged after the stroke(s)?' should be yes (pseiz=1), if the dates of assessment are the same for the two forms. 
name = "seiz_since_last_visit_same"
description = "In SIPS, Follow-up CRF, if 'Have you had seizures since your last visit?' is yes (sz_since_last=1), then in IPSS, Recovery and Recurrence, 'Q4b. Does your child suffer from seizures since being discharged after the stroke(s)?' should be yes (pseiz=1), if the dates of assessment are the same for the two forms."
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ["sz_since_last"]

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    sz_since_last_1 = row_1["sz_since_last"]
    date_1 = row_1["date_v2"]

    # Get values from second project
    event_2 = "followup_arm_1"

    pseiz_2 = "" # Assume blank if corresponding assessment date not found.
    for row_index_2 in record_id_map_list[1][record_id]: # look at all rows corresponding to record ID. 
        row_2 = records_list[1][row_index_2]
        if (row_2["redcap_repeat_instrument"] == "recovery_and_recurrence"): # if row corresponds to correct independent repeating form
            if (row_2["assedat"] == date_1): # if form instance corresponds to same date as SIPS follow-up form.
                pseiz_2 = row_2["pseiz"]
                if (sz_since_last_1 != pseiz_2):
                    element_bad = True
                break
    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
