from Check import Check # Class used to define what a check does and when it is performed

# Create list of checks (must be called 'checklist').
checklist = []


cohort1_normal = ['admityes', 'daent', 'gender', 'birmont', 'biryear', 'substud', 'sip_cohort', 'sipsenrolldate', 'strage', 'doe', 'dateest', 'stk_year', 'yesest', 'toe', 'timedes', 'wklife', 'perigrp', 'csvtgrp', 'tpagrp', 'childeth', 'motheth', 'fatheth', 'childrac', 'childot', 'childun', 'mothrac', 'moetoth', 'moetunk', 'fathrac', 'faetoth', 'faetunk', 'card', 'cardgrp', 'cardrole', 'carothsp', 'csurg', 'surgda', 'carcath', 'cath', 'cathd', 'cathdt', 'ecls', 'eclssp', 'eclssd', 'vad', 'vadsd', 'othpro', 'othprosp', 'othprod', 'art', 'artegrp', 'artrole', 'dissprov', 'moyaprov', 'fcaprov', 'fcat', 'fcaoth', 'vascprov', 'artoth', 'artspe', 'cervess', 'cervessp', 'larves', 'larvessp', 'smalves', 'smalvesp', 'anemia', 'sickle', 'sickrole', 'sickwm', 'genetsy', 'genetsyr', 'genetsys', 'prothrom', 'prothrole', 'prothrosp', 'diabsp', 'infect', 'infectr', 'infectt', 'infectma', 'minfneo', 'torchsp1', 'infectmi', 'infmisp', 'migraine', 'heatrau', 'heatraur', 'systhro', 'systhror', 'systhrom', 'thromsp', 'ilnes', 'ilnesr', 'inflam', 'malig', 'othchr', 'othill', 'ilnes_acute', 'dehyd', 'anoxia', 'drugtox', 'acidos', 'acilloth', 'othill_acute', 'intproc', 'intprocr', 'othsurg', 'endoinst', 'othsurgt', 'endinstt', 'othrisk', 'othrissp', 'comorbi', 'hstroke', 'hheaatt', 'relhstro', 'relha', 'indet', 'mulges', 'mulgessp', 'delmode', 'cemerg', 'cemersp', 'memrup', 'matfev', 'chrioamn', 'matage', 'premie', 'bweight', 'apgar1', 'apgar5', 'apgar10', 'cpintwel', 'neudef', 'neudefs', 'abconc', 'typeconc', 'decencep', 'mentst', 'hemi', 'hemisp', 'ataxia', 'visdef', 'visdefsp', 'speedef', 'adfeve', 'headach', 'neudefsp', 'neudefoth', 'neoencep', 'defleng', 'pednihy', 'pednihsc', 'pednihs', 'seizur', 'seizdate', 'seizgrp',                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'acutsta', 'neustat', 'othdeat', 'neurdef', 'neurdeft', 'neudeoth', 'discloc', 'dislocot', 'psomdate', 'psomr', 'psoml', 'psomlae', 'psomlar', 'psomcb', 'psomsens', 'senssp', 'psomcog', 'psomscr', 'assedat', 'strreco', 'rrq1a', 'rghsid', 'lefsid', 'verbal', 'underst', 'think', 'ppsomsc', 'rrqq2', 'rrqq3', 'parec', 'othclot_sp', 'precdat', 'pctmri', 'pwhtest', 'shnewstr', 'newsymp', 'nwsymoth', 'symlast', 'numepi', 'treatstr', 'othtrebe', 'phead', 'pseiz', 'seimed', 'dfseiz', 'seimed2', 'healprob', 'heaprosp', 'mednow', 'comedsp', 'prehab', 'rehoth', 'pdeath', 'pdeathm', 'deacaus', 'outcome_fupdate', 'funeurst', 'funeudef', 'fudeaoth', 'fneudeft', 'funedeot', 'furehab', 'psom_notdone', 'fuionset', 'fpsomr', 'fpsoml', 'fpsomlae', 'fpsomlar', 'fpsomcb', 'psomsen', 'othsens', 'fpsomco', 'totpsom']
cohort1_groups = [['chais___1', 'chcsvt___1', 'neoais___1', 'neocsvt___1'], ['chd___1', 'ahd___1', 'infcard___1', 'ipfo___1', 'cardoth___1'], ['focalmoa___1', 'generaa___1', 'multiseiza___1', 'prolseiza___1', 'electroga___1']]

cohort2_normal = ['admityes', 'daent', 'gender', 'birmont', 'biryear', 'substud', 'sip_cohort', 'sipsenrolldate', 'strage', 'doe', 'dateest', 'stk_year', 'yesest', 'toe', 'timedes', 'wklife', 'perigrp', 'csvtgrp', 'tpagrp', 'childeth', 'motheth', 'fatheth', 'childrac', 'childot', 'childun', 'mothrac', 'moetoth', 'moetunk', 'fathrac', 'faetoth', 'faetunk', 'card', 'cardgrp', 'cardrole', 'carothsp', 'csurg', 'surgda', 'carcath', 'cath', 'cathd', 'cathdt', 'ecls', 'eclssp', 'eclssd', 'vad', 'vadsd', 'othpro', 'othprosp', 'othprod', 'art', 'artegrp', 'artrole', 'dissprov', 'moyaprov', 'fcaprov', 'fcat', 'fcaoth', 'vascprov', 'artoth', 'artspe', 'cervess', 'cervessp', 'larves', 'larvessp', 'smalves', 'smalvesp', 'anemia', 'sickle', 'sickrole', 'sickwm', 'genetsy', 'genetsyr', 'genetsys', 'prothrom', 'prothrole', 'prothrosp', 'diabsp', 'infect', 'infectr', 'infectt', 'infectma', 'minfneo', 'torchsp1', 'infectmi', 'infmisp', 'migraine', 'heatrau', 'heatraur', 'systhro', 'systhror', 'systhrom', 'thromsp', 'ilnes', 'ilnesr', 'inflam', 'malig', 'othchr', 'othill', 'ilnes_acute', 'dehyd', 'anoxia', 'drugtox', 'acidos', 'acilloth', 'othill_acute', 'intproc', 'intprocr', 'othsurg', 'endoinst', 'othsurgt', 'endinstt', 'othrisk', 'othrissp', 'comorbi', 'hstroke', 'hheaatt', 'relhstro', 'relha', 'indet', 'mulges', 'mulgessp', 'delmode', 'cemerg', 'cemersp', 'memrup', 'matfev', 'chrioamn', 'matage', 'premie', 'bweight', 'apgar1', 'apgar5', 'apgar10', 'cpintwel', 'neudef', 'neudefs', 'abconc', 'typeconc', 'decencep', 'mentst', 'hemi', 'hemisp', 'ataxia', 'visdef', 'visdefsp', 'speedef', 'adfeve', 'headach', 'neudefsp', 'neudefoth', 'neoencep', 'defleng', 'pednihy', 'pednihsc', 'pednihs', 'seizur', 'seizdate', 'seizgrp', 'height', 'weight', 'bpdate', 'bpsys', 'bpdias', 'wbc1', 'rbc1', 'hgb1', 'hct1', 'mcv1', 'plate1', 'rdw1', 'echo', 'echores', 'echoabns', 'sendimag', 'scanty', 'scandat', 'scantim', 'inffind', 'reasimag', 'eegabn', 'infnum', 'infsize', 'artter', 'antart', 'postart', 'infloc', 'infraloc', 'supraloc', 'inflat', 'vasimg', 'vasdate', 'vascim', 'mratype', 'ctatype', 'vascfin', 'vasfiabn', 'vasfitoh', 'vaslate', 'vesseff', 'pstrtrea', 'pstranti', 'antitoh', 'asttpa', 'tpatype', 'tparevas', 'revassp', 'revasoth', 'mechdev', 'devused', 'devoth', 'devproti', 'devangst', 'devangfi', 'recanres', 'tpatime', 'tpatime6', 'tpablee', 'tpablety', 'tecass', 'astrtrea', 'astranti', 'rantipla', 'anticosp', 'ranticoa', 'rectroth', 'treblee', 'treblety', 'antplatt', 'antcoatt', 'trecass', 'othtreti', 'ster', 'ster_spec', 'iv_dose', 'othdose_unit', 'mgkgday', 'mgday', 'iv_date', 'iv_dur', 'ivdur_spec', 'ster_ongoing', 'oral_dose', 'oral_date', 'oral_dur', 'oral_ongo', 'acyclo', 'acyc_admi', 'othtre', 'othintsp', 'anticonv', 'antplcon', 'antcocon', 'antsicon', 'raistia', 'rectype', 'rectime', 'rectrea1', 'rectrea', 'antiplm', 'anticom', 'otherm', 'hemthrom', 'propsym', 'heantit', 'newcsvt', 'prehem', 'newhemo', 'newble', 'rsevblee', 'rbleelo', 'rbleloot', 'hemsymp', 'hemtime', 'hemblee', 'hemecas', 'acutsta', 'neustat', 'othdeat', 'neurdef', 'neurdeft', 'neudeoth', 'discloc', 'dislocot', 'psomdate', 'psomr', 'psoml', 'psomlae', 'psomlar', 'psomcb', 'psomsens', 'senssp', 'psomcog', 'psomscr', 'assedat', 'strreco', 'rrq1a', 'rghsid', 'lefsid', 'verbal', 'underst', 'think', 'ppsomsc', 'rrqq2', 'rrqq3', 'parec', 'othclot_sp', 'precdat', 'pctmri', 'pwhtest', 'shnewstr', 'newsymp', 'nwsymoth', 'symlast', 'numepi', 'treatstr', 'othtrebe', 'phead', 'pseiz', 'seimed', 'dfseiz', 'seimed2', 'healprob', 'heaprosp', 'mednow', 'comedsp', 'prehab', 'rehoth', 'pdeath', 'pdeathm', 'deacaus', 'outcome_fupdate', 'funeurst', 'funeudef', 'fudeaoth', 'fneudeft', 'funedeot', 'furehab', 'psom_notdone', 'fuionset', 'fpsomr', 'fpsoml', 'fpsomlae', 'fpsomlar', 'fpsomcb', 'psomsen', 'othsens', 'fpsomco', 'totpsom']
cohort2_groups = [['chais___1', 'chcsvt___1', 'neoais___1', 'neocsvt___1'], ['chd___1', 'ahd___1', 'infcard___1', 'ipfo___1', 'cardoth___1'], ['focalmoa___1', 'generaa___1', 'multiseiza___1', 'prolseiza___1', 'electroga___1'], ['etb___1', 'hemic___1', 'othns___1', 'hypo___1', 'othert___1']]
 

# Define check by specifying each of the parameters in the 'Check' class.

#### Check: SIPS II Cohort I checks
name = "cohort1_ipss_fields"
description = "Missing fields in IPSS for patients in SIPS II cohort I"
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

    for group in cohort1_groups:
        if field_name in group: # the grouped variables have their full name including the checkbox option.
            return True

    return False # if not in either of the lists checked above

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    # At this point, the field is already known to be in either the list of normal fields, or the list of grouped fields
    field = metadata[field_name]
    row = records[row_index]
    if field_name.split('___')[0] in cohort1_normal: # if in the normal field list    
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
    
    else: # if in the list of grouped fields (which are always single-option checkbox fields)
        for group in cohort1_groups:
            if field_name in group: # the group of variables has been identified. Check if any of them are complete.
                element_bad = True
                for option in group:
                    if (row[option] == '1'):
                        element_bad = False
                        break
                break
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction


#### Check: SIPS II Cohort II checks
name = "cohort2_ipss_fields"
description = "Missing fields in IPSS for patients in SIPS II cohort II"
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

    for group in cohort2_groups:
        if field_name in group: # the grouped variables have their full name including the checkbox option.
            return True

    return False # if not in either of the lists checked above

# Define the function which performs the actual check.
#def checkFunction(row_index, field_name, def_field, metadata, records, form_repetition_map):
def checkFunction(row_index, field_name, def_field, metadata, records, record_id_map, repeating_forms_events, form_repetition_map):
    # At this point, the field is already known to be in either the list of normal fields, or the list of grouped fields
    field = metadata[field_name]
    row = records[row_index]
    if field_name.split('___')[0] in cohort2_normal: # if in the normal field list
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
    
    else: # if in the list of grouped fields (which are always single-option checkbox fields)
        for group in cohort2_groups:
            if field_name in group: # the group of variables has been identified. Check if any of them are complete.
                element_bad = True
                for option in group:
                    if (row[option] == '1'):
                        element_bad = False
                        break
                break
    return element_bad

# Add check instance to list of default checks.            
#print "************************SKIPPING CHECK '"+name+"' FOR TEST************************"
checklist.append(Check(name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction))
del name, description, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction
