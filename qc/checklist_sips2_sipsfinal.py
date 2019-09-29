from Check import Check # Class used to define what a check does and when it is performed

# Create list of checks (must be called 'checklist').
checklist = []


cohort1_normal = ['actcohortsp', 'date_enrolled_sips2', 'date', 'sz_diary', 'seiz_14', 'sztiminghrsdays', 'hrspoststroke', 'hrspoststroke2_dfa', 'lastszhoursdays', 'hrspoststroke2_d81', 'hrspoststroke2_dfa2_e3c', 'bpdate_v2', 'bpsys_v2', 'outpseizure_v2', 'defvsposseizure', 'defseizures', 'sztype', 'longest_seizure_duration', 'seizing_when_arrived_in_ed', 'received_rescue_medication', 'eeg', 'eegtype_v2', 'prorechr_v2', 'eegres_v2', 'elecseiz_v2', 'elseizsp_v2', 'epidischarge', 'epidischarsp', 'actabnslow', 'actabnslosp', 'eegpatindica', 'medications', 'rescue_medication', 'drip', 'maintenance_ac', 'med_count', 'ac_1', 'ac_1_dose', 'aloneconcur1', 'anticonvulsant_2', 'ac_2_dose', 'aloneconcur2', 'anticonvulsant_3', 'ac_3_dose', 'aloneconcur3', 'anticonvulsant_4', 'ac_4_dose', 'aloneconcur4', 'anticonvulsant_5', 'ac_5_dose', 'aloneconcur5', 'm_ac_after_stroke', 'mnc_ac_name', 'timing_mac_unit', 'timing_mac', 'initial_mac_timing', 'discharged_on_a_maintenanc', 'if_yes_state_anticonvulsan', 'disch_dose', 'rad_features', 'lobe_involve', 'history', 'otherfamhist', 'dt_remote_sz', 'remote_symptomatic', 'act_epilepsy', 'date_v2', 'date_last_visit', 'fup_type', 'sz_since_last', 'fup_seiz', 'datesz_since_last_visit', 'numsz_since_last_visit', 'sz_with_triggers', 'sz_with_triggers_specify', 'other_seizure_trigger', 'date_sz_with_trig', 'sz_without_triggers', 'date_sz_without_trig', 'status_epilepticus', 'num_sz_more_fivemins', 'duration_of_stat_ep', 'seizing_arrive_emerg', 'statep_received_rescue_med', 'sz_ep_rescue_med', 'e_d_visits_for_seizures', 'admissions', 'intubations', 'daily_seizures', 'seizures_past_week', 'seizures_past_month', 'seizures_past_year', 'started_on_one_side_2_head', 'sz_side', 'sz_stayed_side', 'sz_side2_9c4', 'seizure_description', 'medications_v2', 'current_ac', 'acs_tried', 'name_of_medication', 'alone_or_concurrent', 'taking_currently', 'name_of_medication_2', 'alone_or_concurrent_2', 'taking_currently_2', 'name_of_medication_3', 'alone_or_concurrent_3', 'taking_currently_3', 'name_of_medication_4', 'alone_or_concurrent_4', 'taking_currently_4', 'eeg_since_last_visit', 'where_eeg', 'eeg_f_up_date', 'eeg_outcome', 'seizure_classification', 'other_please_describe', 'eeg_at_fu', 'eeg_report_type', 'eeg_results_fup_neuro', 'electrographic_seizures', 'electrograph_seizures', 'epilept_discharges', 'epileptiform_discharges', 'focal_discharges', 'multifocal_discharges', 'abnormal_slowing', 'abnormal_slowing_type', 'modified_engel_score', 'mrs']

cohort2_normal = cohort1_normal
 

# Define check by specifying each of the parameters in the 'Check' class.

#### Check: SIPS II Cohort I checks
name = "cohort1_sips2_fields"
description = "Missing fields in SIPS II for patients in SIPS II cohort I"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = False
target_fields = None

# Define function which determines whether a row should be checked (regardless of event, instance, branching logic)
def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

# Define function which determines whether a field should be checked (regardless of branching logic).
def fieldConditions(field_name, metadata):
    field = metadata[field_name]

    if field_name.split('___')[0] in cohort1_normal: # look for the base name of the checkbox field in the requested field list.
        return True

    return False # if not in either of the lists checked above

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    # At this point, the field is already known to be in either the list of normal fields, or the list of grouped fields
    field = metadata[field_name]
    row = records[row_index]
    element_bad = False # Assume good until flaw found.
    if (field.field_type == "checkbox"):
        if (field_name == field.choices[0]): # Perform check when the first checkbox option is found.
            all_boxes_blank = True # Assume all blank until nonblank option found.
            for choice_field_name in field.choices: # Loop over the other checkbox options.
                if (row[choice_field_name] == '1'):
                    all_boxes_blank = False
                    break
    
            # WON'T WORK IF FIELD NAME IS 'foo___var_name___1'.
            if all_boxes_blank:
                element_bad = True

    elif row[field_name].strip() == "":
        element_bad = True    
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: SIPS II Cohort II checks
name = "cohort2_sips2_fields"
description = "Missing fields in SIPS II for patients in SIPS II cohort II"
report_forms = True
inter_project = False
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = False
specify_fields = False
target_fields = None

# Define function which determines whether a row should be checked (regardless of event, instance, branching logic)
def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

# Define function which determines whether a field should be checked (regardless of branching logic).
def fieldConditions(field_name, metadata):
    field = metadata[field_name]

    if field_name.split('___')[0] in cohort2_normal: # look for the base name of the checkbox field in the requested field list.
        return True

    return False # if not in either of the lists checked above

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    # At this point, the field is already known to be in either the list of normal fields, or the list of grouped fields
    field = metadata[field_name]
    row = records[row_index]
    element_bad = False # Assume good until flaw found.
    if (field.field_type == "checkbox"):
        if (field_name == field.choices[0]): # Perform check when the first checkbox option is found.
            all_boxes_blank = True # Assume all blank until nonblank option found.
            for choice_field_name in field.choices: # Loop over the other checkbox options.
                if (row[choice_field_name] == '1'):
                    all_boxes_blank = False
                    break

            # WON'T WORK IF FIELD NAME IS 'foo___var_name___1'.
            if all_boxes_blank:
                element_bad = True

    elif row[field_name].strip() == "":
        element_bad = True
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
