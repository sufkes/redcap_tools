import os, sys

from Check import Check

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import misc
from misc.getRecord import getEntryLR

# Create list of checks (must be called 'checklist')
checklist = []


#### Check: In VIPS II, Screening Form, if etiology of stroke is arteriopathy (vstetiol=1), then in IPSS, Treatment, the fields "Other stroke treatment/intervention" (othtreti), "steroids" (ster) and "acyclovir" (acyclo) should all be answered.
name = "arteriopathy_treatment_details_complete"
description = 'In VIPS II, Screening Form, if etiology of stroke is arteriopathy (vstetiol=1), then in IPSS, Treatment, the fields "Other stroke treatment/intervention" (othtreti), "steroids" (ster) and "acyclovir" (acyclo) should all be answered.'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['vstetiol'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    vstetiol = row_1["vstetiol"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    othtreti, othtreti_hidden = getEntryLR(record_id, event_2, instance_2, "othtreti", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    ster, ster_hidden = getEntryLR(record_id, event_2, instance_2, "ster", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    acyclo, acyclo_hidden = getEntryLR(record_id, event_2, instance_2, "acyclo", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])    

    if (vstetiol == '1'):
        if (othtreti == '') or ((ster == '') and (not ster_hidden)) or ((acyclo == '') and (not acyclo_hidden)):
            element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if family history of stroke <45 is yes (fhstrkyng=1), then in IPSS, Other Child and Neonatal Risk Factors, stroke < 50 years of age should also be yes (hstroke=1).
name = "fam_hist_stroke_consistent"
description = 'In VIPS II, Interview, if family history of stroke <45 is yes (fhstrkyng=1), then in IPSS, Other Child and Neonatal Risk Factors, stroke < 50 years of age should also be yes (hstroke=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['fhstrkyng'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    fhstrkyng = row_1["fhstrkyng"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    hstroke, hstroke_hidden = getEntryLR(record_id, event_2, instance_2, "hstroke", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    if (fhstrkyng == '1'):
        if (hstroke != '1'):
            element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if family history of heart attack <45 is yes (fhhayng=1), then in IPSS, Other Child and Neonatal Risk Factors, heart attack < 50 years of age should also be yes (hheaatt=1).
name = "fam_hist_heart_attack_consistent"
description = 'In VIPS II, Interview, if family history of heart attack <45 is yes (fhhayng=1), then in IPSS, Other Child and Neonatal Risk Factors, heart attack < 50 years of age should also be yes (hheaatt=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['fhhayng'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    fhhayng = row_1["fhhayng"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    hheaatt, hheaatt_hidden = getEntryLR(record_id, event_2, instance_2, "hheaatt", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    if (fhhayng == '1'):
        if (hheaatt != '1'):
            element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if child has ever suffered any head or neck trauma that required a visit to a physician or emergency department is yes (hn_traum=1), then in IPSS, Other Child and Neonatal Risk Factors, head injury/trauma should also be yes (heatrau=1).
name = "head_traum_consistent"
description = ' VIPS II, Interview, if child has ever suffered any head or neck trauma that required a visit to a physician or emergency department is yes (hn_traum=1), then in IPSS, Other Child and Neonatal Risk Factors, head injury/trauma should also be yes (heatrau=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['hn_traum'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    hn_traum = row_1["hn_traum"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    heatrau, heatrau_hidden = getEntryLR(record_id, event_2, instance_2, "heatrau", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    if (hn_traum == '1'):
        if (heatrau != '1'):
            element_bad = True

    return element_bad

print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
#checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
#del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if child has had a UTI (uti=1), then in IPSS, Other Child and Neonatal Risk Factors, minor infection urinary tract infection should also be checked yes (infectmi___4).
name = "uti_consistent"
description = 'In VIPS II, Interview, if child has had a UTI (uti=1), then in IPSS, Other Child and Neonatal Risk Factors, minor infection urinary tract infection should also be checked yes (infectmi___4).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['uti'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    uti = row_1["uti"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    infectmi___4, infectmi___4_hidden = getEntryLR(record_id, event_2, instance_2, "infectmi___4", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    err1 = (uti == '1') and (infectmi___4 != '1')
    err2 = (uti == '0') and (infectmi___4 != '0')
    err3 = (infectmi___4 == '1') and (uti != '1')
#    err4 = (infectmi___4 == '0') and (uti != '0') # do not count this as an error, because an unchecked checkbox could be missing data.

    if err1 or err2 or err3:
        element_bad = True

    return element_bad

print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
#checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
#del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if child has had meningitis or encephalitis (menin_enceph=1) , then in IPSS, Other Child and Neonatal Risk Factors, major infection, meningitis should also be checked yes (infectma___3=1).
name = "meningitis_consistent"
description = 'In VIPS II, Interview, if child has had meningitis or encephalitis (menin_enceph=1) , then in IPSS, Other Child and Neonatal Risk Factors, major infection, meningitis should also be checked yes (infectma___3=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['menin_enceph'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    menin_enceph = row_1["menin_enceph"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None


    infectma___1, infectma___1_hidden = getEntryLR(record_id, event_2, instance_2, "infectma___1", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])
    infectma___3, infectma___3_hidden = getEntryLR(record_id, event_2, instance_2, "infectma___3", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    err1 = (menin_enceph == '1') and ((infectma___1 != '1') and (infectma___3 != '1'))
    err2 = (menin_enceph == '0') and ((infectma___1 != '0') or (infectma___3 != '0'))
#    err3 = ((infectma___1 == '0') and (infectma___3 == '0')) and (menin_enceph != '0') # do not count as error because an unchecked checkbox could be missing data.
    err4 = ((infectma___1 == '1') or (infectma___3 == '1')) and (menin_enceph != '1')

    if err1 or err2 or err4:
        element_bad = True

    return element_bad

#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if the child has had an ear infection in the past year (earinf=1), then in IPSS, Other Child and Neonatal Risk Factors, minor infection, otitis should also be checked yes (infectmi___2=1).
name = "ear_infection_consistent"
description = 'In VIPS II, Interview, if the child has had an ear infection in the past year (earinf=1), then in IPSS, Other Child and Neonatal Risk Factors, minor infection, otitis should also be checked yes (infectmi___2=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['earinf'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    earinf = row_1["earinf"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    infectmi___2, infectmi___2_hidden = getEntryLR(record_id, event_2, instance_2, "infectmi___2", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    err1 = (earinf == '1') and (infectmi___2 != '1')
    err2 = (earinf == '0') and (infectmi___2 != '0')
    err3 = (infectmi___2 == '1') and (earinf != '1')
#    err4 = (infectmi___2 == '0') and (earinf != '0') # do not count as an error because an unchecked checkbox could be missing data.

    if err1 or err2 or err3:
        element_bad = True

    return element_bad

print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
#checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
#del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: In VIPS II, Interview, if child has had any infectious illnesses in the 6 months prior to stroke? (ill_6m_strk=1), then in IPSS, Other Child and Neonatal Risk Factors, infection major or minor should also be yes (infect=1).
name = "infection_consistent"
description = 'In VIPS II, Interview, if child has had any infectious illnesses in the 6 months prior to stroke? (ill_6m_strk=1), then in IPSS, Other Child and Neonatal Risk Factors, infection major or minor should also be yes (infect=1).'
report_forms = True
inter_project = True
whole_row_check = False
check_invalid_entries = False
inter_record = False
inter_row = True
specify_fields = True
target_fields = ['ill_6m_strk'] # list target fields in the first project only; only links to these fields will be generated.

def rowConditions(row_index, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    return True

fieldConditions = None

def checkFunction(row_index_1, field_name_1, def_field_list, metadata_list, records_list, record_id_map_list, repeating_forms_events_list, form_repetition_map_list):
    element_bad = False
    
    # Get values from first project.
    row_1 = records_list[0][row_index_1]
    record_id = row_1[def_field_list[0]]
    ill_6m_strk = row_1["ill_6m_strk"]

    # Get values from second project.
    event_2 = "acute_arm_1"
    instance_2 = None

    infect, infect_hidden = getEntryLR(record_id, event_2, instance_2, "infect", records_list[1], record_id_map_list[1], metadata_list[1], form_repetition_map_list[1])

    if (ill_6m_strk == '1'):
        if (infect != '1'):
            element_bad = True

    return element_bad

print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
#checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
#del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
